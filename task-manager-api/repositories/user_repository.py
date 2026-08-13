from sqlalchemy import func, select

from database import db
from models.task import Task
from models.user import User


class UserRepository:
    @staticmethod
    def get(user_id):
        return db.session.get(User, user_id)

    @staticmethod
    def get_by_email(email):
        return db.session.scalar(select(User).where(User.email == email))

    @staticmethod
    def list_with_task_counts():
        return db.session.execute(
            select(User, func.count(Task.id))
            .outerjoin(Task, Task.user_id == User.id)
            .group_by(User.id)
            .order_by(User.id)
        ).all()

    @staticmethod
    def add(user):
        db.session.add(user)

    @staticmethod
    def delete(user):
        db.session.delete(user)
