from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="WINDSIGHT_",
        extra="ignore",
    )

    allowed_origins: list[str] = ["http://localhost:5173"]
    snapshot_path: Path = Path("../data/processed/january-2026.v1.json")


@lru_cache
def get_settings() -> Settings:
    return Settings()
