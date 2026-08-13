from functools import wraps

from flask import session

from errors import AuthenticationError, AuthorizationError


def current_user():
    return session.get("user")


def login_user(user):
    session.clear()
    session["user"] = {
        "id": user["id"],
        "nome": user["nome"],
        "email": user["email"],
        "tipo": user["tipo"],
    }


def require_login(handler):
    @wraps(handler)
    def wrapped(*args, **kwargs):
        if current_user() is None:
            raise AuthenticationError()
        return handler(*args, **kwargs)

    return wrapped


def require_admin(handler):
    @wraps(handler)
    def wrapped(*args, **kwargs):
        user = current_user()
        if user is None:
            raise AuthenticationError()
        if user["tipo"] != "admin":
            raise AuthorizationError()
        return handler(*args, **kwargs)

    return wrapped


def require_self_or_admin(user_id):
    user = current_user()
    if user is None:
        raise AuthenticationError()
    if user["tipo"] != "admin" and user["id"] != user_id:
        raise AuthorizationError()
