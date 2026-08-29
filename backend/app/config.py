"""Application-wide settings loaded from environment variables."""
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    database_url: str = "sqlite:///./data/results.db"
    max_upload_size_mb: int = 10
    model_dir: str = "ml/artifacts"
    allowed_content_types: list[str] = [
        "image/jpeg", "image/png", "image/webp", "image/bmp"
    ]


settings = Settings()
