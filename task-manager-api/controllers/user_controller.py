from sqlalchemy import delete

from database import db
from errors import AppError, ConflictError, NotFoundError
from models.task import Task
from models.user import User
from repositories.task_repository import TaskRepository
from repositories.user_repository import UserRepository
from services.persistence_service import commit_or_raise
from utils.validators import VALID_ROLES, require_json, require_string, validate_email


class UserController:
    def __init__(self, auth_service):
        self.auth_service = auth_service

    @staticmethod
    def list_users():
        result = []
        for user, task_count in UserRepository.list_with_task_counts():
            data = user.to_dict()
            data['task_count'] = task_count
            result.append(data)
        return result

    @staticmethod
    def get_user(user_id):
        user = UserRepository.get(user_id)
        if not user:
            raise NotFoundError('Usuário não encontrado')
        data = user.to_dict()
        data['tasks'] = [task.to_dict() for task in TaskRepository.list_by_user(user_id)]
        return data

    @staticmethod
    def create_user(data):
        require_json(data)
        name = require_string(data, 'name', 'Nome é obrigatório')
        email = validate_email(require_string(data, 'email', 'Email é obrigatório'))
        password = require_string(data, 'password', 'Senha é obrigatória')
        if len(password) < 8:
            raise AppError('Senha deve ter no mínimo 8 caracteres')
        role = data.get('role', 'user')
        if role not in VALID_ROLES:
            raise AppError('Role inválido')
        if UserRepository.get_by_email(email):
            raise ConflictError('Email já cadastrado')

        user = User(name=name, email=email, role=role)
        user.set_password(password)
        UserRepository.add(user)
        commit_or_raise('Erro ao criar usuário')
        return user.to_dict()

    @staticmethod
    def update_user(user_id, data):
        user = UserRepository.get(user_id)
        if not user:
            raise NotFoundError('Usuário não encontrado')
        require_json(data)
        if 'name' in data:
            user.name = require_string(data, 'name', 'Nome é obrigatório')
        if 'email' in data:
            email = validate_email(data['email'])
            existing = UserRepository.get_by_email(email)
            if existing and existing.id != user_id:
                raise ConflictError('Email já cadastrado')
            user.email = email
        if 'password' in data:
            password = require_string(data, 'password', 'Senha muito curta')
            if len(password) < 8:
                raise AppError('Senha muito curta')
            user.set_password(password)
        if 'role' in data:
            if data['role'] not in VALID_ROLES:
                raise AppError('Role inválido')
            user.role = data['role']
        if 'active' in data:
            if not isinstance(data['active'], bool):
                raise AppError('Dados inválidos')
            user.active = data['active']
        commit_or_raise('Erro ao atualizar')
        return user.to_dict()

    @staticmethod
    def delete_user(user_id):
        user = UserRepository.get(user_id)
        if not user:
            raise NotFoundError('Usuário não encontrado')
        db.session.execute(delete(Task).where(Task.user_id == user_id))
        UserRepository.delete(user)
        commit_or_raise('Erro ao deletar')
        return {'message': 'Usuário deletado com sucesso'}

    @staticmethod
    def get_user_tasks(user_id):
        if not UserRepository.get(user_id):
            raise NotFoundError('Usuário não encontrado')
        result = []
        for task in TaskRepository.list_by_user(user_id):
            data = {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'priority': task.priority,
                'created_at': str(task.created_at),
                'due_date': str(task.due_date) if task.due_date else None,
                'overdue': task.is_overdue(),
            }
            result.append(data)
        return result

    def login(self, data):
        require_json(data)
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            raise AppError('Email e senha são obrigatórios')
        user = UserRepository.get_by_email(email)
        if not user or not user.check_password(password):
            raise AppError('Credenciais inválidas', 401)
        if not user.active:
            raise AppError('Usuário inativo', 403)
        return {
            'message': 'Login realizado com sucesso',
            'user': user.to_dict(),
            'token': self.auth_service.issue_token(user),
        }
