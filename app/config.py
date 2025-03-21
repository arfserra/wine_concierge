import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    app_name: str = os.getenv("APP_NAME", "Wine Storage")
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./wine_storage.db")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    class Config:
        env_file = ".env"

settings = Settings()