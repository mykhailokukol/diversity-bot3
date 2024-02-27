from os import getenv

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


class Settings:
    TG_TOKEN: str = getenv("TG_TOKEN")
    MODERATOR_ID: int = getenv("MODERATOR_ID")
    MONGODB_CLIENT_URL: str = getenv("MONGODB_CLIENT_URL")
    EXCHANGE_RATE_API_TOKEN: str = getenv("EXCHANGE_RATE_API_TOKEN")


settings = Settings()
