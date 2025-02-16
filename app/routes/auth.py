from fastapi import APIRouter, Depends, HTTPException, status, Body, Response, Query
from sqlalchemy.orm import Session
from datetime import timedelta
from app import models, schemas, database, security, config
from passlib.context import CryptContext
import logging

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()
logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/login", response_model=schemas.Token, tags=["auth"])
def login(
        user_credentials: schemas.UserLogin = Body(...),
        local_kw: str = Query(default=None),  # Pour contourner un problème éventuel, si nécessaire
        response: Response = None,
        db: Session = Depends(get_db)
):
    logger.info(f"Tentative de connexion pour {user_credentials.email}")

    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    if not user or not verify_password(user_credentials.password, user.password):
        logger.warning(f"Échec de connexion pour {user_credentials.email}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email ou mot de passe invalide")

    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(
        data={"user_id": user.id, "user_name": user.username}, expires_delta=access_token_expires
    )

    # Définir le cookie JWT avec l'attribut SameSite
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,  # Empêche l'accès via JavaScript
        secure=False,   # Mettez True en production avec HTTPS
        samesite="lax", # 'lax' est recommandé pour protéger contre le CSRF
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Optionnel : durée de vie du cookie en secondes
        path="/",
        domain="localhost"
    )

    logger.info(f"Connexion réussie pour {user_credentials.email}, token généré: {token}")
    return {"access_token": token, "token_type": "bearer"}


@router.post("/logout", tags=["auth"])
def logout(response: Response):
    """
    Dans une architecture JWT stateless, le logout consiste à supprimer le cookie contenant le token.
    Cet endpoint supprime le cookie 'access_token' afin de "déconnecter" l'utilisateur.
    """
    response.delete_cookie(key="access_token", path="/")
    return {"message": "Déconnexion réussie"}