import os
from sqlmodel import select
from typing import Optional
from models.user import User
from jose import jwt, JWTError
from typing import AsyncGenerator
from utils.configs import SECRET_KEY, ALGORITHM
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

DATABASE_URL = f"mysql+aiomysql://root:{os.getenv('DB_PASSWD')}@localhost/{os.getenv('DB_NAME')}"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:

    statement = select(User).where(User.username == username)
    result = await db.execute(statement)

    return result.scalar_one_or_none()


async def get_current_user_from_cookie(
        request: Request,
        db: AsyncSession = Depends(db_session)
):
    token = request.cookies.get("Authorization")
    detail = 'Unauthenticated user'

    if not token:
        raise HTTPException(status_code=401, detail=detail)

    try:
        payload = jwt.decode(token, str(SECRET_KEY), algorithms=[ALGORITHM])
        username = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=401, detail=detail)

    except JWTError:
        raise HTTPException(status_code=401, detail=detail)

    user = await get_user_by_username(db, username=username)

    if user is None:
        raise HTTPException(status_code=401, detail=detail)

    return user
