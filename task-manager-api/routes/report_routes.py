from flask import Blueprint, jsonify, request

from auth import require_roles
from controllers.category_controller import CategoryController
from controllers.report_controller import ReportController


report_bp = Blueprint('reports', __name__)
report_controller = ReportController()
category_controller = CategoryController()


@report_bp.get('/reports/summary')
@require_roles('admin', 'manager')
def summary_report():
    return jsonify(report_controller.summary_report()), 200


@report_bp.get('/reports/user/<int:user_id>')
@require_roles('admin', 'manager')
def user_report(user_id):
    return jsonify(report_controller.user_report(user_id)), 200


@report_bp.get('/categories')
@require_roles('admin', 'manager')
def get_categories():
    return jsonify(category_controller.list_categories()), 200


@report_bp.post('/categories')
@require_roles('admin')
def create_category():
    return jsonify(category_controller.create_category(request.get_json(silent=True))), 201


@report_bp.put('/categories/<int:cat_id>')
@require_roles('admin')
def update_category(cat_id):
    return jsonify(category_controller.update_category(cat_id, request.get_json(silent=True))), 200


@report_bp.delete('/categories/<int:cat_id>')
@require_roles('admin')
def delete_category(cat_id):
    return jsonify(category_controller.delete_category(cat_id)), 200
