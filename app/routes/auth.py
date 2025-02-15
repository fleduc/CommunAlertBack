from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from sqlalchemy.orm import Session
from datetime import timedelta
from app import models, schemas, database, security, config
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# Utilisez get_db en tant que dépendance, pas directement database.SessionLocal
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/login", response_model=schemas.Token, tags=["auth"])
def login(
        user_credentials: schemas.UserLogin = Body(...),
        local_kw: str = Query(default=None),  # Ce paramètre sera consommé ici et ne sera pas transmis plus loin
        db: Session = Depends(get_db)  # Utilisez get_db pour obtenir la session
):
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    if not user or not verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email ou mot de passe invalide")

    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"user_id": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
