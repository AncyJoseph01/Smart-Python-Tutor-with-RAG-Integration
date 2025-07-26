from databases import Database
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from core.config import settings

database = Database(settings.DATABASE_URL)
Base = declarative_base()