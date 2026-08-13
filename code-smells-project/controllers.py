from flask import current_app, jsonify, request, session

import services
from auth import login_user, require_admin, require_login, require_self_or_admin
from database import get_db, transaction
from errors import AppError, NotFoundError
from validation import (
    parse_login,
    parse_optional_float,
    parse_order,
    parse_pagination,
    parse_product,
    parse_status,
    parse_user,
    require_json,
)


def _success(data=None, *, status=200, message=None, extra=None):
    payload = {"sucesso": True}
    if data is not None:
        payload["dados"] = data
    if message is not None:
        payload["mensagem"] = message
    if extra:
        payload.update(extra)
    return jsonify(payload), status


def index():
    return jsonify(
        {
            "mensagem": "Bem-vindo à API da Loja",
            "versao": "1.0.0",
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        }
    )


def listar_produtos():
    limit, offset = parse_pagination(request)
    products = services.product_repository().list(limit, offset)
    return _success([product.to_dict() for product in products])


def buscar_produto(id):
    product = services.product_repository().get(id)
    if product is None:
        raise NotFoundError("Produto não encontrado")
    return _success(product.to_dict())


@require_admin
def criar_produto():
    product = parse_product(require_json(request))
    product_id = services.product_repository().create(product)
    return _success(
        {"id": product_id}, status=201, message="Produto criado"
    )


@require_admin
def atualizar_produto(id):
    if services.product_repository().get(id) is None:
        raise NotFoundError("Produto não encontrado")
    services.product_repository().update(id, parse_product(require_json(request)))
    return _success(message="Produto atualizado")


@require_admin
def deletar_produto(id):
    if not services.product_repository().delete(id):
        raise NotFoundError("Produto não encontrado")
    return _success(message="Produto deletado")


def buscar_produtos():
    minimum_price = parse_optional_float(request.args.get("preco_min"), "preco_min")
    maximum_price = parse_optional_float(request.args.get("preco_max"), "preco_max")
    limit, offset = parse_pagination(request)
    results = services.product_repository().search(
        request.args.get("q", ""),
        request.args.get("categoria"),
        minimum_price,
        maximum_price,
        limit,
        offset,
    )
    data = [product.to_dict() for product in results]
    return _success(data, extra={"total": len(data)})


@require_admin
def listar_usuarios():
    limit, offset = parse_pagination(request)
    users = services.user_repository().list(limit, offset)
    return _success([user.to_dict() for user in users])


@require_login
def buscar_usuario(id):
    require_self_or_admin(id)
    user = services.user_repository().get(id)
    if user is None:
        raise NotFoundError("Usuário não encontrado")
    return _success(user.to_dict())


def criar_usuario():
    user_id = services.create_user(parse_user(require_json(request)))
    return _success({"id": user_id}, status=201)


def login():
    email, password = parse_login(require_json(request))
    user = services.authenticate(email, password)
    login_user(user)
    return _success(user, message="Login OK")


def logout():
    session.clear()
    return _success(message="Logout realizado")


@require_login
def criar_pedido():
    user_id, items = parse_order(require_json(request))
    require_self_or_admin(user_id)
    result = services.create_order(user_id, items)
    current_app.logger.info("Pedido criado", extra={"pedido_id": result["pedido_id"]})
    return _success(result, status=201, message="Pedido criado com sucesso")


@require_login
def listar_pedidos_usuario(usuario_id):
    require_self_or_admin(usuario_id)
    limit, offset = parse_pagination(request)
    orders = services.order_repository().list(limit, offset, usuario_id)
    return _success([order.to_dict() for order in orders])


@require_admin
def listar_todos_pedidos():
    limit, offset = parse_pagination(request)
    orders = services.order_repository().list(limit, offset)
    return _success([order.to_dict() for order in orders])


@require_admin
def atualizar_status_pedido(pedido_id):
    status = parse_status(require_json(request))
    services.update_order_status(pedido_id, status)
    return _success(message="Status atualizado")


@require_admin
def relatorio_vendas():
    return _success(services.sales_report())


def health_check():
    database = get_db()
    counts = {
        "produtos": database.execute("SELECT COUNT(*) FROM produtos").fetchone()[0],
        "usuarios": database.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0],
        "pedidos": database.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0],
    }
    return jsonify(
        {
            "status": "ok",
            "database": "connected",
            "counts": counts,
            "versao": "1.0.0",
            "ambiente": current_app.config["ENVIRONMENT"],
        }
    )


@require_admin
def reset_database():
    with transaction() as database:
        database.execute("DELETE FROM itens_pedido")
        database.execute("DELETE FROM pedidos")
        database.execute("DELETE FROM produtos")
        database.execute("DELETE FROM usuarios")
    return _success(message="Banco de dados resetado")


@require_admin
def executar_query():
    raise AppError(
        "Execução arbitrária de SQL foi desativada por segurança", status_code=410
    )
