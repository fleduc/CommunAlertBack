import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app import models, schemas, database
from typing import List

logger = logging.getLogger(__name__)

router = APIRouter()

print("✅ Routes ALERTS chargées")


# Dépendance pour obtenir la session DB
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[schemas.AlertResponse])
def list_alerts(request: Request, db: Session = Depends(get_db)):
    logger.info("Requête GET sur /api/alerts/")
    logger.info("Cookies reçus : %s", request.cookies)
    logger.info("Query params : %s", request.query_params)
    return db.query(models.Alert).all()


@router.get("/{alert_id}", response_model=schemas.AlertResponse)
def get_alert(request: Request, alert_id: int, db: Session = Depends(get_db)):
    logger.info("Requête GET sur /api/alert{id}/")
    logger.info("Cookies reçus : %s", request.cookies)
    logger.info("Query params : %s", request.query_params)
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alerte non trouvée")
    return alert


@router.post("/", response_model=schemas.AlertResponse)
def create_alert(request: Request, alert: schemas.AlertCreate, db: Session = Depends(get_db)):
    logger.info("Requête POST sur /api/alerts/ avec body : %s", alert.dict())
    logger.info("Cookies reçus : %s", request.cookies)
    new_alert = models.Alert(
        alert_title=alert.alert_title,
        description=alert.description,
        alert_type=alert.alert_type,
        closing_date=alert.closing_date,
        postal_code=alert.postal_code,
        user_id=alert.user_id
    )
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    return new_alert


# Endpoint pour modifier une alerte
@router.put("/{alert_id}", response_model=schemas.AlertResponse)
def update_alert(alert_id: int, alert_update: schemas.AlertUpdate, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alerte non trouvée")

    # Mettre à jour les champs uniquement s'ils sont fournis dans la requête
    if alert_update.alert_title is not None:
        alert.alert_title = alert_update.alert_title
    if alert_update.description is not None:
        alert.description = alert_update.description
    if alert_update.alert_type is not None:
        alert.alert_type = alert_update.alert_type
    if alert_update.closing_date is not None:
        alert.closing_date = alert_update.closing_date
    if alert_update.postal_code is not None:
        alert.postal_code = alert_update.postal_code
    if alert_update.user_id is not None:
        alert.user_id = alert_update.user_id

    db.commit()
    db.refresh(alert)
    return alert


# Endpoint pour supprimer une alerte
@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alerte non trouvée")
    db.delete(alert)
    db.commit()
    return
