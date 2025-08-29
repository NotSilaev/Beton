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

    # Cache
    CACHE_HOST: str
    CACHE_PORT: str
    CACHE_DB: int
    CACHE_MAX_CONNECTIONS: int

    # Telegram Bots
    TELEGRAM_LOGS_BOT_TOKEN: str
    TELEGRAM_LOGS_BOT_USERS: list    
    
    TELEGRAM_ORDERS_BOT_TOKEN: str
    TELEGRAM_ORDERS_BOT_USERS: list

    class Config:
        env_file = Path(__file__).parent / '.env'


project_settings = ProjectSettings()
