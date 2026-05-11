from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    telegram_api_id: int = Field(alias="TELEGRAM_API_ID")
    telegram_api_hash: str = Field(alias="TELEGRAM_API_HASH")
    telegram_session_name: str = Field(default="media_archiver", alias="TELEGRAM_SESSION_NAME")
    telegram_bot_token: str | None = Field(default=None, alias="TELEGRAM_BOT_TOKEN")
    telegram_channel: str = Field(alias="TELEGRAM_CHANNEL")
    telegram_download_dir: Path = Field(default=Path("downloads"), alias="TELEGRAM_DOWNLOAD_DIR")
    database_path: Path = Field(default=Path("data/archiver.db"), alias="DATABASE_PATH")
    rclone_remote: str = Field(alias="RCLONE_REMOTE")
    rclone_path_template: str = Field(
        default="{channel}/{year}/{month}/{filename}",
        alias="RCLONE_PATH_TEMPLATE",
    )
    rclone_extra_args: str = Field(default="", alias="RCLONE_EXTRA_ARGS")
    max_concurrent_uploads: int = Field(default=2, alias="MAX_CONCURRENT_UPLOADS")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    history_limit: int = Field(default=0, alias="HISTORY_LIMIT")

    @model_validator(mode="after")
    def validate_authentication(self) -> "Settings":
        if self.telegram_bot_token:
            return self
        if not self.telegram_session_name:
            raise ValueError("TELEGRAM_SESSION_NAME is required when TELEGRAM_BOT_TOKEN is not set")
        return self

    @property
    def uses_bot_token(self) -> bool:
        return bool(self.telegram_bot_token)

    def ensure_directories(self) -> None:
        self.telegram_download_dir.mkdir(parents=True, exist_ok=True)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
