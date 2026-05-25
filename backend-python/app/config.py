from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    SECRET_KEY: str = "super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/cromos.db"
    UPLOADS_DIR: Path = BASE_DIR / "uploads"

    class Config:
        env_file = ".env"


settings = Settings()
