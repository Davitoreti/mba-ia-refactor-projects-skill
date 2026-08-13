from errors import AppError, NotFoundError
from models.category import Category
from repositories.category_repository import CategoryRepository
from services.persistence_service import commit_or_raise
from utils.validators import require_json, require_string


class CategoryController:
    @staticmethod
    def list_categories():
        result = []
        for category, task_count in CategoryRepository.list_with_task_counts():
            data = category.to_dict()
            data['task_count'] = task_count
            result.append(data)
        return result

    @staticmethod
    def _validate_color(color):
        if not isinstance(color, str) or len(color) != 7 or not color.startswith('#'):
            raise AppError('Cor inválida')
        try:
            int(color[1:], 16)
        except ValueError:
            raise AppError('Cor inválida') from None
        return color

    @classmethod
    def create_category(cls, data):
        require_json(data)
        category = Category(
            name=require_string(data, 'name', 'Nome é obrigatório'),
            description=data.get('description', ''),
            color=cls._validate_color(data.get('color', '#000000')),
        )
        if not isinstance(category.description, str):
            raise AppError('Dados inválidos')
        CategoryRepository.add(category)
        commit_or_raise('Erro ao criar categoria')
        return category.to_dict()

    @classmethod
    def update_category(cls, category_id, data):
        category = CategoryRepository.get(category_id)
        if not category:
            raise NotFoundError('Categoria não encontrada')
        require_json(data)
        if 'name' in data:
            category.name = require_string(data, 'name', 'Nome é obrigatório')
        if 'description' in data:
            if not isinstance(data['description'], str):
                raise AppError('Dados inválidos')
            category.description = data['description']
        if 'color' in data:
            category.color = cls._validate_color(data['color'])
        commit_or_raise('Erro ao atualizar')
        return category.to_dict()

    @staticmethod
    def delete_category(category_id):
        category = CategoryRepository.get(category_id)
        if not category:
            raise NotFoundError('Categoria não encontrada')
        CategoryRepository.delete(category)
        commit_or_raise('Erro ao deletar')
        return {'message': 'Categoria deletada'}
