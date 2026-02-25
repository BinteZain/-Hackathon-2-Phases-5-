from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import JSON, Column, Index
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConfirmationType(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    MODIFY = "modify"
    SKIP = "skip"


class ConversationBase(SQLModel):
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    session_id: str = Field(max_length=100, unique=True)
    title: Optional[str] = Field(default=None, max_length=255)
    is_active: bool = Field(default=True)


class Conversation(ConversationBase, table=True):
    __tablename__ = "conversations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_message_at: Optional[datetime] = Field(default=None)

    # Relationships
    messages: Optional[List["Message"]] = Relationship(back_populates="conversation")

    __table_args__ = (
        Index("ix_conversations_user_id", "user_id"),
        Index("ix_conversations_session_id", "session_id"),
        Index("ix_conversations_user_created", "user_id", "created_at"),
    )


class ConversationCreate(SQLModel):
    user_id: uuid.UUID
    session_id: str
    title: Optional[str] = None


class ConversationRead(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    session_id: str
    title: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime]
    message_count: Optional[int] = None


class MessageBase(SQLModel):
    role: MessageRole = Field(default=MessageRole.USER)
    content: str = Field(min_length=1, max_length=10000)

    # Agent metadata
    intent: Optional[str] = Field(default=None, max_length=200)
    entities: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    tool_calls: Optional[List[Dict[str, Any]]] = Field(default=None, sa_type=JSON)
    tool_results: Optional[List[Dict[str, Any]]] = Field(default=None, sa_type=JSON)

    # Confirmation tracking
    requires_confirmation: bool = Field(default=False)
    confirmation_status: Optional[ConfirmationType] = Field(default=None)
    pending_action: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)


class Message(MessageBase, table=True):
    __tablename__ = "messages"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversations.id", nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: Optional[Conversation] = Relationship(back_populates="messages")

    __table_args__ = (
        Index("ix_messages_conversation_id", "conversation_id"),
        Index("ix_messages_created_at", "created_at"),
        Index("ix_messages_user_conversation", "conversation_id", "created_at"),
    )


class MessageCreate(MessageBase):
    conversation_id: uuid.UUID


class MessageRead(MessageBase):
    id: uuid.UUID
    conversation_id: uuid.UUID
    created_at: datetime


class PendingActionBase(SQLModel):
    conversation_id: uuid.UUID = Field(foreign_key="conversations.id", nullable=False)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    tool_name: str = Field(max_length=100)
    action_params: Dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
    confirmation_prompt: str = Field(max_length=1000)
    is_resolved: bool = Field(default=False)
    resolved_at: Optional[datetime] = Field(default=None)
    resolved_value: Optional[ConfirmationType] = Field(default=None)


class PendingAction(PendingActionBase, table=True):
    __tablename__ = "pending_actions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow())

    __table_args__ = (
        Index("ix_pending_actions_conversation_id", "conversation_id"),
        Index("ix_pending_actions_user_id", "user_id"),
        Index("ix_pending_actions_is_resolved", "is_resolved"),
    )


class PendingActionCreate(PendingActionBase):
    pass


class PendingActionRead(PendingActionBase):
    id: uuid.UUID
    created_at: datetime
    expires_at: datetime
