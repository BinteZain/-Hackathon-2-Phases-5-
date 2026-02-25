from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Optional, List
from ..database.session import get_session
from ..utils.jwt import get_current_user, TokenData
from ..schemas.agent import (
    UserInputRequest, FollowUpRequest, ConfirmationRequest, ClarificationRequest,
    AgentResponse, AgentTaskResponse, AgentTaskListResponse, ApiResponse
)
from ..agent.service import AgentService
from ..models.agent import AgentTaskStatus
import uuid

router = APIRouter(prefix="/agent", tags=["agent"])

_agent_service: Optional[AgentService] = None


def get_agent_service():
    global _agent_service
    if _agent_service is None:
        from ..database.session import engine
        from sqlmodel import Session as SQLModelSession
        from contextlib import contextmanager
        
        @contextmanager
        def session_factory():
            session = SQLModelSession(bind=engine)
            try:
                yield session
            finally:
                session.close()
        
        _agent_service = AgentService(session_factory, get_session)
    return _agent_service


@router.post("/chat", response_model=AgentResponse)
async def agent_chat(
    request: UserInputRequest,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Process natural language input and execute agent tasks.
    Supports multi-step reasoning, follow-up responses, and ambiguity resolution.
    """
    try:
        agent_service = get_agent_service()
        
        result = await agent_service.process_user_input(
            user_id=current_user.user_id,
            user_input=request.input,
            session_id=request.session_id
        )
        
        return AgentResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent processing error: {str(e)}"
        )


@router.post("/followup", response_model=AgentResponse)
async def agent_followup(
    request: FollowUpRequest,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Handle follow-up responses (yes/no/ok/do it) to pending confirmations or clarifications.
    """
    try:
        agent_service = get_agent_service()
        
        result = await agent_service.handle_follow_up(
            user_id=current_user.user_id,
            follow_up_input=request.response
        )
        
        return AgentResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Follow-up processing error: {str(e)}"
        )


@router.post("/confirm", response_model=AgentResponse)
async def agent_confirm(
    request: ConfirmationRequest,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Explicitly confirm or reject a pending agent operation.
    """
    try:
        agent_service = get_agent_service()
        
        if not request.confirmed:
            result = await agent_service.handle_follow_up(
                user_id=current_user.user_id,
                follow_up_input="no"
            )
            return AgentResponse(**result)
        
        pending = agent_service.context_manager.get_pending_confirmation(current_user.user_id)
        if not pending:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No pending confirmation found"
            )
        
        chain_data = pending.get("chain", {})
        from ..agent.reasoning_engine import ReasoningChain
        chain = ReasoningChain(**chain_data)
        
        context = agent_service.context_manager.get_context(current_user.user_id)
        result = await agent_service._execute_reasoning_chain(
            user_id=current_user.user_id,
            chain=chain,
            context=context
        )
        
        agent_service.context_manager.clear_pending_confirmation(current_user.user_id)
        
        return AgentResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Confirmation processing error: {str(e)}"
        )


@router.post("/clarify", response_model=AgentResponse)
async def agent_clarify(
    request: ClarificationRequest,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Provide clarifications for ambiguous agent requests.
    """
    try:
        agent_service = get_agent_service()
        
        context = agent_service.context_manager.get_context(current_user.user_id)
        if not context:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No conversation context found"
            )
        
        conversation_history = agent_service.context_manager.get_conversation_history(
            current_user.user_id, limit=5
        )
        
        last_assistant_turn = None
        for turn in reversed(conversation_history):
            if turn.get("role") == "assistant" and turn.get("intent"):
                last_assistant_turn = turn
                break
        
        if not last_assistant_turn:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No clarification request found in conversation history"
            )
        
        clarified_input = " ".join(request.answers) if request.answers else str(request.clarifications)
        
        result = await agent_service.process_user_input(
            user_id=current_user.user_id,
            user_input=clarified_input,
            session_id=request.task_id
        )
        
        return AgentResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Clarification processing error: {str(e)}"
        )


@router.get("/tasks", response_model=AgentTaskListResponse)
async def list_agent_tasks(
    status_filter: Optional[AgentTaskStatus] = None,
    limit: int = 20,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    List agent tasks for the authenticated user.
    """
    try:
        agent_service = get_agent_service()
        
        tasks = await agent_service.list_agent_tasks(
            user_id=current_user.user_id,
            status=status_filter,
            limit=limit
        )
        
        return AgentTaskListResponse(
            success=True,
            tasks=tasks,
            message=f"Retrieved {len(tasks)} agent tasks"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing agent tasks: {str(e)}"
        )


@router.get("/tasks/{task_id}", response_model=AgentTaskResponse)
async def get_agent_task(
    task_id: str,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get details of a specific agent task including tool executions.
    """
    try:
        agent_service = get_agent_service()
        
        task = await agent_service.get_agent_task(
            user_id=current_user.user_id,
            task_id=task_id
        )
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent task not found"
            )
        
        return AgentTaskResponse(
            success=True,
            task=task,
            message="Agent task retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving agent task: {str(e)}"
        )


@router.get("/tools", response_model=ApiResponse)
async def list_available_tools(
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    List available MCP tools for the agent.
    """
    try:
        from ..agent.mcp_tools import MCPToolRegistry
        
        registry = MCPToolRegistry()
        tools = registry.list_tools()
        
        return ApiResponse(
            success=True,
            data={
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "category": tool.category,
                        "parameters": [
                            {
                                "name": p.name,
                                "type": p.type,
                                "description": p.description,
                                "required": p.required,
                                "enum": p.enum
                            }
                            for p in tool.parameters
                        ],
                        "requires_confirmation": tool.requires_confirmation
                    }
                    for tool in tools
                ]
            },
            message="Available tools retrieved successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing tools: {str(e)}"
        )
