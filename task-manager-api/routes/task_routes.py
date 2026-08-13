from flask import Blueprint, jsonify, request

from auth import require_auth
from controllers.task_controller import TaskController
from utils.validators import parse_integer


task_bp = Blueprint('tasks', __name__)
controller = TaskController()


@task_bp.get('/tasks')
@require_auth
def get_tasks():
    limit = request.args.get('limit')
    parsed_limit = parse_integer(limit, 'Limite inválido', 1, 100) if limit else None
    offset = parse_integer(request.args.get('offset', 0), 'Offset inválido', 0)
    return jsonify(controller.list_tasks(parsed_limit, offset)), 200


@task_bp.get('/tasks/<int:task_id>')
@require_auth
def get_task(task_id):
    return jsonify(controller.get_task(task_id)), 200


@task_bp.post('/tasks')
@require_auth
def create_task():
    return jsonify(controller.create_task(request.get_json(silent=True))), 201


@task_bp.put('/tasks/<int:task_id>')
@require_auth
def update_task(task_id):
    return jsonify(controller.update_task(task_id, request.get_json(silent=True))), 200


@task_bp.delete('/tasks/<int:task_id>')
@require_auth
def delete_task(task_id):
    return jsonify(controller.delete_task(task_id)), 200


@task_bp.get('/tasks/search')
@require_auth
def search_tasks():
    return jsonify(controller.search_tasks(request.args)), 200


@task_bp.get('/tasks/stats')
@require_auth
def task_stats():
    return jsonify(controller.task_stats()), 200
