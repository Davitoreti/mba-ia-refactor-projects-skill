import os
from dataclasses import dataclass


def _as_bool(value):
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    secret_key: str
    database_path: str
    debug: bool
    environment: str

    @classmethod
    def from_env(cls):
        secret_key = os.environ.get("SECRET_KEY")
        if not secret_key:
            raise RuntimeError("SECRET_KEY is required")

        return cls(
            secret_key=secret_key,
            database_path=os.environ.get("DATABASE_PATH", "loja.db"),
            debug=_as_bool(os.environ.get("FLASK_DEBUG", "false")),
            environment=os.environ.get("APP_ENV", "development"),
        )
