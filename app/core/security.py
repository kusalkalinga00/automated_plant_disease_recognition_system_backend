import datetime, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jwt import ExpiredSignatureError, InvalidSignatureError, DecodeError

from app.core.config import settings
from app.db.deps import get_db
from app.db.models import User

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

# must match your real login URL (with version prefix)
bearer_scheme = HTTPBearer(bearerFormat="JWT", auto_error=False)


def hash_password(plain: str) -> str:
    return pwd.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd.verify(plain, hashed)


def _create_token(sub: str, minutes: int) -> str:
    now = datetime.datetime.utcnow()
    payload = {"sub": sub, "iat": now, "exp": now + datetime.timedelta(minutes=minutes)}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def create_access_token(user_id: str) -> str:
    return _create_token(user_id, minutes=getattr(settings, "ACCESS_TOKEN_MINUTES", 15))


def create_refresh_token(user_id: str) -> str:
    days = getattr(settings, "REFRESH_TOKEN_DAYS", 14)
    return _create_token(user_id, minutes=days * 24 * 60)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> User:
    if not credentials or (credentials.scheme or "").lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    token = credentials.credentials
    try:
        payload = decode_token(token)
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except InvalidSignatureError:
        raise HTTPException(status_code=401, detail="Invalid signature")
    except DecodeError:
        raise HTTPException(status_code=401, detail="Malformed token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    uid = payload.get("sub")
    user = db.query(User).filter(User.id == uid).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found for token")
    return user


def admin_required(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")
    return user
