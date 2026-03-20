import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for fastAPI"""

    secret_key: str = "secret"
    algorithm: str = "HS256"
    adapter: str = "in_memory"

    db_user: str = "savibud_user"
    db_host: str = "db"
    db_name: str = "savibud"
    db_password: str = (
        ""  # Pydantic reads this from /run/secrets/db_password or .secrets/
    )

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:5432/{self.db_name}"

    powens_client_id: str = ""
    powens_client_secret: str = ""
    powens_redirect_uri: str = ""
    powens_domain: str = "api.powens.com"

    _secrets_dir = "/run/secrets" if os.path.exists("/run/secrets") else ".secrets"

    # Important: env_file_encoding is often required for some OS environments
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        secrets_dir=_secrets_dir,
        extra="ignore",  # Useful if you have extra stuff in .env
    )

    print(f"DEBUG: Using secrets from {_secrets_dir}")


settings = Settings()
if not settings.db_password:
    print("DEBUG: WARNING - db_password is empty!")
