from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..schemas.user import UserCreate, UserRead
from ..schemas.token import Token
from ..models.user import User
from ..models.token import RefreshToken
from ..db import get_db
from passlib.context import CryptContext
from ..security import (
    create_access_token, create_refresh_token, verify_token
)
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(tags=["auth"])

@router.post("/signup", response_model=UserRead)
async def signup(user: UserCreate, db: AsyncSession = Depends(get_db)):
    hashed = pwd_context.hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
async def login(form_data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.email == form_data.email)
    )
    user = result.scalar_one_or_none()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    jti = str(uuid.uuid4())
    access = create_access_token(str(user.id))
    refresh = create_refresh_token(str(user.id), jti)
    db_token = RefreshToken(user_id=user.id, jti=jti)
    db.add(db_token)
    await db.commit()
    return {"access_token": access, "refresh_token": refresh}

@router.post("/refresh", response_model=Token)
async def refresh(token: str, db: AsyncSession = Depends(get_db)):
    payload = verify_token(token)
    # check in DB
    result = await db.execute(select(RefreshToken).where(RefreshToken.jti == payload.jti))
    db_token = result.scalar_one_or_none()
    if not db_token or db_token.revoked:
        raise HTTPException(status_code=401, detail="Invalid token")
    new_jti = str(uuid.uuid4())
    access = create_access_token(payload.sub)
    refresh = create_refresh_token(payload.sub, new_jti)
    # revoke old
    db_token.revoked = True
    db.add(RefreshToken(user_id=int(payload.sub), jti=new_jti))
    await db.commit()
    return {"access_token": access, "refresh_token": refresh}

@router.post("/logout")
async def logout(token: str, db: AsyncSession = Depends(get_db)):
    payload = verify_token(token)
    result = await db.execute(select(RefreshToken).where(RefreshToken.jti == payload.jti))
    db_token = result.scalar_one_or_none()
    if db_token:
        db_token.revoked = True
        await db.commit()
    return {"msg": "Logged out"}
