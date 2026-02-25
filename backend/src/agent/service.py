from typing import Dict, Any, List, Optional, Callable
from sqlmodel import Session, select
from datetime import datetime
import uuid

from ..models.agent import (
    AgentTask, AgentTaskStatus, AgentTaskCreate, AgentTaskUpdate,
    ToolExecution, ToolExecutionStatus, ToolExecutionCreate,
    ConversationTurn, ConversationTurnCreate,
    AgentSession
)
from ..models.task import Task as TaskModel, TaskRead
from .reasoning_engine import ReasoningEngine, ParsedIntent, ReasoningChain, IntentType
from .ambiguity_resolver import AmbiguityResolver, AmbiguityResolution
from .context_manager import FollowUpContextManager, ConversationContext
from .mcp_tools import MCPToolRegistry, ToolResult


class TaskServiceAdapter:
    def __init__(self, session_factory, get_session):
        self.session_factory = session_factory
        self.get_session = get_session
    
    async def list_tasks(self, user_id: str) -> List[Dict[str, Any]]:
        with self.session_factory() as session:
            stmt = select(TaskModel).where(TaskModel.user_id == uuid.UUID(user_id))
            tasks = session.exec(stmt).all()
            return [self._task_to_dict(t) for t in tasks]
    
    async def get_task(self, user_id: str, task_id: str) -> Optional[Dict[str, Any]]:
        with self.session_factory() as session:
            stmt = select(TaskModel).where(
                TaskModel.id == uuid.UUID(task_id),
                TaskModel.user_id == uuid.UUID(user_id)
            )
            task = session.exec(stmt).first()
            return self._task_to_dict(task) if task else None
    
    async def create_task(self, user_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        with self.session_factory() as session:
            task = TaskModel(
                user_id=uuid.UUID(user_id),
                title=task_data.get("title", "Untitled"),
                description=task_data.get("description"),
                priority=task_data.get("priority", "medium"),
                status="pending",
                due_date=task_data.get("due_date")
            )
            session.add(task)
            session.commit()
            session.refresh(task)
            return self._task_to_dict(task)
    
    async def update_task(self, user_id: str, task_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        with self.session_factory() as session:
            stmt = select(TaskModel).where(
                TaskModel.id == uuid.UUID(task_id),
                TaskModel.user_id == uuid.UUID(user_id)
            )
            task = session.exec(stmt).first()
            if not task:
                return None
            
            for key, value in update_data.items():
                if hasattr(task, key) and value is not None:
                    setattr(task, key, value)
            
            task.updated_at = datetime.utcnow()
            session.add(task)
            session.commit()
            session.refresh(task)
            return self._task_to_dict(task)
    
    async def delete_task(self, user_id: str, task_id: str) -> bool:
        with self.session_factory() as session:
            stmt = select(TaskModel).where(
                TaskModel.id == uuid.UUID(task_id),
                TaskModel.user_id == uuid.UUID(user_id)
            )
            task = session.exec(stmt).first()
            if not task:
                return False
            session.delete(task)
            session.commit()
            return True
    
    async def toggle_task_status(self, user_id: str, task_id: str, completed: bool) -> Optional[Dict[str, Any]]:
        with self.session_factory() as session:
            stmt = select(TaskModel).where(
                TaskModel.id == uuid.UUID(task_id),
                TaskModel.user_id == uuid.UUID(user_id)
            )
            task = session.exec(stmt).first()
            if not task:
                return None
            
            if completed:
                task.status = "completed"
                task.completed_at = datetime.utcnow()
            else:
                task.status = "pending"
                task.completed_at = None
            
            task.updated_at = datetime.utcnow()
            session.add(task)
            session.commit()
            session.refresh(task)
            return self._task_to_dict(task)
    
    def _task_to_dict(self, task: TaskModel) -> Dict[str, Any]:
        return {
            "id": str(task.id),
            "user_id": str(task.user_id),
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
            "completed_at": task.completed_at.isoformat() if task.completed_at else None
        }


class AgentService:
    def __init__(self, session_factory, get_session):
        self.session_factory = session_factory
        self.get_session = get_session
        self.task_service = TaskServiceAdapter(session_factory, get_session)
        self.reasoning_engine = ReasoningEngine()
        self.ambiguity_resolver = AmbiguityResolver()
        self.context_manager = FollowUpContextManager(session_factory)
        self.mcp_registry: Optional[MCPToolRegistry] = None
    
    def initialize_mcp_tools(self):
        self.mcp_registry = MCPToolRegistry()
        self.mcp_registry.register(self.task_service)
    
    async def process_user_input(self, user_id: str, user_input: str, 
                                 session_id: Optional[str] = None) -> Dict[str, Any]:
        context = self.context_manager.get_context(user_id)
        if not context:
            context = self.context_manager.create_context(user_id)
        
        self.context_manager.add_conversation_turn(user_id, "user", user_input)
        
        parsed_intent = self.reasoning_engine.parse_intent(user_input, context.to_dict())
        
        if parsed_intent.requires_clarification:
            clarification_response = self.reasoning_engine.generate_clarification_response(parsed_intent)
            ambiguities = self.ambiguity_resolver.resolve_ambiguity(user_input, context.to_dict(), parsed_intent.entities)
            
            agent_task = await self._create_agent_task(
                user_id=user_id,
                title=user_input[:255],
                description=user_input,
                status=AgentTaskStatus.WAITING_CLARIFICATION,
                clarification_question=clarification_response
            )
            
            self.context_manager.add_conversation_turn(
                user_id, "assistant", clarification_response, 
                str(parsed_intent.intent), parsed_intent.entities
            )
            
            return {
                "success": True,
                "requires_clarification": True,
                "clarification_question": clarification_response,
                "ambiguities": [a.dict() for a in ambiguities],
                "task_id": str(agent_task.id),
                "intent": str(parsed_intent.intent),
                "entities": parsed_intent.entities
            }
        
        reasoning_chain = self.reasoning_engine.create_reasoning_chain(parsed_intent, user_id)
        
        if parsed_intent.requires_confirmation or reasoning_chain.risk_level in ["high", "medium"]:
            confirmation_prompt = self.reasoning_engine.generate_confirmation_prompt(reasoning_chain)
            
            agent_task = await self._create_agent_task(
                user_id=user_id,
                title=user_input[:255],
                description=user_input,
                status=AgentTaskStatus.WAITING_CONFIRMATION,
                plan=reasoning_chain.dict()
            )
            
            self.context_manager.set_pending_confirmation(user_id, {
                "task_id": str(agent_task.id),
                "chain": reasoning_chain.dict(),
                "intent": str(parsed_intent.intent),
                "entities": parsed_intent.entities
            })
            
            self.context_manager.add_conversation_turn(
                user_id, "assistant", confirmation_prompt,
                str(parsed_intent.intent), parsed_intent.entities
            )
            
            return {
                "success": True,
                "requires_confirmation": True,
                "confirmation_prompt": confirmation_prompt,
                "reasoning_chain": reasoning_chain.dict(),
                "task_id": str(agent_task.id),
                "intent": str(parsed_intent.intent)
            }
        
        result = await self._execute_reasoning_chain(user_id, reasoning_chain, context)
        
        self.context_manager.add_conversation_turn(
            user_id, "assistant", result.get("response", ""),
            str(parsed_intent.intent), parsed_intent.entities
        )
        
        return result
    
    async def handle_follow_up(self, user_id: str, follow_up_input: str) -> Dict[str, Any]:
        context = self.context_manager.get_context(user_id)
        if not context:
            return {
                "success": False,
                "error": "No conversation context found. Please start with a new request."
            }
        
        pending = self.context_manager.get_pending_confirmation(user_id)
        if pending:
            follow_up_lower = follow_up_input.lower().strip()
            
            if any(word in follow_up_lower for word in ["yes", "yeah", "yep", "sure", "ok", "okay", "do it", "go ahead", "proceed"]):
                chain = ReasoningChain(**pending.get("chain", {}))
                result = await self._execute_reasoning_chain(user_id, chain, context)
                self.context_manager.clear_pending_confirmation(user_id)
                return result
            
            elif any(word in follow_up_lower for word in ["no", "nope", "don't", "do not", "cancel", "stop", "never mind"]):
                self.context_manager.clear_pending_confirmation(user_id)
                agent_task = await self._create_agent_task(
                    user_id=user_id,
                    title="Cancelled operation",
                    description=f"User cancelled: {pending.get('intent', 'unknown')}",
                    status=AgentTaskStatus.CANCELLED
                )
                self.context_manager.add_conversation_turn(user_id, "assistant", "Operation cancelled.")
                return {
                    "success": True,
                    "cancelled": True,
                    "message": "Operation cancelled.",
                    "task_id": str(agent_task.id)
                }
        
        parsed_intent = self.reasoning_engine.parse_intent(follow_up_input, context.to_dict())
        
        if parsed_intent.intent == IntentType.FOLLOW_UP_APPROVE and pending:
            chain = ReasoningChain(**pending.get("chain", {}))
            result = await self._execute_reasoning_chain(user_id, chain, context)
            self.context_manager.clear_pending_confirmation(user_id)
            return result
        
        elif parsed_intent.intent == IntentType.FOLLOW_UP_REJECT:
            self.context_manager.clear_pending_confirmation(user_id)
            self.context_manager.add_conversation_turn(user_id, "assistant", "Understood. I won't proceed with that operation.")
            return {
                "success": True,
                "message": "Understood. I won't proceed with that operation."
            }
        
        return await self.process_user_input(user_id, follow_up_input)
    
    async def _execute_reasoning_chain(self, user_id: str, chain: ReasoningChain, 
                                       context: ConversationContext) -> Dict[str, Any]:
        agent_task = await self._create_agent_task(
            user_id=user_id,
            title=chain.steps[0].description if chain.steps else "Agent task",
            description=f"Executing: {chain.steps[0].action}",
            status=AgentTaskStatus.PLANNING,
            plan=chain.dict()
        )
        
        await self._update_agent_task_status(agent_task.id, AgentTaskStatus.EXECUTING)
        
        results = []
        for step in chain.steps:
            tool_result = await self._execute_tool(user_id, step, agent_task.id)
            results.append(tool_result)
            
            if not tool_result["success"]:
                await self._update_agent_task_status(agent_task.id, AgentTaskStatus.FAILED)
                return {
                    "success": False,
                    "error": tool_result.get("error", "Unknown error"),
                    "task_id": str(agent_task.id),
                    "failed_step": step.step_number
                }
        
        await self._update_agent_task_status(agent_task.id, AgentTaskStatus.COMPLETED)
        
        response = self._generate_response(chain, results)
        
        return {
            "success": True,
            "response": response,
            "task_id": str(agent_task.id),
            "tool_results": results,
            "reasoning_chain": chain.dict()
        }
    
    async def _execute_tool(self, user_id: str, step: Any, agent_task_id: uuid.UUID) -> Dict[str, Any]:
        tool_execution = ToolExecution(
            agent_task_id=agent_task_id,
            tool_name=step.tool_name,
            tool_type="mcp",
            input_data=step.tool_params,
            status=ToolExecutionStatus.RUNNING,
            step_number=step.step_number,
            requires_confirmation=step.requires_confirmation
        )
        
        with self.session_factory() as session:
            session.add(tool_execution)
            session.commit()
            session.refresh(tool_execution)
            execution_id = tool_execution.id
        
        tool_execution.started_at = datetime.utcnow()
        
        try:
            if step.tool_name == "task_management":
                result = await self._execute_task_tool(user_id, step.tool_params)
            elif step.tool_name == "analysis":
                result = await self._execute_analysis_tool(user_id, step.tool_params)
            else:
                result = ToolResult(success=False, error=f"Unknown tool: {step.tool_name}")
            
            tool_execution.output_data = result.data if result.data else {}
            tool_execution.error_message = result.error
            tool_execution.status = ToolExecutionStatus.SUCCESS if result.success else ToolExecutionStatus.FAILED
            
            if result.success:
                tool_execution.completed_at = datetime.utcnow()
                
                with self.session_factory() as session:
                    session.add(tool_execution)
                    session.commit()
            
            return {
                "success": result.success,
                "data": result.data,
                "error": result.error,
                "followup_message": result.followup_message,
                "execution_id": str(execution_id)
            }
            
        except Exception as e:
            tool_execution.error_message = str(e)
            tool_execution.status = ToolExecutionStatus.FAILED
            tool_execution.completed_at = datetime.utcnow()
            
            with self.session_factory() as session:
                session.add(tool_execution)
                session.commit()
            
            return {
                "success": False,
                "error": str(e),
                "execution_id": str(execution_id)
            }
    
    async def _execute_task_tool(self, user_id: str, params: Dict[str, Any]) -> ToolResult:
        action = params.get("action")
        
        if action == "list":
            tasks = await self.task_service.list_tasks(user_id)
            self.context_manager.update_recent_tasks(user_id, tasks)
            return ToolResult(
                success=True,
                data={"tasks": tasks},
                followup_message=f"Found {len(tasks)} tasks"
            )
        
        elif action == "create":
            task = await self.task_service.create_task(user_id, params)
            self.context_manager.set_last_task_id(user_id, task["id"])
            return ToolResult(
                success=True,
                data={"task": task},
                followup_message=f"Task '{task['title']}' created successfully"
            )
        
        elif action == "read":
            task_id = params.get("task_id")
            if not task_id:
                return ToolResult(success=False, error="task_id is required")
            task = await self.task_service.get_task(user_id, task_id)
            if task:
                self.context_manager.set_last_mentioned_task(user_id, task)
                return ToolResult(success=True, data={"task": task})
            return ToolResult(success=False, error="Task not found")
        
        elif action == "update":
            task_id = params.get("task_id")
            if not task_id:
                return ToolResult(success=False, error="task_id is required")
            update_data = {k: v for k, v in params.items() 
                          if k in ["title", "description", "status", "priority", "due_date"] and v is not None}
            task = await self.task_service.update_task(user_id, task_id, update_data)
            if task:
                return ToolResult(success=True, data={"task": task}, followup_message="Task updated successfully")
            return ToolResult(success=False, error="Task not found")
        
        elif action == "delete":
            task_id = params.get("task_id")
            if not task_id:
                return ToolResult(success=False, error="task_id is required")
            success = await self.task_service.delete_task(user_id, task_id)
            return ToolResult(success=success, data={"deleted": success})
        
        elif action == "toggle_status":
            task_id = params.get("task_id")
            if not task_id:
                return ToolResult(success=False, error="task_id is required")
            completed = params.get("completed", True)
            task = await self.task_service.toggle_task_status(user_id, task_id, completed)
            if task:
                return ToolResult(
                    success=True,
                    data={"task": task},
                    followup_message=f"Task marked as {'completed' if completed else 'pending'}"
                )
            return ToolResult(success=False, error="Task not found")
        
        return ToolResult(success=False, error=f"Unknown action: {action}")
    
    async def _execute_analysis_tool(self, user_id: str, params: Dict[str, Any]) -> ToolResult:
        analysis_type = params.get("analysis_type", "summary")
        tasks = await self.task_service.list_tasks(user_id)
        
        if analysis_type == "summary":
            total = len(tasks)
            completed = sum(1 for t in tasks if t.get("status") == "completed")
            pending = total - completed
            high_priority = sum(1 for t in tasks if t.get("priority") in ["high", "urgent"])
            return ToolResult(
                success=True,
                data={
                    "total_tasks": total,
                    "completed": completed,
                    "pending": pending,
                    "high_priority": high_priority,
                    "completion_rate": round((completed / total * 100) if total > 0 else 0, 1)
                }
            )
        
        elif analysis_type == "overdue":
            now = datetime.utcnow()
            overdue = []
            for t in tasks:
                if t.get("due_date") and t.get("status") != "completed":
                    try:
                        due = datetime.fromisoformat(t["due_date"].replace("Z", "+00:00")).replace(tzinfo=None)
                        if due < now:
                            overdue.append(t)
                    except:
                        pass
            return ToolResult(success=True, data={"overdue_tasks": overdue, "count": len(overdue)})
        
        elif analysis_type == "by_priority":
            by_priority = {"urgent": [], "high": [], "medium": [], "low": []}
            for task in tasks:
                priority = task.get("priority", "medium")
                if priority in by_priority:
                    by_priority[priority].append(task)
            return ToolResult(success=True, data={"by_priority": by_priority})
        
        elif analysis_type == "by_status":
            by_status = {"pending": [], "in_progress": [], "completed": []}
            for task in tasks:
                status = task.get("status", "pending")
                if status in by_status:
                    by_status[status].append(task)
            return ToolResult(success=True, data={"by_status": by_status})
        
        return ToolResult(success=False, error=f"Unknown analysis type: {analysis_type}")
    
    def _generate_response(self, chain: ReasoningChain, results: List[Dict[str, Any]]) -> str:
        if not results:
            return "Operation completed."
        
        messages = []
        for result in results:
            if result.get("followup_message"):
                messages.append(result["followup_message"])
            elif result.get("data"):
                if "tasks" in result["data"]:
                    tasks = result["data"]["tasks"]
                    if len(tasks) == 0:
                        messages.append("No tasks found.")
                    elif len(tasks) <= 5:
                        task_list = "\n".join([f"  • {t['title']} ({t['status']})" for t in tasks])
                        messages.append(f"Your tasks:\n{task_list}")
                    else:
                        messages.append(f"You have {len(tasks)} tasks.")
                elif "task" in result["data"]:
                    task = result["data"]["task"]
                    messages.append(f"Task: {task['title']} - {task['status']}")
                elif "total_tasks" in result["data"]:
                    data = result["data"]
                    messages.append(
                        f"Summary: {data['total_tasks']} total, {data['completed']} completed, "
                        f"{data['pending']} pending, {data['high_priority']} high priority. "
                        f"Completion rate: {data['completion_rate']}%"
                    )
        
        if messages:
            return "\n\n".join(messages)
        return "Operation completed successfully."
    
    async def _create_agent_task(self, user_id: str, title: str, description: Optional[str] = None,
                                 status: AgentTaskStatus = AgentTaskStatus.PENDING,
                                 plan: Optional[Dict[str, Any]] = None,
                                 clarification_question: Optional[str] = None) -> AgentTask:
        agent_task = AgentTask(
            user_id=uuid.UUID(user_id),
            title=title,
            description=description,
            status=status,
            plan=plan,
            clarification_question=clarification_question
        )
        
        with self.session_factory() as session:
            session.add(agent_task)
            session.commit()
            session.refresh(agent_task)
        
        return agent_task
    
    async def _update_agent_task_status(self, task_id: uuid.UUID, status: AgentTaskStatus) -> None:
        with self.session_factory() as session:
            stmt = select(AgentTask).where(AgentTask.id == task_id)
            agent_task = session.exec(stmt).first()
            if agent_task:
                agent_task.status = status
                if status == AgentTaskStatus.EXECUTING and not agent_task.started_at:
                    agent_task.started_at = datetime.utcnow()
                elif status in [AgentTaskStatus.COMPLETED, AgentTaskStatus.FAILED, AgentTaskStatus.CANCELLED]:
                    agent_task.completed_at = datetime.utcnow()
                session.add(agent_task)
                session.commit()
    
    async def get_agent_task(self, user_id: str, task_id: str) -> Optional[Dict[str, Any]]:
        with self.session_factory() as session:
            stmt = select(AgentTask).where(
                AgentTask.id == uuid.UUID(task_id),
                AgentTask.user_id == uuid.UUID(user_id)
            )
            task = session.exec(stmt).first()
            if not task:
                return None
            
            stmt_executions = select(ToolExecution).where(ToolExecution.agent_task_id == task.id)
            executions = session.exec(stmt_executions).all()
            
            return {
                "id": str(task.id),
                "user_id": str(task.user_id),
                "title": task.title,
                "description": task.description,
                "status": task.status.value,
                "plan": task.plan,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "tool_executions": [
                    {
                        "id": str(e.id),
                        "tool_name": e.tool_name,
                        "status": e.status.value,
                        "input_data": e.input_data,
                        "output_data": e.output_data,
                        "error_message": e.error_message
                    }
                    for e in executions
                ]
            }
    
    async def list_agent_tasks(self, user_id: str, status: Optional[AgentTaskStatus] = None,
                               limit: int = 20) -> List[Dict[str, Any]]:
        with self.session_factory() as session:
            stmt = select(AgentTask).where(AgentTask.user_id == uuid.UUID(user_id))
            if status:
                stmt = stmt.where(AgentTask.status == status)
            stmt = stmt.order_by(AgentTask.created_at.desc()).limit(limit)
            tasks = session.exec(stmt).all()
            
            return [
                {
                    "id": str(t.id),
                    "title": t.title,
                    "status": t.status.value,
                    "created_at": t.created_at.isoformat()
                }
                for t in tasks
            ]
