class AppError(Exception):
    status_code = 400
    public_message = "Erro na requisição"

    def __init__(self, message=None, *, status_code=None):
        super().__init__(message or self.public_message)
        self.public_message = message or self.public_message
        if status_code is not None:
            self.status_code = status_code


class ValidationError(AppError):
    status_code = 400


class AuthenticationError(AppError):
    status_code = 401
    public_message = "Autenticação necessária"


class AuthorizationError(AppError):
    status_code = 403
    public_message = "Acesso negado"


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409
