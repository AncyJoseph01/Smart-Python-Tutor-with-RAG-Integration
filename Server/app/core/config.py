from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str
    LLM_API_KEY: str
    HEYGEN_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()