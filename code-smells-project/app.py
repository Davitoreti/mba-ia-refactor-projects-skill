import logging

from flask import Flask, jsonify

from config import Settings
from database import init_db, register_database
from errors import AppError
from routes import api


def create_app(test_config=None):
    settings = Settings.from_env()
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=settings.secret_key,
        DATABASE_PATH=settings.database_path,
        DEBUG=settings.debug,
        ENVIRONMENT=settings.environment,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=settings.environment == "production",
    )
    if test_config:
        app.config.update(test_config)

    register_database(app)
    app.register_blueprint(api)
    register_error_handlers(app)
    return app


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({"erro": error.public_message, "sucesso": False}), error.status_code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Erro inesperado", exc_info=error)
        return jsonify({"erro": "Erro interno"}), 500


app = create_app()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    with app.app_context():
        init_db()
    app.run(host="127.0.0.1", port=5000, debug=app.config["DEBUG"])
