from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.utils.response import api_response
from app.db.deps import get_db
from app.db.models import User
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
)
from app.schemas.auth import RegisterIn, UserOut, TokenPairOut, RefreshIn, LoginIn

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(data: RegisterIn, db: Session = Depends(get_db)):
    email = data.email.lower()
    if db.query(User).filter(User.email == email).first():
        return api_response(False, "Email already registered", None, None)
    u = User(
        email=email,
        password_hash=hash_password(data.password),
        full_name=data.full_name or "",
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    payload = UserOut(
        id=u.id, email=u.email, full_name=u.full_name, is_admin=u.is_admin
    ).model_dump()
    return api_response(True, "User registered successfully", payload, None)


@router.post("/login")  # <-- now JSON body
def login(data: LoginIn, db: Session = Depends(get_db)):
    email = data.email.lower()
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(data.password, user.password_hash):
        return api_response(False, "Invalid credentials", None, None)

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    payload = {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
        "user": UserOut(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_admin=user.is_admin,
        ).model_dump(),
    }
    return api_response(True, "Login successful", payload, None)


@router.post("/refresh")
def refresh(data: RefreshIn, db: Session = Depends(get_db)):
    try:
        decoded = decode_token(data.refresh_token)
        uid = decoded.get("sub")
        user = db.query(User).filter(User.id == uid).first()
        if not user:
            return api_response(False, "Invalid refresh token", None, None)
        access = create_access_token(user.id)
        return api_response(
            True,
            "Token refreshed",
            {"access_token": access, "token_type": "bearer"},
            None,
        )
    except Exception:
        return api_response(False, "Invalid or expired refresh token", None, None)


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    payload = UserOut(
        id=user.id, email=user.email, full_name=user.full_name, is_admin=user.is_admin
    ).model_dump()
    return api_response(True, "Current user", payload, None)
