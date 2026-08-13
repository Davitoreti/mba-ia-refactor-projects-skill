from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash


class AuthService:
    SALT = "task-manager-auth"

    def __init__(self, secret_key, max_age_seconds=3600):
        self.serializer = URLSafeTimedSerializer(secret_key, salt=self.SALT)
        self.max_age_seconds = max_age_seconds

    @staticmethod
    def hash_password(password):
        return generate_password_hash(password)

    @staticmethod
    def verify_password(password_hash, password):
        return check_password_hash(password_hash, password)

    def issue_token(self, user):
        return self.serializer.dumps({"sub": user.id, "role": user.role})

    def verify_token(self, token):
        try:
            return self.serializer.loads(token, max_age=self.max_age_seconds)
        except (BadSignature, SignatureExpired):
            return None
