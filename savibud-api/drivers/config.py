from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Settings for fastAPI"""

    secret_key: str = "secret"
    algorithm: str = "HS256"
    adapter: str = "in_memory"

    db_user: str = "savibud_user"
    db_host: str = "db"
    db_name: str = "savibud"
    db_password: str = "" # Pydantic reads this from /run/secrets/db_password or .secrets/

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:5432/{self.db_name}"

    powens_client_id: str = ""
    powens_client_secret: str = ""
    powens_redirect_uri: str = ""
    powens_domain: str = "api.powens.com"

    # Important: env_file_encoding is often required for some OS environments
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        secrets_dir=".secrets",
        extra='ignore' # Useful if you have extra stuff in .env
    )

settings = Settings()