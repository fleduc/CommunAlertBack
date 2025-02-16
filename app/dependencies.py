from fastapi import Cookie, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app import models, database, security


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_token_from_cookie(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return access_token


def get_current_user(token: str = Depends(get_token_from_cookie), db: Session = Depends(get_db)) -> models.User:
    # Retirez "Bearer " si présent
    if token.startswith("Bearer "):
        token = token[7:]
    payload = security.verify_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
