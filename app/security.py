from datetime import datetime, timedelta
from jose import jwt, JWTError
import uuid
from .config import settings
from .schemas.token import TokenPayload

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_EXPIRE = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_EXPIRE = settings.REFRESH_TOKEN_EXPIRE_DAYS


def create_access_token(subject: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_EXPIRE)
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(subject: str, jti: str) -> str:
    expire = datetime.utcnow() + timedelta(days=REFRESH_EXPIRE)
    to_encode = {"sub": subject, "exp": expire, "jti": jti}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenPayload(**payload)
    except JWTError as e:
        raise
