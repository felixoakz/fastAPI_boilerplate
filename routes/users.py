from models.user import User
from sqlalchemy.future import select
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from utils.dependencies import db_session, get_current_user_from_cookie


router = APIRouter()

@router.get("/users", tags=['Users'])
async def get_users(
    db: AsyncSession = Depends(db_session),
    _: User = Depends(get_current_user_from_cookie)
):
    result = await db.execute(select(User))
    users = result.scalars().all()

    return users
