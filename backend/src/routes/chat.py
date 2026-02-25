"""
Chat API Routes for Todo AI Chatbot.

This module implements the stateless POST /api/v1/chat/message endpoint
with JWT authentication and conversation persistence.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Header, Request
from fastapi.responses import JSONResponse
from sqlmodel import Session, select, func
from typing import Optional, List
from datetime import datetime, timedelta
from uuid import UUID, uuid4
import logging

from ..database.session import get_session
from ..models.chat import (
    Conversation, ConversationCreate, ConversationRead,
    Message, MessageCreate, MessageRead, MessageRole,
    PendingAction, PendingActionCreate, ConfirmationType
)
from ..schemas.chat import (
    ChatMessageRequest, ChatMessageResponse, ChatResponseData,
    ChatConfirmRequest, ChatConfirmResponse, ChatErrorResponse,
    ListSessionsResponse, SessionInfo, GetMessagesResponse,
    MessageHistoryItem, DeleteSessionResponse, ToolResultResponse
)
from ..agent.mcp_service import get_mcp_tool_service, MCPTaskService, MCPToolError
from ..agent.chat_agent import create_todo_agent, TodoAgent, ChatContext
from ..utils.jwt import verify_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chatbot"])


# ============================================================
# Helper Functions
# ============================================================


def get_user_id_from_token(authorization: str) -> UUID:
    """Extract and verify user ID from JWT token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization[len("Bearer "):]

    try:
        payload = verify_token(token)
        user_id = payload.get("sub") or payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return UUID(user_id) if isinstance(user_id, str) else user_id
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_or_create_session(
    session: Session,
    user_id: UUID,
    session_id: Optional[str] = None
) -> Conversation:
    """Get existing session or create a new one."""
    if session_id:
        # Try to find existing session
        conversation = session.exec(
            select(Conversation).where(
                Conversation.session_id == session_id,
                Conversation.user_id == user_id
            )
        ).first()

        if conversation:
            return conversation

    # Create new session
    new_session_id = session_id or str(uuid4())
    conversation = Conversation(
        user_id=user_id,
        session_id=new_session_id,
        title="New Chat",
        is_active=True
    )

    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    return conversation


def save_message(
    session: Session,
    conversation_id: UUID,
    role: MessageRole,
    content: str,
    intent: Optional[str] = None,
    entities: Optional[dict] = None,
    tool_calls: Optional[List[dict]] = None,
    tool_results: Optional[List[dict]] = None,
    requires_confirmation: bool = False,
    pending_action: Optional[dict] = None
) -> Message:
    """Save a message to the database."""
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        intent=intent,
        entities=entities,
        tool_calls=tool_calls,
        tool_results=tool_results,
        requires_confirmation=requires_confirmation,
        pending_action=pending_action
    )

    session.add(message)

    # Update conversation's last_message_at
    conversation = session.get(Conversation, conversation_id)
    if conversation:
        conversation.last_message_at = datetime.utcnow()
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)

    session.commit()
    session.refresh(message)

    return message


def format_tool_results(tool_results: List[dict]) -> List[ToolResultResponse]:
    """Format tool results for response."""
    formatted = []
    for result in tool_results or []:
        formatted.append(ToolResultResponse(
            tool_name=result.get("tool_name", "unknown"),
            success=result.get("success", False),
            data=result.get("data")
        ))
    return formatted


# ============================================================
# Chat Endpoints
# ============================================================


@router.post("/message", response_model=ChatMessageResponse)
async def chat_message(
    request: ChatMessageRequest,
    authorization: str = Header(..., description="JWT token"),
    session: Session = Depends(get_session)
):
    """
    Send a message to the Todo AI Chatbot.

    This endpoint processes user messages, executes AI agent operations,
    and persists conversation history.
    """
    try:
        # Authenticate user
        user_id = get_user_id_from_token(authorization)

        # Get or create conversation session
        conversation = get_or_create_session(session, user_id, request.session_id)

        # Save user message
        user_message = save_message(
            session=session,
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=request.content
        )

        # Create agent context
        context = ChatContext(
            user_id=str(user_id),
            conversation_id=str(conversation.id)
        )

        # Create MCP service and agent
        mcp_service = get_mcp_tool_service(session)
        agent = create_todo_agent(mcp_service)

        # Get conversation history for context (last 10 messages)
        history_messages = session.exec(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .where(Message.id != user_message.id)
            .order_by(Message.created_at.desc())
            .limit(10)
        ).all()

        # Format history for agent
        conversation_history = [
            {"role": msg.role.value, "content": msg.content}
            for msg in reversed(history_messages)
        ]

        # Process message with agent
        agent_result = await agent.process_message(
            user_message=request.content,
            conversation_history=conversation_history,
            context=context
        )

        # Check for agent errors
        if agent_result.get("error"):
            logger.error(f"Agent error: {agent_result['error']}")
            assistant_content = agent_result.get("content", "I encountered an error processing your request.")
        else:
            assistant_content = agent_result.get("content", "")

        # Save assistant response
        assistant_message = save_message(
            session=session,
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=assistant_content,
            intent=agent_result.get("intent"),
            entities=agent_result.get("entities"),
            tool_results=agent_result.get("tool_results"),
            requires_confirmation=agent_result.get("requires_confirmation", False),
            pending_action={
                "action_id": agent_result.get("pending_action_id")
            } if agent_result.get("pending_action_id") else None
        )

        # Build response
        response = ChatMessageResponse(
            success=True,
            message_id=str(assistant_message.id),
            conversation_id=str(conversation.id),
            session_id=conversation.session_id,
            response=ChatResponseData(
                content=assistant_content,
                intent=agent_result.get("intent", "general"),
                entities=agent_result.get("entities")
            ),
            tool_results=format_tool_results(agent_result.get("tool_results")),
            requires_confirmation=agent_result.get("requires_confirmation", False),
            confirmation_prompt=agent_result.get("confirmation_prompt"),
            pending_action_id=agent_result.get("pending_action_id"),
            created_at=assistant_message.created_at
        )

        return response

    except HTTPException:
        raise
    except MCPToolError as e:
        logger.error(f"MCP tool error: {e.code} - {e.message}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ChatErrorResponse(
                success=False,
                error={"code": e.code, "message": e.message, "details": e.details},
                created_at=datetime.utcnow()
            ).model_dump()
        )
    except Exception as e:
        logger.error(f"Chat message error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ChatErrorResponse(
                success=False,
                error={"code": "AGENT_ERROR", "message": "Failed to process message. Please try again."},
                created_at=datetime.utcnow()
            ).model_dump()
        )


@router.post("/confirm", response_model=ChatConfirmResponse)
async def confirm_action(
    request: ChatConfirmRequest,
    authorization: str = Header(..., description="JWT token"),
    session: Session = Depends(get_session)
):
    """
    Confirm or reject a pending action that requires confirmation.
    """
    try:
        # Authenticate user
        user_id = get_user_id_from_token(authorization)

        # Get conversation session
        conversation = session.exec(
            select(Conversation).where(
                Conversation.session_id == request.session_id,
                Conversation.user_id == user_id
            )
        ).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        # Create MCP service
        mcp_service = get_mcp_tool_service(session)

        # Process confirmation
        context = {"user_id": str(user_id), "conversation_id": str(conversation.id)}

        try:
            result = await mcp_service.confirm_action(
                action_id=request.action_id,
                confirmed=request.confirmed,
                modifications=request.modifications,
                context=context
            )

            # Determine response content
            if request.confirmed:
                content = "Action completed successfully."
                intent = "action_completed"
            else:
                content = "Action cancelled. No changes were made."
                intent = "action_cancelled"

            # Save assistant response
            assistant_message = save_message(
                session=session,
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT,
                content=content,
                intent=intent
            )

            # Build response
            response = ChatConfirmResponse(
                success=True,
                message_id=str(assistant_message.id),
                response=ChatResponseData(
                    content=content,
                    intent=intent
                ),
                tool_results=format_tool_results([result.data] if result.data else []),
                action_status="completed" if request.confirmed else "rejected",
                created_at=assistant_message.created_at
            )

            return response

        except MCPToolError as e:
            logger.error(f"Confirmation error: {e.code} - {e.message}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=ChatErrorResponse(
                    success=False,
                    error={"code": e.code, "message": e.message, "details": e.details},
                    created_at=datetime.utcnow()
                ).model_dump()
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Confirm action error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ChatErrorResponse(
                success=False,
                error={"code": "DATABASE_ERROR", "message": "Failed to process confirmation."},
                created_at=datetime.utcnow()
            ).model_dump()
        )


@router.get("/sessions", response_model=ListSessionsResponse)
async def list_sessions(
    limit: int = 20,
    offset: int = 0,
    include_inactive: bool = False,
    authorization: str = Header(..., description="JWT token"),
    session: Session = Depends(get_session)
):
    """
    List all active chat sessions for the authenticated user.
    """
    try:
        # Authenticate user
        user_id = get_user_id_from_token(authorization)

        # Build query
        query = select(Conversation).where(Conversation.user_id == user_id)

        if not include_inactive:
            query = query.where(Conversation.is_active == True)

        # Get total count
        count_query = select(func.count()).select_from(Conversation).where(Conversation.user_id == user_id)
        if not include_inactive:
            count_query = count_query.where(Conversation.is_active == True)
        total = session.exec(count_query).one()

        # Apply pagination
        query = query.order_by(Conversation.last_message_at.desc()).offset(offset).limit(limit)
        conversations = session.exec(query).all()

        # Format response
        sessions_list = []
        for conv in conversations:
            # Get message count
            msg_count = session.exec(
                select(func.count()).select_from(Message).where(Message.conversation_id == conv.id)
            ).one()

            sessions_list.append(SessionInfo(
                session_id=conv.session_id,
                title=conv.title,
                last_message_at=conv.last_message_at,
                message_count=msg_count,
                is_active=conv.is_active
            ))

        return ListSessionsResponse(
            success=True,
            sessions=sessions_list,
            total=total,
            has_more=offset + len(conversations) < total
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List sessions error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ChatErrorResponse(
                success=False,
                error={"code": "DATABASE_ERROR", "message": "Failed to list sessions."},
                created_at=datetime.utcnow()
            ).model_dump()
        )


@router.delete("/sessions/{session_id}", response_model=DeleteSessionResponse)
async def delete_session(
    session_id: str,
    authorization: str = Header(..., description="JWT token"),
    db_session: Session = Depends(get_session)
):
    """
    Delete a chat session and all associated messages.
    """
    try:
        # Authenticate user
        user_id = get_user_id_from_token(authorization)

        # Find conversation
        conversation = db_session.exec(
            select(Conversation).where(
                Conversation.session_id == session_id,
                Conversation.user_id == user_id
            )
        ).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        # Delete messages first (cascade)
        messages = db_session.exec(
            select(Message).where(Message.conversation_id == conversation.id)
        ).all()

        for message in messages:
            db_session.delete(message)

        # Delete conversation
        db_session.delete(conversation)
        db_session.commit()

        return DeleteSessionResponse(
            success=True,
            message="Session deleted successfully",
            session_id=session_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete session error: {str(e)}", exc_info=True)
        db_session.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ChatErrorResponse(
                success=False,
                error={"code": "DATABASE_ERROR", "message": "Failed to delete session."},
                created_at=datetime.utcnow()
            ).model_dump()
        )


@router.get("/sessions/{session_id}/messages", response_model=GetMessagesResponse)
async def get_session_messages(
    session_id: str,
    limit: int = 50,
    before: Optional[datetime] = None,
    authorization: str = Header(..., description="JWT token"),
    session: Session = Depends(get_session)
):
    """
    Retrieve message history for a specific session.
    """
    try:
        # Authenticate user
        user_id = get_user_id_from_token(authorization)

        # Find conversation
        conversation = session.exec(
            select(Conversation).where(
                Conversation.session_id == session_id,
                Conversation.user_id == user_id
            )
        ).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        # Build query
        query = select(Message).where(Message.conversation_id == conversation.id)

        if before:
            query = query.where(Message.created_at < before)

        # Get total count
        count_query = select(func.count()).select_from(Message).where(Message.conversation_id == conversation.id)
        if before:
            count_query = count_query.where(Message.created_at < before)
        total = session.exec(count_query).one()

        # Apply pagination and ordering
        query = query.order_by(Message.created_at.desc()).limit(limit)
        messages = session.exec(query).all()

        # Format response (reverse to get chronological order)
        messages_list = [
            MessageHistoryItem(
                id=str(msg.id),
                role=msg.role.value,
                content=msg.content,
                intent=msg.intent,
                entities=msg.entities,
                tool_results=msg.tool_results,
                created_at=msg.created_at
            )
            for msg in reversed(messages)
        ]

        return GetMessagesResponse(
            success=True,
            messages=messages_list,
            has_more=len(messages_list) < total
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get messages error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ChatErrorResponse(
                success=False,
                error={"code": "DATABASE_ERROR", "message": "Failed to retrieve messages."},
                created_at=datetime.utcnow()
            ).model_dump()
        )
