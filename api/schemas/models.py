from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship, declarative_base
import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

Base = declarative_base()


class Setting(Base):
    __tablename__ = "setting"

    id = Column(Integer, primary_key=True, autoincrement=True)
    isLocal = Column(Boolean, nullable=True, default=None)
    isApi = Column(Boolean, nullable=True, default=None)
    domainName = Column(String, nullable=True, default=None)
    apiKey = Column(String, nullable=True, default=None)
    modelName = Column(String, nullable=True, default=None)
    temperature = Column(Float, nullable=True, default=0.7)
    systemPrompt = Column(Text, nullable=True, default=None)

    users = relationship("UserAccount", back_populates="setting")

class UserAccount(Base):
    __tablename__ = "useraccount"
    username = Column(String, primary_key=True, index=True)
    password = Column(String, nullable=False)
    setting_id = Column(Integer, ForeignKey("setting.id"))
    setting = relationship("Setting", back_populates="users")
    domainName = Column(String, nullable=True)
    documents = relationship("Document", back_populates="user")

class Document(Base):
    __tablename__ = "document"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, ForeignKey("useraccount.username"))
    fileName = Column(String, nullable=False)
    filePath = Column(Text, nullable=False)
    user = relationship("UserAccount", back_populates="documents")

class ChatRoom(Base):
    __tablename__ = "chatroom"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    roomName = Column(String, unique=True, nullable=False)
    username = Column(String, ForeignKey("useraccount.username"), nullable=False)
    conversations = relationship("Conversation", back_populates="chatroom")

class Conversation(Base):
    __tablename__ = "conversation"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chatRoom_id = Column(UUID(as_uuid=True), ForeignKey("chatroom.id"))
    query = Column(Text, nullable=False)
    responseMessage = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)  # ⏳ new field

    chatroom = relationship("ChatRoom", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "message"
    conversation_id = Column(Integer, ForeignKey("conversation.id"), primary_key=True)
    senderUsername = Column(String, ForeignKey("useraccount.username"), primary_key=True)
    rating = Column(Integer, nullable=True)

    conversation = relationship("Conversation", back_populates="messages")
    user = relationship("UserAccount")
