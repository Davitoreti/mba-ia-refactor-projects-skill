import sqlite3

from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db, transaction
from errors import AuthenticationError, ConflictError, NotFoundError, ValidationError
from repositories import OrderRepository, ProductRepository, UserRepository


DISCOUNT_TIERS = ((10000, 0.10), (5000, 0.05), (1000, 0.02))


def product_repository():
    return ProductRepository(get_db())


def user_repository():
    return UserRepository(get_db())


def order_repository():
    return OrderRepository(get_db())


def create_user(user):
    try:
        return user_repository().create(
            user["nome"], user["email"], generate_password_hash(user["senha"])
        )
    except sqlite3.IntegrityError as error:
        raise ConflictError("Email já cadastrado") from error


def authenticate(email, password):
    row = user_repository().find_for_login(email)
    if row is None or not check_password_hash(row["senha"], password):
        raise AuthenticationError("Email ou senha inválidos")
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
    }


def create_order(user_id, items):
    if user_repository().get(user_id) is None:
        raise ValidationError("Usuário não encontrado")

    with transaction() as database:
        repository = OrderRepository(database)
        prepared_items = []
        total = 0
        for item in items:
            product = repository.product_for_update(item["produto_id"])
            if product is None:
                raise ValidationError(f"Produto {item['produto_id']} não encontrado")
            if product["estoque"] < item["quantidade"]:
                raise ValidationError(f"Estoque insuficiente para {product['nome']}")
            total += product["preco"] * item["quantidade"]
            prepared_items.append((item, product["preco"]))

        order_id = repository.create_order(user_id, total)
        for item, unit_price in prepared_items:
            repository.create_item(
                order_id, item["produto_id"], item["quantidade"], unit_price
            )
            if not repository.decrease_stock(item["produto_id"], item["quantidade"]):
                raise ConflictError("Estoque alterado durante a criação do pedido")

    return {"pedido_id": order_id, "total": total}


def update_order_status(order_id, status):
    if not order_repository().update_status(order_id, status):
        raise NotFoundError("Pedido não encontrado")


def sales_report():
    row = order_repository().sales_report()
    gross = row["faturamento"]
    discount = next(
        (gross * rate for threshold, rate in DISCOUNT_TIERS if gross > threshold), 0
    )
    total_orders = row["total_pedidos"]
    return {
        "total_pedidos": total_orders,
        "faturamento_bruto": round(gross, 2),
        "desconto_aplicavel": round(discount, 2),
        "faturamento_liquido": round(gross - discount, 2),
        "pedidos_pendentes": row["pendentes"],
        "pedidos_aprovados": row["aprovados"],
        "pedidos_cancelados": row["cancelados"],
        "ticket_medio": round(gross / total_orders, 2) if total_orders else 0,
    }
