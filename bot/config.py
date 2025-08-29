from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Telegram Bot
    telegram_bot_token: str

    class Config:
        env_file = Path(__file__).parent / '.env'


settings = Settings()
