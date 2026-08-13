from errors import ValidationError


VALID_CATEGORIES = {
    "informatica",
    "moveis",
    "vestuario",
    "geral",
    "eletronicos",
    "livros",
}
VALID_ORDER_STATUSES = {
    "pendente",
    "aprovado",
    "enviado",
    "entregue",
    "cancelado",
}


def require_json(request):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValidationError("Dados inválidos")
    return data


def require_string(data, field, *, label=None, min_length=1, max_length=None):
    label = label or field.capitalize()
    value = data.get(field)
    if not isinstance(value, str) or len(value.strip()) < min_length:
        raise ValidationError(f"{label} é obrigatório")
    value = value.strip()
    if max_length is not None and len(value) > max_length:
        raise ValidationError(f"{label} muito longo")
    return value


def require_number(data, field, *, label=None, minimum=None, integer=False):
    label = label or field.capitalize()
    value = data.get(field)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"{label} deve ser numérico")
    if integer and not isinstance(value, int):
        raise ValidationError(f"{label} deve ser inteiro")
    if minimum is not None and value < minimum:
        raise ValidationError(f"{label} não pode ser menor que {minimum}")
    return value


def parse_product(data):
    name = require_string(data, "nome", label="Nome", min_length=2, max_length=200)
    price = require_number(data, "preco", label="Preço", minimum=0)
    stock = require_number(data, "estoque", label="Estoque", minimum=0, integer=True)
    description = data.get("descricao", "")
    category = data.get("categoria", "geral")

    if not isinstance(description, str):
        raise ValidationError("Descrição deve ser texto")
    if category not in VALID_CATEGORIES:
        raise ValidationError(f"Categoria inválida. Válidas: {sorted(VALID_CATEGORIES)}")

    return {
        "nome": name,
        "descricao": description,
        "preco": price,
        "estoque": stock,
        "categoria": category,
    }


def parse_user(data):
    name = require_string(data, "nome", label="Nome", max_length=200)
    email = require_string(data, "email", label="Email", max_length=254).lower()
    password = require_string(data, "senha", label="Senha", min_length=6, max_length=256)
    if "@" not in email or email.startswith("@") or email.endswith("@"):
        raise ValidationError("Email inválido")
    return {"nome": name, "email": email, "senha": password}


def parse_login(data):
    email = require_string(data, "email", label="Email", max_length=254).lower()
    password = require_string(data, "senha", label="Senha", max_length=256)
    return email, password


def parse_order(data):
    user_id = require_number(data, "usuario_id", label="Usuario ID", minimum=1, integer=True)
    items = data.get("itens")
    if not isinstance(items, list) or not items:
        raise ValidationError("Pedido deve ter pelo menos 1 item")

    parsed_items = []
    for item in items:
        if not isinstance(item, dict):
            raise ValidationError("Item do pedido inválido")
        parsed_items.append(
            {
                "produto_id": require_number(
                    item, "produto_id", label="Produto ID", minimum=1, integer=True
                ),
                "quantidade": require_number(
                    item, "quantidade", label="Quantidade", minimum=1, integer=True
                ),
            }
        )
    return user_id, parsed_items


def parse_status(data):
    status = data.get("status")
    if status not in VALID_ORDER_STATUSES:
        raise ValidationError("Status inválido")
    return status


def parse_optional_float(value, field):
    if value in (None, ""):
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError) as error:
        raise ValidationError(f"{field} deve ser numérico") from error
    if parsed < 0:
        raise ValidationError(f"{field} não pode ser negativo")
    return parsed


def parse_pagination(request, *, default=100, maximum=100):
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", default))
    except (TypeError, ValueError) as error:
        raise ValidationError("Paginação inválida") from error
    if page < 1 or per_page < 1 or per_page > maximum:
        raise ValidationError(f"Paginação deve usar page >= 1 e per_page entre 1 e {maximum}")
    return per_page, (page - 1) * per_page
