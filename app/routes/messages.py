import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from app import models, schemas, database
from app.dependencies import get_current_user, get_db

logger = logging.getLogger(__name__)

router = APIRouter()


# 1. Créer un message dans le contexte d'une alerte donnée
@router.post("/", response_model=schemas.MessageResponse)
def create_message(request: Request, alert_id: int, message: schemas.MessageCreate, db: Session = Depends(get_db),
                   current_user: models.User = Depends(get_current_user)):
    logger.info("Requête POST sur /api/alerts/%s/messages/ avec body : %s", alert_id, message.dict())
    logger.info("Cookies reçus : %s", request.cookies)
    # Vérifier que l'alerte existe
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")

    new_message = models.Message(
        alert_id=alert_id,
        sender_id=current_user.id,  # On utilise l'ID de l'utilisateur connecté
        content=message.content,
        media_url = message.media_url,
        created_at = datetime.utcnow()
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message


# 2. Lister tous les messages d'une alerte
@router.get("/", response_model=list[schemas.MessageResponse])
def list_messages(alert_id: int, db: Session = Depends(get_db),
                  current_user: models.User = Depends(get_current_user)):
    # Vérifier que l'alerte existe
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")

    messages = (
        db.query(models.Message)
        .options(joinedload(models.Message.sender))
        .filter(models.Message.alert_id == alert_id)
        .all()
    )
    logger.info("Messages", messages)
    return messages


# 3. Supprimer un message (seul l'expéditeur peut supprimer)
@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(alert_id: int, message_id: int, db: Session = Depends(get_db),
                   current_user: models.User = Depends(get_current_user)):
    message = db.query(models.Message).filter(models.Message.id == message_id,
                                              models.Message.alert_id == alert_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message non trouvé")

    if message.sender_id != current_user.id:
        raise HTTPException(status_code=403, detail="Non autorisé à supprimer ce message")

    db.delete(message)
    db.commit()
    return


# 4. Marquer un message comme lu (enregistrer une lecture)
@router.post("/{message_id}/read", response_model=schemas.MessageReadResponse)
def mark_message_read(alert_id: int, message_id: int, db: Session = Depends(get_db),
                      current_user: models.User = Depends(get_current_user)):
    message = db.query(models.Message).filter(models.Message.id == message_id,
                                              models.Message.alert_id == alert_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message non trouvé")
    # Vérifier si un read receipt existe déjà pour cet utilisateur et ce message
    read_receipt = db.query(models.MessageRead).filter(
        models.MessageRead.message_id == message_id,
        models.MessageRead.user_id == current_user.id
    ).first()

    if read_receipt:
        return read_receipt
    new_receipt = models.MessageRead(
        message_id=message_id,
        user_id=current_user.id
    )
    db.add(new_receipt)
    db.commit()
    db.refresh(new_receipt)
    return new_receipt


# 5. Ajouter une réaction (emoji) à un message
@router.post("/{message_id}/reaction", response_model=schemas.MessageReactionResponse)
def add_reaction(alert_id: int, message_id: int, reaction: schemas.MessageReactionCreate, db: Session = Depends(get_db),
                 current_user: models.User = Depends(get_current_user)):
    message = db.query(models.Message).filter(models.Message.id == message_id,
                                              models.Message.alert_id == alert_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message non trouvé")
    # Vérifier si l'utilisateur a déjà réagi avec le même emoji (si on ne veut pas autoriser plusieurs réactions identiques)
    existing_reaction = db.query(models.MessageReaction).filter(
        models.MessageReaction.message_id == message_id,
        models.MessageReaction.user_id == current_user.id,
        models.MessageReaction.emoji == reaction.emoji
    ).first()
    if existing_reaction:
        raise HTTPException(status_code=400, detail="Réaction déjà ajoutée")
    new_reaction = models.MessageReaction(
        message_id=message_id,
        user_id=current_user.id,
        emoji=reaction.emoji
    )
    db.add(new_reaction)
    db.commit()
    db.refresh(new_reaction)
    return new_reaction


# 6. Supprimer une réaction d'un message
@router.delete("/{message_id}/reaction", status_code=status.HTTP_204_NO_CONTENT)
def remove_reaction(alert_id: int, message_id: int, emoji: str, db: Session = Depends(get_db),
                    current_user: models.User = Depends(get_current_user)):
    reaction = db.query(models.MessageReaction).filter(
        models.MessageReaction.message_id == message_id,
        models.MessageReaction.user_id == current_user.id,
        models.MessageReaction.emoji == emoji
    ).first()
    if not reaction:
        raise HTTPException(status_code=404, detail="Réaction non trouvée")
    db.delete(reaction)
    db.commit()
    return
