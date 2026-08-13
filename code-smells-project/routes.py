from flask import Blueprint

import controllers


api = Blueprint("api", __name__)

api.add_url_rule("/", "index", controllers.index, methods=["GET"])
api.add_url_rule("/produtos", "listar_produtos", controllers.listar_produtos, methods=["GET"])
api.add_url_rule("/produtos/busca", "buscar_produtos", controllers.buscar_produtos, methods=["GET"])
api.add_url_rule("/produtos/<int:id>", "buscar_produto", controllers.buscar_produto, methods=["GET"])
api.add_url_rule("/produtos", "criar_produto", controllers.criar_produto, methods=["POST"])
api.add_url_rule("/produtos/<int:id>", "atualizar_produto", controllers.atualizar_produto, methods=["PUT"])
api.add_url_rule("/produtos/<int:id>", "deletar_produto", controllers.deletar_produto, methods=["DELETE"])
api.add_url_rule("/usuarios", "listar_usuarios", controllers.listar_usuarios, methods=["GET"])
api.add_url_rule("/usuarios/<int:id>", "buscar_usuario", controllers.buscar_usuario, methods=["GET"])
api.add_url_rule("/usuarios", "criar_usuario", controllers.criar_usuario, methods=["POST"])
api.add_url_rule("/login", "login", controllers.login, methods=["POST"])
api.add_url_rule("/logout", "logout", controllers.logout, methods=["POST"])
api.add_url_rule("/pedidos", "criar_pedido", controllers.criar_pedido, methods=["POST"])
api.add_url_rule("/pedidos", "listar_todos_pedidos", controllers.listar_todos_pedidos, methods=["GET"])
api.add_url_rule(
    "/pedidos/usuario/<int:usuario_id>",
    "listar_pedidos_usuario",
    controllers.listar_pedidos_usuario,
    methods=["GET"],
)
api.add_url_rule(
    "/pedidos/<int:pedido_id>/status",
    "atualizar_status_pedido",
    controllers.atualizar_status_pedido,
    methods=["PUT"],
)
api.add_url_rule("/relatorios/vendas", "relatorio_vendas", controllers.relatorio_vendas, methods=["GET"])
api.add_url_rule("/health", "health_check", controllers.health_check, methods=["GET"])
api.add_url_rule("/admin/reset-db", "reset_database", controllers.reset_database, methods=["POST"])
api.add_url_rule("/admin/query", "executar_query", controllers.executar_query, methods=["POST"])
