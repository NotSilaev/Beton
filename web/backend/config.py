from pathlib import Path
from pydantic_settings import BaseSettings


class ProjectSettings(BaseSettings):
    # Django project
    DJANGO_SECRET_KEY: str

    # Database
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    # Telegram Bots
    TELEGRAM_LOGS_BOT_TOKEN: str
    TELEGRAM_LOGS_BOT_USERS: list

    class Config:
        env_file = Path(__file__).parent / '.env'


project_settings = ProjectSettings()
