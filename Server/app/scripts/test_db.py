import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from db.models import User, Base
from core.config import settings
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def insert_test_data():
    engine = create_async_engine(str(settings.DATABASE_URL), echo=True)
    AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with AsyncSessionLocal() as session:
            hashed_password = pwd_context.hash("hashedpassword123")
            user = User(name="Tony Baby", email="Tony@example.com", password=hashed_password)
            session.add(user)
            await session.flush()
            await session.commit()
            print("[✅] Test data inserted successfully.")
    except Exception as e:
        print(f"[❌] Error: {e}")
        await session.rollback()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(insert_test_data())
