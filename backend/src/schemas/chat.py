"""
Chat API Schemas for Todo AI Chatbot.

This module defines request/response schemas for the chat API endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# ============================================================
# Request Schemas
# ============================================================


class ChatMessageRequest(BaseModel):
    """Request schema for POST /api/v1/chat/message."""

    content: str = Field(..., min_length=1, max_length=10000, description="User's message content")
    session_id: Optional[str] = Field(default=None, max_length=100, description="Existing session ID for conversation continuity")

    class Config:
        schema_extra = {
            "example": {
                "content": "Add a task to buy groceries tomorrow",
                "session_id": "optional-session-id-uuid"
            }
        }


class ChatConfirmRequest(BaseModel):
    """Request schema for POST /api/v1/chat/confirm."""

    session_id: str = Field(..., max_length=100, description="Session ID from previous response")
    action_id: str = Field(..., description="ID of pending action to confirm")
    confirmed: bool = Field(..., description="Whether user confirms the action")
    modifications: Optional[Dict[str, Any]] = Field(default=None, description="Optional modifications to the action")

    class Config:
        schema_extra = {
            "example": {
                "session_id": "session-id-uuid",
                "action_id": "pending-action-uuid",
                "confirmed": True,
                "modifications": None
            }
        }


# ============================================================
# Response Schemas
# ============================================================


class ToolResultResponse(BaseModel):
    """Schema for tool execution results in responses."""

    tool_name: str
    success: bool
    data: Optional[Dict[str, Any]] = None


class ChatResponseData(BaseModel):
    """Schema for chat response content."""

    content: str
    intent: str
    entities: Optional[Dict[str, Any]] = None


class ChatMessageResponse(BaseModel):
    """Response schema for chat message endpoint."""

    success: bool
    message_id: str
    conversation_id: str
    session_id: str
    response: ChatResponseData
    tool_results: Optional[List[ToolResultResponse]] = None
    requires_confirmation: bool = False
    confirmation_prompt: Optional[str] = None
    pending_action_id: Optional[str] = None
    created_at: datetime

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message_id": "uuid",
                "conversation_id": "uuid",
                "session_id": "uuid",
                "response": {
                    "content": "I've added 'Buy groceries' to your todo list for tomorrow.",
                    "intent": "create_task",
                    "entities": {"title": "Buy groceries", "due_date": "2026-02-18"}
                },
                "tool_results": [
                    {"tool_name": "add_task", "success": True, "data": {"task_id": "uuid"}}
                ],
                "requires_confirmation": False,
                "created_at": "2026-02-17T10:30:00Z"
            }
        }


class ChatConfirmResponse(BaseModel):
    """Response schema for chat confirm endpoint."""

    success: bool
    message_id: str
    response: ChatResponseData
    tool_results: Optional[List[ToolResultResponse]] = None
    action_status: Optional[str] = None  # "completed" or "rejected"
    created_at: datetime


class SessionInfo(BaseModel):
    """Schema for chat session information."""

    session_id: str
    title: Optional[str]
    last_message_at: Optional[datetime]
    message_count: int
    is_active: bool


class ListSessionsResponse(BaseModel):
    """Response schema for listing chat sessions."""

    success: bool
    sessions: List[SessionInfo]
    total: int
    has_more: bool


class MessageHistoryItem(BaseModel):
    """Schema for a single message in history."""

    id: str
    role: str  # "user" or "assistant"
    content: str
    intent: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None
    tool_results: Optional[List[Dict[str, Any]]] = None
    created_at: datetime


class GetMessagesResponse(BaseModel):
    """Response schema for getting message history."""

    success: bool
    messages: List[MessageHistoryItem]
    has_more: bool


class DeleteSessionResponse(BaseModel):
    """Response schema for deleting a session."""

    success: bool
    message: str
    session_id: str


# ============================================================
# Error Response Schemas
# ============================================================


class ErrorDetail(BaseModel):
    """Schema for error details."""

    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ChatErrorResponse(BaseModel):
    """Response schema for chat errors."""

    success: bool = False
    error: ErrorDetail
    created_at: datetime

    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Content is required and cannot be empty",
                    "details": {"field": "content", "issue": "min_length"}
                },
                "created_at": "2026-02-17T10:30:00Z"
            }
        }


# ============================================================
# Internal Schemas
# ============================================================


class AgentProcessResult(BaseModel):
    """Internal schema for agent processing results."""

    content: str
    intent: str
    entities: Optional[Dict[str, Any]] = None
    tool_results: Optional[List[Dict[str, Any]]] = None
    requires_confirmation: bool = False
    pending_action_id: Optional[str] = None
    error: Optional[str] = None
