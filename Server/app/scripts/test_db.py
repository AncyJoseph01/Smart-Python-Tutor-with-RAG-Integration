import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.db.models import User, Chat, Base
from app.core.config import settings
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def insert_test_data():
    engine = create_async_engine(str(settings.DATABASE_URL), echo=True)
    AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with AsyncSessionLocal() as session:
            # 1️⃣ Create user
            hashed_password = pwd_context.hash("1234")
            user = User(name="Ancy", email="ancy@example.com", password=hashed_password)
            session.add(user)
            await session.flush()  # so user.id is available

            # 2️⃣ Create chat session (example: session_id = 1)
            chat1 = Chat(
                chat_session_id=1,
                user_id=user.id,
                query="Hello chatbot!",
                answer="Hi Ancy! How can I help you today?"
            )
            chat2 = Chat(
                chat_session_id=1,
                user_id=user.id,
                query="What's the weather like?",
                answer="It's sunny and 25°C."
            )

            session.add_all([chat1, chat2])
            await session.commit()

            # 3️⃣ Verify insertion
            result = await session.execute(select(User).where(User.email == "ancy@example.com"))
            inserted_user = result.scalar_one()
            print(f"[✅] Inserted User: {inserted_user.name}, ID: {inserted_user.id}")

    except Exception as e:
        print(f"[❌] Error: {e}")
        await session.rollback()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(insert_test_data())
