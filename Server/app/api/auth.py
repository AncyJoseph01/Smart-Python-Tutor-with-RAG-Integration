import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from app.db.database import database
from app.db.models import User
from app.schemas.user import UserCreate, UserOut
from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_db():
    try:
        yield database
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {str(e)}")
        raise  # Re-raise the exception
    finally:
        pass  # No close() needed here

@router.post("/register", response_model=UserOut)
async def register(user: UserCreate, db: database = Depends(get_db)):
    logger.info(f"Processing registration for email: {user.email}")
    # Lowercase email for uniqueness
    email = user.email.lower()

    # Check if email already exists
    query = select(User).where(User.email == email)
    existing_user = await db.fetch_one(query)
    if existing_user:
        logger.warning(f"Registration attempt with existing email: {email}")
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password before saving
    hashed_password = pwd_context.hash(user.password)
    logger.debug(f"Hashed password for {email}")

    # Use a transaction context
    async with db.transaction():
        logger.info(f"Starting transaction for user: {email}")
        # Insert new user with hashed password
        query = User.__table__.insert().values(
            name=user.name,
            email=email,
            password=hashed_password
        )
        user_id = await db.execute(query)
        logger.info(f"Successfully inserted user with ID: {user_id}")
    logger.info(f"Registration completed for user: {email}")
    return {"id": user_id, "name": user.name, "email": email}

@router.post("/login")
async def login(email: str, password: str, db: database = Depends(get_db)):
    logger.info(f"Login attempt for email: {email}")
    email = email.lower()
    query = select(User).where(User.email == email)
    user = await db.fetch_one(query)

    if not user:
        logger.warning(f"Failed login attempt for non-existent email: {email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # user.password here is hashed, verify it
    if not pwd_context.verify(password, user.password):
        logger.warning(f"Failed login attempt for email: {email} due to incorrect password")
        raise HTTPException(status_code=401, detail="Invalid email or password")

    logger.info(f"Successful login for user: {user.name}")
    return {"message": f"Welcome back, {user.name}!"}