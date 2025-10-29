import uuid
from fastapi import WebSocket, WebSocketDisconnect, Depends, APIRouter
from sqlalchemy.orm import Session
from libs.llm import get_llm_response
from schemas.models import Conversation, ChatRoom, Message, UserAccount
from dependency import get_db

router = APIRouter(prefix="/ws", tags=["websocket"])



@router.websocket("/chat/{room_id}/{username}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, username: str, db: Session = Depends(get_db)):
    try:
        room_uuid = uuid.UUID(room_id)
    except ValueError:
        await websocket.accept()
        await websocket.send_text("Error: Invalid room ID format")
        await websocket.close()
        return

    user = db.query(UserAccount).filter(UserAccount.username == username).first()
    if not user:
        await websocket.accept()
        # await websocket.send_text("Error: User does not exist")
        await websocket.close()
        return

    room = db.query(ChatRoom).filter(ChatRoom.id == room_uuid, ChatRoom.username == username).first()
    if not room:
        await websocket.accept()
        # await websocket.send_text("Error: ChatRoom does not exist or does not belong to this user")
        await websocket.close()
        return

    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()

            convo = Conversation(chatRoom_id=room_uuid, query=data, responseMessage="")
            db.add(convo)
            db.commit()
            db.refresh(convo)

            response = get_llm_response(data)
            convo.responseMessage = response
            db.commit()

            msg = Message(conversation_id=convo.id, senderUsername=username, rating=None)
            db.add(msg)
            db.commit()

            await websocket.send_text(response)

    except WebSocketDisconnect:
        print(f"Room {room_id} (user={username}): client disconnected")
