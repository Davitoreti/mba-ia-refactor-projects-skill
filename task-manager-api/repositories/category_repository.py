from sqlalchemy import func, select

from database import db
from models.category import Category
from models.task import Task


class CategoryRepository:
    @staticmethod
    def get(category_id):
        return db.session.get(Category, category_id)

    @staticmethod
    def list_with_task_counts():
        return db.session.execute(
            select(Category, func.count(Task.id))
            .outerjoin(Task, Task.category_id == Category.id)
            .group_by(Category.id)
            .order_by(Category.id)
        ).all()

    @staticmethod
    def add(category):
        db.session.add(category)

    @staticmethod
    def delete(category):
        db.session.delete(category)
