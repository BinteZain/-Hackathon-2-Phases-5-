from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid


class AgentTaskStatus(str, Enum):
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    WAITING_CONFIRMATION = "waiting_confirmation"
    WAITING_CLARIFICATION = "waiting_clarification"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ToolExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class ConfirmationType(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    MODIFY = "modify"
    SKIP = "skip"


class AgentTaskBase(SQLModel):
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    title: str = Field(min_length=1, max_length=500)
    description: Optional[str] = Field(default=None, max_length=5000)
    status: AgentTaskStatus = Field(default=AgentTaskStatus.PENDING)
    priority: str = Field(default="medium")
    plan: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    context: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    follow_up_count: int = Field(default=0)
    requires_confirmation: bool = Field(default=False)
    requires_clarification: bool = Field(default=False)
    clarification_question: Optional[str] = Field(default=None, max_length=1000)


class AgentTask(AgentTaskBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)
    started_at: Optional[datetime] = Field(default=None)

    tool_executions: Optional[List["ToolExecution"]] = Relationship(back_populates="agent_task")
    conversation_history: Optional[List["ConversationTurn"]] = Relationship(back_populates="agent_task")


class AgentTaskCreate(AgentTaskBase):
    pass


class AgentTaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=500)
    description: Optional[str] = Field(default=None, max_length=5000)
    status: Optional[AgentTaskStatus] = Field(default=None)
    priority: Optional[str] = Field(default=None)
    plan: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    context: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    requires_confirmation: Optional[bool] = Field(default=None)
    requires_clarification: Optional[bool] = Field(default=None)
    clarification_question: Optional[str] = Field(default=None, max_length=1000)


class AgentTaskRead(AgentTaskBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    started_at: Optional[datetime]


class ToolExecutionBase(SQLModel):
    agent_task_id: uuid.UUID = Field(foreign_key="agenttask.id", nullable=False)
    tool_name: str = Field(min_length=1, max_length=100)
    tool_type: str = Field(default="mcp")
    input_data: Dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
    output_data: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    error_message: Optional[str] = Field(default=None, max_length=2000)
    status: ToolExecutionStatus = Field(default=ToolExecutionStatus.PENDING)
    step_number: int = Field(default=0)
    requires_confirmation: bool = Field(default=False)
    confirmation_status: Optional[ConfirmationType] = Field(default=None)


class ToolExecution(ToolExecutionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)

    agent_task: Optional[AgentTask] = Relationship(back_populates="tool_executions")


class ToolExecutionCreate(ToolExecutionBase):
    pass


class ToolExecutionRead(ToolExecutionBase):
    id: uuid.UUID
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


class ConversationTurnBase(SQLModel):
    agent_task_id: uuid.UUID = Field(foreign_key="agenttask.id", nullable=False)
    turn_number: int = Field(default=0)
    role: str = Field(min_length=1, max_length=20)
    content: str = Field(min_length=1, max_length=10000)
    intent: Optional[str] = Field(default=None, max_length=200)
    entities: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    is_follow_up: bool = Field(default=False)


class ConversationTurn(ConversationTurnBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    agent_task: Optional[AgentTask] = Relationship(back_populates="conversation_history")


class ConversationTurnCreate(ConversationTurnBase):
    pass


class ConversationTurnRead(ConversationTurnBase):
    id: uuid.UUID
    created_at: datetime


class AgentSessionBase(SQLModel):
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    session_id: str = Field(unique=True, max_length=100)
    context: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    is_active: bool = Field(default=True)


class AgentSession(AgentSessionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity_at: datetime = Field(default_factory=datetime.utcnow)


class AgentSessionCreate(AgentSessionBase):
    pass


class AgentSessionRead(AgentSessionBase):
    id: uuid.UUID
    created_at: datetime
    last_activity_at: datetime
