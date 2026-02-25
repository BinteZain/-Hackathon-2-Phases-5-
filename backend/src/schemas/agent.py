from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from enum import Enum


class AgentTaskStatusEnum(str, Enum):
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    WAITING_CONFIRMATION = "waiting_confirmation"
    WAITING_CLARIFICATION = "waiting_clarification"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class UserInputRequest(BaseModel):
    input: str = Field(min_length=1, max_length=5000, description="User's natural language input")
    session_id: Optional[str] = None


class FollowUpRequest(BaseModel):
    response: str = Field(min_length=1, max_length=1000, description="User's follow-up response (yes/no/ok/etc)")


class ConfirmationRequest(BaseModel):
    confirmed: bool
    task_id: str
    modifications: Optional[Dict[str, Any]] = None


class ClarificationRequest(BaseModel):
    task_id: str
    answers: List[str] = Field(default_factory=list)
    clarifications: Dict[str, Any] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    response: Optional[str] = None
    requires_confirmation: bool = False
    confirmation_prompt: Optional[str] = None
    requires_clarification: bool = False
    clarification_question: Optional[str] = None
    ambiguities: List[Dict[str, Any]] = Field(default_factory=list)
    task_id: Optional[str] = None
    intent: Optional[str] = None
    entities: Dict[str, Any] = Field(default_factory=dict)
    reasoning_chain: Optional[Dict[str, Any]] = None
    tool_results: List[Dict[str, Any]] = Field(default_factory=list)
    cancelled: bool = False


class AgentTaskResponse(BaseModel):
    success: bool
    task: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class AgentTaskListResponse(BaseModel):
    success: bool
    tasks: List[Dict[str, Any]] = Field(default_factory=list)
    message: Optional[str] = None


class ReasoningStepSchema(BaseModel):
    step_number: int
    action: str
    tool_name: str
    tool_params: Dict[str, Any]
    description: str
    requires_confirmation: bool = False
    depends_on: List[int] = Field(default_factory=list)


class ReasoningChainSchema(BaseModel):
    intent: Dict[str, Any]
    steps: List[ReasoningStepSchema] = Field(default_factory=list)
    total_steps: int = 0
    estimated_time_seconds: int = 0
    risk_level: str = "low"


class ToolExecutionSchema(BaseModel):
    id: str
    tool_name: str
    status: str
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class AgentTaskDetailSchema(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    status: str
    plan: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None
    tool_executions: List[ToolExecutionSchema] = Field(default_factory=list)


class ApiResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
