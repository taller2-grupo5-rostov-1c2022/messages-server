from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy import Table

from src.postgres.database import Base


class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(String, ForeignKey("users.id"))
    receiver_id = Column(String, ForeignKey("users.id"))
    text = Column(String)
    created_at = Column(TIMESTAMP)
    read = Column(Boolean)

    sender = relationship(
        "UserModel", foreign_keys=[sender_id], back_populates="messages_sent"
    )
    receiver = relationship(
        "UserModel", foreign_keys=[receiver_id], back_populates="messages_received"
    )


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)

    # define relationship between UserModel and MessageModel
    messages_sent = relationship(
        "MessageModel", foreign_keys=[MessageModel.sender_id], back_populates="sender"
    )
    messages_received = relationship(
        "MessageModel",
        foreign_keys=[MessageModel.receiver_id],
        back_populates="receiver",
    )
