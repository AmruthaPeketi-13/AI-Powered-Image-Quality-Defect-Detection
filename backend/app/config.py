"""Application-wide settings loaded from environment variables."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./data/results.db"
    max_upload_size_mb: int = 10
    model_dir: str = "ml/artifacts"
    allowed_content_types: list[str] = [
        "image/jpeg", "image/png", "image/webp", "image/bmp"
    ]

    class Config:
        env_file = ".env"


settings = Settings()
