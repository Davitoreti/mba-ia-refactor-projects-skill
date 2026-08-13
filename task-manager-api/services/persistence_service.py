from sqlalchemy.exc import SQLAlchemyError

from database import db
from errors import AppError


def commit_or_raise(message):
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise AppError(message, 500) from None
