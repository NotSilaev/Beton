from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_BOT_WHITE_LIST: list

    # Beton API
    BETON_API_URL: str
    BETON_API_AUTH_TOKEN: str

    class Config:
        env_file = Path(__file__).parent / '.env'


settings = Settings()
