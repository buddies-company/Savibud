from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for fastAPI"""

    secret_key: str = "secret"  # Used to decode and encode JWT
    algorithm: str = "HS256"
    adapter: str = "in_memory"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
