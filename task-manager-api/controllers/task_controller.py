from datetime import datetime, timezone

from errors import NotFoundError
from models.task import Task
from repositories.category_repository import CategoryRepository
from repositories.task_repository import TaskRepository
from repositories.user_repository import UserRepository
from services.persistence_service import commit_or_raise
from utils.validators import parse_integer, validate_task_fields


class TaskController:
    @staticmethod
    def _detail(task, include_names=False):
        data = task.to_dict()
        data['overdue'] = task.is_overdue()
        if include_names:
            data['user_name'] = task.user.name if task.user else None
            data['category_name'] = task.category.name if task.category else None
        return data

    @classmethod
    def list_tasks(cls, limit=None, offset=0):
        return [cls._detail(task, include_names=True) for task in TaskRepository.list(limit, offset)]

    @classmethod
    def get_task(cls, task_id):
        task = TaskRepository.get(task_id)
        if not task:
            raise NotFoundError('Task não encontrada')
        return cls._detail(task)

    @staticmethod
    def _validate_references(fields):
        if fields.get('user_id') and not UserRepository.get(fields['user_id']):
            raise NotFoundError('Usuário não encontrado')
        if fields.get('category_id') and not CategoryRepository.get(fields['category_id']):
            raise NotFoundError('Categoria não encontrada')

    @classmethod
    def create_task(cls, data):
        fields = validate_task_fields(data, creating=True)
        fields.setdefault('description', '')
        fields.setdefault('status', 'pending')
        fields.setdefault('priority', 3)
        cls._validate_references(fields)
        task = Task(**fields)
        TaskRepository.add(task)
        commit_or_raise('Erro ao criar task')
        return task.to_dict()

    @classmethod
    def update_task(cls, task_id, data):
        task = TaskRepository.get(task_id)
        if not task:
            raise NotFoundError('Task não encontrada')
        fields = validate_task_fields(data)
        cls._validate_references(fields)
        for field, value in fields.items():
            setattr(task, field, value)
        task.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        commit_or_raise('Erro ao atualizar')
        return task.to_dict()

    @staticmethod
    def delete_task(task_id):
        task = TaskRepository.get(task_id)
        if not task:
            raise NotFoundError('Task não encontrada')
        TaskRepository.delete(task)
        commit_or_raise('Erro ao deletar')
        return {'message': 'Task deletada com sucesso'}

    @staticmethod
    def search_tasks(args):
        priority = parse_integer(args.get('priority'), 'Prioridade inválida', 1, 5) if args.get('priority') else None
        user_id = parse_integer(args.get('user_id'), 'Usuário inválido', 1) if args.get('user_id') else None
        limit = parse_integer(args.get('limit', 100), 'Limite inválido', 1, 100)
        tasks = TaskRepository.search(args.get('q', ''), args.get('status', ''), priority, user_id, limit)
        return [task.to_dict() for task in tasks]

    @staticmethod
    def task_stats():
        counts = TaskRepository.status_counts()
        all_tasks = TaskRepository.list()
        total = sum(counts.values())
        done = counts.get('done', 0)
        return {
            'total': total,
            'pending': counts.get('pending', 0),
            'in_progress': counts.get('in_progress', 0),
            'done': done,
            'cancelled': counts.get('cancelled', 0),
            'overdue': sum(task.is_overdue() for task in all_tasks),
            'completion_rate': round((done / total) * 100, 2) if total else 0,
        }
