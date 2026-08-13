from datetime import datetime, timezone

from flask import Flask
from flask_cors import CORS

from config import Config
from database import db
from errors import register_error_handlers
from routes.report_routes import report_bp
from routes.task_routes import task_bp
from routes.user_routes import user_bp
from services.auth_service import AuthService


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    if not app.config.get('SECRET_KEY'):
        raise RuntimeError('SECRET_KEY is required')

    CORS(app)
    db.init_app(app)
    app.extensions['auth_service'] = AuthService(
        app.config['SECRET_KEY'],
        app.config.get('TOKEN_MAX_AGE_SECONDS', 3600),
    )
    register_error_handlers(app)
    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)

    @app.get('/health')
    def health():
        return {'status': 'ok', 'timestamp': str(datetime.now(timezone.utc))}

    @app.get('/')
    def index():
        return {'message': 'Task Manager API', 'version': '1.0'}

    return app


app = create_app()


if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)
