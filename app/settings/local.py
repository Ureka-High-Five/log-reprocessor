from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class LocalSettings(BaseSettings):
    DB_NAME: str
    W2V_MODEL_PATH: str
    MONGO_DB_NAME: str
    MONGO_DB_HOST: str
    MONGO_DB_PORT: int
    DEV_REDIS_HOST: str
    DEV_REDIS_PORT: int

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
    )


settings = LocalSettings()
