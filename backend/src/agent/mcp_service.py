"""
MCP Tools Service for Todo AI Chatbot.

This module implements the official MCP (Model Context Protocol) SDK server
with OpenAI Agents SDK integration for task management operations.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Session, select
from uuid import UUID
import logging

from ..models.task import Task, TaskUpdate
from ..models.chat import PendingAction, PendingActionCreate, ConfirmationType

logger = logging.getLogger(__name__)


class MCPToolError(Exception):
    """Base exception for MCP tool errors."""

    def __init__(self, code: str, message: str, details: Optional[Dict[str, Any]] = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ToolResponse(SQLModel):
    """Standard response envelope for all MCP tool operations."""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    requires_confirmation: bool = False
    confirmation_prompt: Optional[str] = None
    pending_action_id: Optional[UUID] = None


def _serialize_datetime(obj: Any) -> Any:
    """Serialize datetime objects to ISO format strings."""
    if isinstance(obj, datetime):
        return obj.isoformat() + "Z"
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: _serialize_datetime(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize_datetime(item) for item in obj]
    return obj


def _task_to_dict(task: Task) -> Dict[str, Any]:
    """Convert a Task model to a dictionary with proper serialization."""
    task_dict = task.model_dump()
    return _serialize_datetime(task_dict)


class MCPTaskService:
    """
    MCP-compliant task management service.

    All tools enforce strict user isolation and stateless execution.
    """

    def __init__(self, session: Session):
        self.session = session

    async def add_task(
        self,
        title: str,
        description: Optional[str] = None,
        priority: str = "medium",
        due_date: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ToolResponse:
        """
        Create a new task for the authenticated user.

        User Isolation: Task is created with user_id from JWT context.
        """
        try:
            if not context or "user_id" not in context:
                raise MCPToolError(
                    code="UNAUTHORIZED",
                    message="Authentication context required"
                )

            user_id = UUID(context["user_id"]) if isinstance(context["user_id"], str) else context["user_id"]

            # Validate parameters
            if not title or len(title) > 255:
                raise MCPToolError(
                    code="VALIDATION_ERROR",
                    message="Parameter 'title' is required and must be 1-255 characters"
                )

            if description and len(description) > 500:
                raise MCPToolError(
                    code="VALIDATION_ERROR",
                    message="Parameter 'description' exceeds maximum length of 500 characters"
                )

            valid_priorities = ["low", "medium", "high", "urgent"]
            if priority not in valid_priorities:
                raise MCPToolError(
                    code="VALIDATION_ERROR",
                    message=f"Parameter 'priority' must be one of: {valid_priorities}"
                )

            # Parse due_date if provided
            parsed_due_date = None
            if due_date:
                try:
                    parsed_due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                except ValueError:
                    raise MCPToolError(
                        code="VALIDATION_ERROR",
                        message="Parameter 'due_date' must be a valid ISO 8601 datetime string"
                    )

            # Create task with user isolation
            task = Task(
                user_id=user_id,
                title=title,
                description=description,
                priority=priority,
                due_date=parsed_due_date,
                status="pending"
            )

            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)

            logger.info(f"Task created: {task.id} for user {user_id}")

            return ToolResponse(
                success=True,
                data={"task": _task_to_dict(task)}
            )

        except MCPToolError:
            raise
        except Exception as e:
            logger.error(f"Error in add_task: {str(e)}")
            raise MCPToolError(
                code="DATABASE_ERROR",
                message="Failed to create task. Database operation failed."
            )

    async def list_tasks(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        search: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ToolResponse:
        """
        List tasks for the authenticated user with optional filtering.

        User Isolation: Query includes WHERE user_id = context.user_id
        """
        try:
            if not context or "user_id" not in context:
                raise MCPToolError(
                    code="UNAUTHORIZED",
                    message="Authentication context required"
                )

            user_id = UUID(context["user_id"]) if isinstance(context["user_id"], str) else context["user_id"]

            # Validate parameters
            if limit < 1 or limit > 100:
                raise MCPToolError(
                    code="VALIDATION_ERROR",
                    message="Parameter 'limit' must be between 1 and 100"
                )

            if offset < 0:
                raise MCPToolError(
                    code="VALIDATION_ERROR",
                    message="Parameter 'offset' must be >= 0"
                )

            valid_statuses = ["pending", "in_progress", "completed"]
            if status and status not in valid_statuses:
                raise MCPToolError(
                    code="VALIDATION_ERROR",
                    message=f"Parameter 'status' must be one of: {valid_statuses}"
                )

            valid_priorities = ["low", "medium", "high", "urgent"]
            if priority and priority not in valid_priorities:
                raise MCPToolError(
                    code="VALIDATION_ERROR",
                    message=f"Parameter 'priority' must be one of: {valid_priorities}"
                )

            # Build query with user isolation
            query = select(Task).where(Task.user_id == user_id)

            # Apply filters
            if status:
                query = query.where(Task.status == status)
            if priority:
                query = query.where(Task.priority == priority)
            if search:
                from sqlalchemy import or_
                query = query.where(
                    or_(
                        Task.title.ilike(f"%{search}%"),
                        Task.description.ilike(f"%{search}%")
                    )
                )

            # Get total count
            count_query = select(Task.id).where(Task.user_id == user_id)
            if status:
                count_query = count_query.where(Task.status == status)
            if priority:
                count_query = count_query.where(Task.priority == priority)
            total = len(list(self.session.exec(count_query)))

            # Apply pagination
            query = query.offset(offset).limit(limit)
            tasks = self.session.exec(query).all()

            return ToolResponse(
                success=True,
                data={
                    "tasks": [_task_to_dict(task) for task in tasks],
                    "total": total,
                    "has_more": offset + len(tasks) < total,
                    "filters": {
                        k: v for k, v in {
                            "status": status,
                            "priority": priority,
                            "search": search
                        }.items() if v is not None
                    }
                }
            )

        except MCPToolError:
            raise
        except Exception as e:
            logger.error(f"Error in list_tasks: {str(e)}")
            raise MCPToolError(
                code="DATABASE_ERROR",
                message="Failed to retrieve tasks. Database query failed."
            )

    async def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ToolResponse:
        """
        Update an existing task.

        User Isolation: Query includes WHERE user_id = context.user_id AND id = task_id
        """
        try:
            if not context or "user_id" not in context:
                raise MCPToolError(
                    code="UNAUTHORIZED",
                    message="Authentication context required"
                )

            user_id = UUID(context["user_id"]) if isinstance(context["user_id"], str) else context["user_id"]

            # Validate task_id
            try:
                task_uuid = UUID(task_id)
            except ValueError:
                raise MCPToolError(
                    code="VALIDATION_ERROR",
                    message="Parameter 'task_id' must be a valid UUID"
                )

            # Find task with user isolation
            query = select(Task).where(
                Task.id == task_uuid,
                Task.user_id == user_id
            )
            task = self.session.exec(query).first()

            if not task:
                # Check if task exists but belongs to different user
                task_check = self.session.get(Task, task_uuid)
                if task_check:
                    raise MCPToolError(
                        code="FORBIDDEN",
                        message="You do not have permission to modify this task"
                    )
                else:
                    raise MCPToolError(
                        code="NOT_FOUND",
                        message=f"Task not found with ID: {task_id}"
                    )

            # Validate update parameters
            if title is not None and (not title or len(title) > 255):
                raise MCPToolError(
                    code="VALIDATION_ERROR",
                    message="Parameter 'title' must be 1-255 characters"
                )

            if description is not None and len(description) > 500:
                raise MCPToolError(
                    code="VALIDATION_ERROR",
                    message="Parameter 'description' exceeds maximum length of 500 characters"
                )

            valid_statuses = ["pending", "in_progress", "completed"]
            if status is not None and status not in valid_statuses:
                raise MCPToolError(
                    code="VALIDATION_ERROR",
                    message=f"Parameter 'status' must be one of: {valid_statuses}"
                )

            valid_priorities = ["low", "medium", "high", "urgent"]
            if priority is not None and priority not in valid_priorities:
                raise MCPToolError(
                    code="VALIDATION_ERROR",
                    message=f"Parameter 'priority' must be one of: {valid_priorities}"
                )

            # Parse due_date if provided
            parsed_due_date = None
            if due_date:
                try:
                    parsed_due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                except ValueError:
                    raise MCPToolError(
                        code="VALIDATION_ERROR",
                        message="Parameter 'due_date' must be a valid ISO 8601 datetime string"
                    )

            # Update fields (only provided values)
            update_data = {
                k: v for k, v in {
                    "title": title,
                    "description": description,
                    "status": status,
                    "priority": priority,
                    "due_date": parsed_due_date
                }.items() if v is not None
            }

            for field, value in update_data.items():
                setattr(task, field, value)

            task.updated_at = datetime.utcnow()

            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)

            logger.info(f"Task updated: {task.id} for user {user_id}")

            return ToolResponse(
                success=True,
                data={"task": _task_to_dict(task)}
            )

        except MCPToolError:
            raise
        except Exception as e:
            logger.error(f"Error in update_task: {str(e)}")
            raise MCPToolError(
                code="DATABASE_ERROR",
                message="Failed to update task. Database error."
            )

    async def complete_task(
        self,
        task_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ToolResponse:
        """
        Mark a task as completed.

        User Isolation: Query includes WHERE user_id = context.user_id AND id = task_id
        """
        try:
            if not context or "user_id" not in context:
                raise MCPToolError(
                    code="UNAUTHORIZED",
                    message="Authentication context required"
                )

            user_id = UUID(context["user_id"]) if isinstance(context["user_id"], str) else context["user_id"]

            # Validate task_id
            try:
                task_uuid = UUID(task_id)
            except ValueError:
                raise MCPToolError(
                    code="VALIDATION_ERROR",
                    message="Parameter 'task_id' must be a valid UUID"
                )

            # Find task with user isolation
            query = select(Task).where(
                Task.id == task_uuid,
                Task.user_id == user_id
            )
            task = self.session.exec(query).first()

            if not task:
                task_check = self.session.get(Task, task_uuid)
                if task_check:
                    raise MCPToolError(
                        code="FORBIDDEN",
                        message="You do not have permission to modify this task"
                    )
                else:
                    raise MCPToolError(
                        code="NOT_FOUND",
                        message=f"Task not found with ID: {task_id}"
                    )

            # Check if already completed
            if task.status == "completed":
                raise MCPToolError(
                    code="CONFLICT",
                    message="Task is already completed",
                    details={
                        "task_id": str(task.id),
                        "current_status": task.status,
                        "completed_at": task.completed_at.isoformat() if task.completed_at else None
                    }
                )

            # Update status
            now = datetime.utcnow()
            task.status = "completed"
            task.completed_at = now
            task.updated_at = now

            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)

            logger.info(f"Task completed: {task.id} for user {user_id}")

            return ToolResponse(
                success=True,
                data={"task": _task_to_dict(task)}
            )

        except MCPToolError:
            raise
        except Exception as e:
            logger.error(f"Error in complete_task: {str(e)}")
            raise MCPToolError(
                code="DATABASE_ERROR",
                message="Failed to complete task. Database error."
            )

    async def delete_task(
        self,
        task_id: str,
        confirmed: bool = False,
        context: Optional[Dict[str, Any]] = None
    ) -> ToolResponse:
        """
        Delete a task. Requires confirmation for destructive operation.

        User Isolation: Query includes WHERE user_id = context.user_id AND id = task_id
        """
        try:
            if not context or "user_id" not in context:
                raise MCPToolError(
                    code="UNAUTHORIZED",
                    message="Authentication context required"
                )

            user_id = UUID(context["user_id"]) if isinstance(context["user_id"], str) else context["user_id"]

            # Validate task_id
            try:
                task_uuid = UUID(task_id)
            except ValueError:
                raise MCPToolError(
                    code="VALIDATION_ERROR",
                    message="Parameter 'task_id' must be a valid UUID"
                )

            # Find task with user isolation
            query = select(Task).where(
                Task.id == task_uuid,
                Task.user_id == user_id
            )
            task = self.session.exec(query).first()

            if not task:
                task_check = self.session.get(Task, task_uuid)
                if task_check:
                    raise MCPToolError(
                        code="FORBIDDEN",
                        message="You do not have permission to delete this task"
                    )
                else:
                    raise MCPToolError(
                        code="NOT_FOUND",
                        message=f"Task not found with ID: {task_id}"
                    )

            # If not confirmed, create pending action
            if not confirmed:
                pending_action = PendingAction(
                    conversation_id=UUID(context.get("conversation_id", user_id)),
                    user_id=user_id,
                    tool_name="delete_task",
                    action_params={"task_id": task_id},
                    confirmation_prompt=f"Are you sure you want to delete the task '{task.title}'? This action cannot be undone.",
                    expires_at=datetime.utcnow()
                )
                # Set expiry to 24 hours from now
                from datetime import timedelta
                pending_action.expires_at = datetime.utcnow() + timedelta(hours=24)

                self.session.add(pending_action)
                self.session.commit()
                self.session.refresh(pending_action)

                logger.info(f"Pending action created for task deletion: {pending_action.id}")

                return ToolResponse(
                    success=True,
                    requires_confirmation=True,
                    confirmation_prompt=pending_action.confirmation_prompt,
                    pending_action_id=pending_action.id,
                    data={
                        "pending_action": {
                            "tool": "delete_task",
                            "params": {"task_id": task_id},
                            "task_title": task.title
                        }
                    }
                )

            # Delete the task
            self.session.delete(task)
            self.session.commit()

            logger.info(f"Task deleted: {task_id} for user {user_id}")

            return ToolResponse(
                success=True,
                data={
                    "deleted": True,
                    "task_id": task_id
                }
            )

        except MCPToolError:
            raise
        except Exception as e:
            logger.error(f"Error in delete_task: {str(e)}")
            raise MCPToolError(
                code="DATABASE_ERROR",
                message="Failed to delete task. Database error."
            )

    async def confirm_action(
        self,
        action_id: str,
        confirmed: bool,
        modifications: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ToolResponse:
        """
        Confirm or reject a pending action.
        """
        try:
            if not context or "user_id" not in context:
                raise MCPToolError(
                    code="UNAUTHORIZED",
                    message="Authentication context required"
                )

            user_id = UUID(context["user_id"]) if isinstance(context["user_id"], str) else context["user_id"]

            # Validate action_id
            try:
                action_uuid = UUID(action_id)
            except ValueError:
                raise MCPToolError(
                    code="VALIDATION_ERROR",
                    message="Parameter 'action_id' must be a valid UUID"
                )

            # Find pending action with user isolation
            query = select(PendingAction).where(
                PendingAction.id == action_uuid,
                PendingAction.user_id == user_id
            )
            pending_action = self.session.exec(query).first()

            if not pending_action:
                raise MCPToolError(
                    code="NOT_FOUND",
                    message=f"Pending action not found with ID: {action_id}"
                )

            if pending_action.is_resolved:
                raise MCPToolError(
                    code="CONFLICT",
                    message="This action has already been resolved"
                )

            # Check expiry
            if datetime.utcnow() > pending_action.expires_at:
                raise MCPToolError(
                    code="CONFLICT",
                    message="This confirmation has expired"
                )

            if not confirmed:
                # Reject the action
                pending_action.is_resolved = True
                pending_action.resolved_at = datetime.utcnow()
                pending_action.resolved_value = ConfirmationType.REJECT
                self.session.add(pending_action)
                self.session.commit()

                return ToolResponse(
                    success=True,
                    data={
                        "action_status": "rejected",
                        "action_id": action_id
                    }
                )

            # Execute the confirmed action
            if pending_action.tool_name == "delete_task":
                task_id = pending_action.action_params.get("task_id")
                if task_id:
                    # Apply modifications if any
                    if modifications:
                        await self.update_task(
                            task_id=task_id,
                            context=context,
                            **modifications
                        )

                    # Now delete
                    result = await self.delete_task(
                        task_id=task_id,
                        confirmed=True,
                        context=context
                    )
                    result.data["action_id"] = action_id
                    return result

            # Mark as resolved
            pending_action.is_resolved = True
            pending_action.resolved_at = datetime.utcnow()
            pending_action.resolved_value = ConfirmationType.APPROVE
            self.session.add(pending_action)
            self.session.commit()

            return ToolResponse(
                success=True,
                data={
                    "action_status": "completed",
                    "action_id": action_id
                }
            )

        except MCPToolError:
            raise
        except Exception as e:
            logger.error(f"Error in confirm_action: {str(e)}")
            raise MCPToolError(
                code="DATABASE_ERROR",
                message="Failed to process confirmation. Database error."
            )


def get_mcp_tool_service(session: Session) -> MCPTaskService:
    """Factory function to get MCP tool service instance."""
    return MCPTaskService(session=session)
