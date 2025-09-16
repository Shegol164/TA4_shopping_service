from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from app.models.user import User
from app.core.security import get_password_hash

async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalar_one_or_none()

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalar_one_or_none()

async def get_user_by_phone(db: AsyncSession, phone: str):
    result = await db.execute(select(User).filter(User.phone == phone))
    return result.scalar_one_or_none()

async def get_user_by_login(db: AsyncSession, login: str):
    """Get user by email or phone"""
    result = await db.execute(
        select(User).filter(
            or_(User.email == login, User.phone == login)
        )
    )
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user_data):
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        phone=user_data.phone,
        hashed_password=hashed_password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user