from functools import wraps

from flask import current_app, g, request

from database import db
from errors import AuthenticationError, AuthorizationError
from models.user import User


def _authenticate():
    header = request.headers.get("Authorization", "")
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise AuthenticationError()

    payload = current_app.extensions["auth_service"].verify_token(token)
    if not payload:
        raise AuthenticationError("Token inválido ou expirado")

    user = db.session.get(User, payload.get("sub"))
    if not user or not user.active:
        raise AuthenticationError("Token inválido ou expirado")
    g.current_user = user
    return user


def require_auth(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        _authenticate()
        return view(*args, **kwargs)

    return wrapped


def require_roles(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user = _authenticate()
            if user.role not in roles:
                raise AuthorizationError()
            return view(*args, **kwargs)

        return wrapped

    return decorator
