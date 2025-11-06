import uuid
import logging
from dependency import get_db
from libs.llm import get_llm_response
import asyncio
from threading import Thread

from sqlalchemy.orm import Session
from fastapi import WebSocket, WebSocketDisconnect, Depends, APIRouter
from schemas.models import Conversation, ChatRoom, Message, UserAccount

router = APIRouter(prefix="/ws", tags=["websocket"])

logger = logging.getLogger("ws_chat")
logging.basicConfig(level=logging.DEBUG)

def get_next(streamer):
    try:
        return next(iter(streamer))
    except StopIteration:
        return None

async def async_generator(streamer):
    while True:
        next_item = await asyncio.to_thread(get_next, streamer)
        if next_item is None:
            break
        yield next_item

@router.websocket("/chat/{room_id}/{username}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, username: str, db: Session = Depends(get_db)):
    logger.debug(f"WebSocket connection attempt: room_id={room_id}, username={username}")
    try:
        room_uuid = uuid.UUID(room_id)
    except ValueError:
        await websocket.accept()
        logger.error(f"Invalid room ID format: {room_id}")
        await websocket.send_text("Error: Invalid room ID format")
        await websocket.close()
        return

    user = db.query(UserAccount).filter(UserAccount.username == username).first()
    if not user:
        await websocket.accept()
        logger.error(f"User does not exist: {username}")
        # await websocket.send_text("Error: User does not exist")
        await websocket.close()
        return

    room = db.query(ChatRoom).filter(ChatRoom.id == room_uuid, ChatRoom.username == username).first()
    if not room:
        await websocket.accept()
        logger.error(f"ChatRoom does not exist or does not belong to this user: room_id={room_id}, username={username}")
        # await websocket.send_text("Error: ChatRoom does not exist or does not belong to this user")
        await websocket.close()
        return

    await websocket.accept()
    logger.debug(f"WebSocket connection accepted: room_id={room_id}, username={username}")
    try:
        while True:
            data = await websocket.receive_text()
            logger.debug(f"Received data from user {username} in room {room_id}: {data}")

            convo = Conversation(chatRoom_id=room_uuid, query=data, responseMessage="")
            db.add(convo)
            db.commit()
            db.refresh(convo)
            logger.debug(f"Conversation created: id={convo.id}, query={data}")

            streamer_response = get_llm_response(room_id, data)

            if isinstance(streamer_response, str):
                logger.error(f"LLM response is an error string: {streamer_response}")
                await websocket.send_text(streamer_response)
                continue

            # Start generation in a separate thread
            thread = Thread(target=lambda: streamer_response.model.generate(**streamer_response.inputs, streamer=streamer_response.streamer, max_new_tokens=64, use_cache=True))
            thread.start()

            # Stream response back to the client
            generated_text = ""
            async for new_text in async_generator(streamer_response.streamer):
                generated_text += new_text
                await websocket.send_text(generated_text)

            thread.join()
            logger.debug(f"LLM response: {generated_text}")
            convo.responseMessage = generated_text
            db.commit()
            logger.debug(f"Conversation updated with response: id={convo.id}")

            msg = Message(conversation_id=convo.id, senderUsername=username, rating=None)
            db.add(msg)
            db.commit()
            logger.debug(f"Message created: conversation_id={convo.id}, senderUsername={username}")

    except WebSocketDisconnect:
        logger.info(f"Room {room_id} (user={username}): client disconnected")
        print(f"Room {room_id} (user={username}): client disconnected")
