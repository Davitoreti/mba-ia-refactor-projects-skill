from flask import Blueprint, current_app, jsonify, request

from auth import require_auth, require_roles
from controllers.user_controller import UserController


user_bp = Blueprint('users', __name__)


def controller():
    return UserController(current_app.extensions['auth_service'])


@user_bp.get('/users')
@require_roles('admin', 'manager')
def get_users():
    return jsonify(controller().list_users()), 200


@user_bp.get('/users/<int:user_id>')
@require_auth
def get_user(user_id):
    return jsonify(controller().get_user(user_id)), 200


@user_bp.post('/users')
@require_roles('admin')
def create_user():
    return jsonify(controller().create_user(request.get_json(silent=True))), 201


@user_bp.put('/users/<int:user_id>')
@require_roles('admin')
def update_user(user_id):
    return jsonify(controller().update_user(user_id, request.get_json(silent=True))), 200


@user_bp.delete('/users/<int:user_id>')
@require_roles('admin')
def delete_user(user_id):
    return jsonify(controller().delete_user(user_id)), 200


@user_bp.get('/users/<int:user_id>/tasks')
@require_auth
def get_user_tasks(user_id):
    return jsonify(controller().get_user_tasks(user_id)), 200


@user_bp.post('/login')
def login():
    return jsonify(controller().login(request.get_json(silent=True))), 200
