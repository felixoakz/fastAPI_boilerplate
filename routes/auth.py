from jose import jwt
from sqlmodel import select
from typing import Optional
from passlib.context import CryptContext
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, Response, status

from models.user import User
from utils.dependencies import get_user_by_username, db_session
from utils.configs import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


auth_router = APIRouter()
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# REGISTER -------------------------------------------------------------
async def create_user(
    user: User,
    db: AsyncSession = Depends(db_session)
) -> User:

    hashed_password = bcrypt_context.hash(user.password)

    db_user = User(username=user.username, email=user.email, password=hashed_password)

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user


@auth_router.post("/register", tags=["Auth"])
async def register_user(
    user: User,
    db: AsyncSession = Depends(db_session)
) -> dict:

    existing_user = await get_user_by_username(db, username=user.username)

    if existing_user:
        raise HTTPException(status_code=400, detail="Username is already taken")

    email_taken = await db.execute(select(User).where(User.email == user.email))

    if email_taken.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email is already in use")

    await create_user(db=db, user=user)

    return {"message": "User registered successfully"}


# AUTHENTICATE ----------------------------------------------------------------
async def authenticate_user(
    username: str,
    password: str,
    db: AsyncSession
) -> Optional[User]:

    result = await db.execute(select(User).where(User.username == username))

    user = result.scalar_one_or_none()

    if not user or not bcrypt_context.verify(password, user.password):
        return None

    return user


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, str(SECRET_KEY), algorithm=ALGORITHM)


@auth_router.post("/token", tags=["Auth"])
async def get_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(db_session)
) -> Response:

    user = await authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    response = JSONResponse({"username": user.username})

    response.set_cookie(
        "Authorization",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=259200,
        expires=259200,
    )

    return response


# LOGOUT ----------------------------------------------------------------
@auth_router.post("/logout", tags=["Auth"])
async def logout_user() -> Response:

    response = JSONResponse({"message": "Logged out"})

    response.delete_cookie("Authorization", httponly=True, secure=True, samesite="strict")

    return response

