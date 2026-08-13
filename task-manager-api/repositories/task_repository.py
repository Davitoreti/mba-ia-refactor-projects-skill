from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from database import db
from models.task import Task


class TaskRepository:
    MAX_PAGE_SIZE = 100

    @staticmethod
    def get(task_id):
        return db.session.get(Task, task_id)

    @classmethod
    def list(cls, limit=None, offset=0):
        statement = select(Task).options(selectinload(Task.user), selectinload(Task.category)).order_by(Task.id)
        if limit is not None:
            statement = statement.limit(min(limit, cls.MAX_PAGE_SIZE)).offset(offset)
        return db.session.scalars(statement).all()

    @staticmethod
    def list_by_user(user_id):
        return db.session.scalars(select(Task).where(Task.user_id == user_id).order_by(Task.id)).all()

    @staticmethod
    def search(query='', status='', priority=None, user_id=None, limit=100):
        statement = select(Task).order_by(Task.id).limit(min(limit, TaskRepository.MAX_PAGE_SIZE))
        if query:
            statement = statement.where(or_(Task.title.like(f'%{query}%'), Task.description.like(f'%{query}%')))
        if status:
            statement = statement.where(Task.status == status)
        if priority is not None:
            statement = statement.where(Task.priority == priority)
        if user_id is not None:
            statement = statement.where(Task.user_id == user_id)
        return db.session.scalars(statement).all()

    @staticmethod
    def status_counts():
        rows = db.session.execute(select(Task.status, func.count(Task.id)).group_by(Task.status)).all()
        return dict(rows)

    @staticmethod
    def add(task):
        db.session.add(task)

    @staticmethod
    def delete(task):
        db.session.delete(task)
