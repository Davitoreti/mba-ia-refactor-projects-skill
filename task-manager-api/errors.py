from dataclasses import dataclass

from flask import jsonify


@dataclass
class AppError(Exception):
    message: str
    status_code: int = 400


class NotFoundError(AppError):
    def __init__(self, message):
        super().__init__(message, 404)


class ConflictError(AppError):
    def __init__(self, message):
        super().__init__(message, 409)


class AuthenticationError(AppError):
    def __init__(self, message="Autenticação necessária"):
        super().__init__(message, 401)


class AuthorizationError(AppError):
    def __init__(self, message="Acesso negado"):
        super().__init__(message, 403)


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({"error": error.message}), error.status_code

    @app.errorhandler(404)
    def handle_route_not_found(_error):
        return jsonify({"error": "Recurso não encontrado"}), 404

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Erro inesperado", exc_info=error)
        return jsonify({"error": "Erro interno"}), 500
