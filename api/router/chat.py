import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from router.auth import get_current_user
from schemas.models import ChatRoom, Conversation, Message, UserAccount
from sqlalchemy import asc
from dependency import get_db

router = APIRouter(prefix="/chat", tags=["chat"])

logger = logging.getLogger(__name__)
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.DEBUG)
logger.debug("router.chat module loaded")


@router.post("/create-room")
def create_room(
    roomName: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    logger.debug(f"create_room called: roomName={roomName}, user={current_user.username}")
    existing = (
        db.query(ChatRoom)
        .filter(ChatRoom.roomName == roomName, ChatRoom.username == current_user.username)
        .first()
    )
    if existing:
        logger.warning(f"Room already exists for user={current_user.username}, roomName={roomName}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room already exists for this user",
        )

    room = ChatRoom(roomName=roomName, username=current_user.username)
    db.add(room)
    db.commit()
    db.refresh(room)
    logger.info(f"Room created: id={room.id}, name={room.roomName}, owner={current_user.username}")
    return {
        "id": str(room.id), 
        "roomName": room.roomName,
        "owner": current_user.username,
    }


@router.get("/rooms")
def get_rooms(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    logger.debug(f"get_rooms called for user={current_user.username}")
    rooms = db.query(ChatRoom).filter(ChatRoom.username == current_user.username).all()
    logger.info(f"Found {len(rooms)} rooms for user={current_user.username}")
    return [
        {"id": str(r.id), "roomName": r.roomName, "owner": r.username} for r in rooms
    ]


@router.get("/room/{room_id}")
def get_room(
    room_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    logger.debug(f"get_room called: room_id={room_id}, user={current_user.username}")
    room = (
        db.query(ChatRoom)
        .filter(ChatRoom.id == room_id, ChatRoom.username == current_user.username)
        .first()
    )
    if not room:
        logger.warning(f"Room not found: room_id={room_id}, user={current_user.username}")
        raise HTTPException(status_code=404, detail="Room not found")
    logger.info(f"Room found: id={room.id}, name={room.roomName}, owner={room.username}")
    return {"id": str(room.id), "roomName": room.roomName, "owner": room.username}


@router.put("/room/{room_id}")
def update_room(
    room_id: uuid.UUID, 
    new_name: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    logger.debug(f"update_room called: room_id={room_id}, new_name={new_name}, user={current_user.username}")
    room = (
        db.query(ChatRoom)
        .filter(ChatRoom.id == room_id, ChatRoom.username == current_user.username)
        .first()
    )
    if not room:
        logger.warning(f"Room not found for update: room_id={room_id}, user={current_user.username}")
        raise HTTPException(status_code=404, detail="Room not found")

    duplicate = (
        db.query(ChatRoom)
        .filter(ChatRoom.roomName == new_name, ChatRoom.username == current_user.username)
        .first()
    )
    if duplicate:
        logger.warning(f"Duplicate room name for user={current_user.username}: new_name={new_name}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A room with this name already exists",
        )

    room.roomName = new_name
    db.commit()
    db.refresh(room)
    logger.info(f"Room updated: id={room.id}, new_name={room.roomName}, owner={room.username}")
    return {"id": str(room.id), "roomName": room.roomName, "owner": room.username}


@router.delete("/room/{room_id}")
def delete_room(
    room_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    logger.debug(f"delete_room called: room_id={room_id}, user={current_user.username}")
    room = (
        db.query(ChatRoom)
        .filter(ChatRoom.id == room_id, ChatRoom.username == current_user.username)
        .first()
    )
    if not room:
        logger.warning(f"Room not found for delete: room_id={room_id}, user={current_user.username}")
        raise HTTPException(status_code=404, detail="Room not found")

    db.delete(room)
    db.commit()
    logger.info(f"Room deleted: id={room_id}, user={current_user.username}")
    return {"message": "Room deleted successfully"}


@router.get("/history/{chatroom_id}")
def get_conversation_history(
    chatroom_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    logger.debug(f"get_conversation_history called: chatroom_id={chatroom_id}, user={current_user.username}")
    chatroom = (
        db.query(ChatRoom)
        .filter(ChatRoom.id == chatroom_id, ChatRoom.username == current_user.username)
        .first()
    )
    if not chatroom:
        logger.warning(f"Chat room not found for history: chatroom_id={chatroom_id}, user={current_user.username}")
        raise HTTPException(status_code=404, detail="Chat room not found")

    conversations = (
        db.query(Conversation)
        .filter(Conversation.chatRoom_id == chatroom_id)
        .order_by(asc(Conversation.timestamp))
        .all()
    )
    logger.info(f"Found {len(conversations)} conversations for chatroom_id={chatroom_id}")

    history = []
    for convo in conversations:
        msg = (
            db.query(Message)
            .filter(Message.conversation_id == convo.id)
            .first()
        )
        history.append({
            "conversation_id": convo.id,
            "query": convo.query,
            "response": convo.responseMessage,
            "timestamp": convo.timestamp,
            "senderUsername": msg.senderUsername if msg else None,
            "rating": msg.rating if msg else None
        })

    logger.debug(f"Returning history for chatroom_id={chatroom_id}, messages_count={len(history)}")
    return {
        "chatroom_id": str(chatroom.id),
        "chatroom_name": chatroom.roomName,
        "owner": chatroom.username,
        "messages": history
    }