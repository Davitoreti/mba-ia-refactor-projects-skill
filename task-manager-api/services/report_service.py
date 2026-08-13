from datetime import datetime, timedelta, timezone

from sqlalchemy import case, func, select

from database import db
from errors import NotFoundError
from models.category import Category
from models.task import Task
from models.user import User
from repositories.task_repository import TaskRepository
from repositories.user_repository import UserRepository


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class ReportService:
    @staticmethod
    def summary():
        now = utcnow()
        seven_days_ago = now - timedelta(days=7)
        task_row = db.session.execute(
            select(
                func.count(Task.id),
                func.sum(case((Task.status == 'pending', 1), else_=0)),
                func.sum(case((Task.status == 'in_progress', 1), else_=0)),
                func.sum(case((Task.status == 'done', 1), else_=0)),
                func.sum(case((Task.status == 'cancelled', 1), else_=0)),
                *[func.sum(case((Task.priority == priority, 1), else_=0)) for priority in range(1, 6)],
                func.sum(case((Task.created_at >= seven_days_ago, 1), else_=0)),
                func.sum(case(((Task.status == 'done') & (Task.updated_at >= seven_days_ago), 1), else_=0)),
            )
        ).one()
        values = [value or 0 for value in task_row]
        total, pending, in_progress, done, cancelled, p1, p2, p3, p4, p5, recent_tasks, recent_done = values

        overdue_tasks = db.session.scalars(
            select(Task).where(
                Task.due_date < now,
                Task.status.not_in(('done', 'cancelled')),
            ).order_by(Task.id)
        ).all()
        user_rows = db.session.execute(
            select(
                User.id,
                User.name,
                func.count(Task.id),
                func.sum(case((Task.status == 'done', 1), else_=0)),
            ).outerjoin(Task, Task.user_id == User.id).group_by(User.id).order_by(User.id)
        ).all()
        user_stats = []
        for user_id, name, user_total, completed in user_rows:
            completed = completed or 0
            user_stats.append({
                'user_id': user_id,
                'user_name': name,
                'total_tasks': user_total,
                'completed_tasks': completed,
                'completion_rate': round((completed / user_total) * 100, 2) if user_total else 0,
            })

        return {
            'generated_at': str(now),
            'overview': {
                'total_tasks': total,
                'total_users': db.session.scalar(select(func.count(User.id))),
                'total_categories': db.session.scalar(select(func.count(Category.id))),
            },
            'tasks_by_status': {'pending': pending, 'in_progress': in_progress, 'done': done, 'cancelled': cancelled},
            'tasks_by_priority': {'critical': p1, 'high': p2, 'medium': p3, 'low': p4, 'minimal': p5},
            'overdue': {
                'count': len(overdue_tasks),
                'tasks': [{
                    'id': task.id,
                    'title': task.title,
                    'due_date': str(task.due_date),
                    'days_overdue': (now - task.due_date).days,
                } for task in overdue_tasks],
            },
            'recent_activity': {
                'tasks_created_last_7_days': recent_tasks,
                'tasks_completed_last_7_days': recent_done,
            },
            'user_productivity': user_stats,
        }

    @staticmethod
    def user_report(user_id):
        user = UserRepository.get(user_id)
        if not user:
            raise NotFoundError('Usuário não encontrado')
        tasks = TaskRepository.list_by_user(user_id)
        counts = {status: 0 for status in ('done', 'pending', 'in_progress', 'cancelled')}
        for task in tasks:
            if task.status in counts:
                counts[task.status] += 1
        total = len(tasks)
        return {
            'user': {'id': user.id, 'name': user.name, 'email': user.email},
            'statistics': {
                'total_tasks': total,
                **counts,
                'overdue': sum(task.is_overdue() for task in tasks),
                'high_priority': sum(task.priority <= 2 for task in tasks),
                'completion_rate': round((counts['done'] / total) * 100, 2) if total else 0,
            },
        }
