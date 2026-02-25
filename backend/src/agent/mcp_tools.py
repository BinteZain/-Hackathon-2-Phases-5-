from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from pydantic import BaseModel, Field
from enum import Enum
import uuid
from datetime import datetime


class ToolParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None
    enum: Optional[List[Any]] = None


class ToolDefinition(BaseModel):
    name: str
    description: str
    category: str
    parameters: List[ToolParameter]
    requires_confirmation: bool = False
    confirmation_message: Optional[str] = None


class ToolResult(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    requires_followup: bool = False
    followup_message: Optional[str] = None


class BaseTool(ABC):
    definition: ToolDefinition
    
    @abstractmethod
    async def execute(self, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> ToolResult:
        pass
    
    def validate_params(self, params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        for param in self.definition.parameters:
            if param.required and param.name not in params:
                return False, f"Missing required parameter: {param.name}"
            
            if param.name in params:
                value = params[param.name]
                
                if param.enum and value not in param.enum:
                    return False, f"Parameter {param.name} must be one of: {param.enum}"
                
                type_map = {
                    "string": str,
                    "integer": int,
                    "number": (int, float),
                    "boolean": bool,
                    "array": list,
                    "object": dict
                }
                
                expected_type = type_map.get(param.type)
                if expected_type and not isinstance(value, expected_type):
                    return False, f"Parameter {param.name} must be of type {param.type}"
        
        return True, None


class TaskManagementTool(BaseTool):
    definition = ToolDefinition(
        name="task_management",
        description="Create, read, update, delete, and manage todo tasks",
        category="task",
        parameters=[
            ToolParameter(
                name="action",
                type="string",
                description="The action to perform: create, read, update, delete, list, toggle_status",
                required=True,
                enum=["create", "read", "update", "delete", "list", "toggle_status"]
            ),
            ToolParameter(
                name="task_id",
                type="string",
                description="UUID of the task (required for read, update, delete, toggle_status)",
                required=False
            ),
            ToolParameter(
                name="title",
                type="string",
                description="Task title (required for create)",
                required=False
            ),
            ToolParameter(
                name="description",
                type="string",
                description="Task description",
                required=False
            ),
            ToolParameter(
                name="status",
                type="string",
                description="Task status: pending, in_progress, completed",
                required=False,
                enum=["pending", "in_progress", "completed"]
            ),
            ToolParameter(
                name="priority",
                type="string",
                description="Task priority: low, medium, high, urgent",
                required=False,
                enum=["low", "medium", "high", "urgent"]
            ),
            ToolParameter(
                name="due_date",
                type="string",
                description="Due date in ISO format",
                required=False
            ),
            ToolParameter(
                name="completed",
                type="boolean",
                description="Whether task is completed (for toggle_status)",
                required=False
            )
        ],
        requires_confirmation=True,
        confirmation_message="Confirm task operation before proceeding"
    )
    
    def __init__(self, task_service: Callable):
        self.task_service = task_service
    
    async def execute(self, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> ToolResult:
        try:
            action = params.get("action")
            
            if action == "list":
                tasks = await self.task_service.list_tasks(context.get("user_id"))
                return ToolResult(
                    success=True,
                    data={"tasks": tasks},
                    requires_followup=False
                )
            
            elif action == "create":
                task_data = {
                    "title": params.get("title"),
                    "description": params.get("description"),
                    "priority": params.get("priority", "medium"),
                    "due_date": params.get("due_date")
                }
                task = await self.task_service.create_task(context.get("user_id"), task_data)
                return ToolResult(
                    success=True,
                    data={"task": task},
                    requires_followup=False,
                    followup_message=f"Task '{task.get('title')}' created successfully"
                )
            
            elif action == "read":
                task_id = params.get("task_id")
                if not task_id:
                    return ToolResult(success=False, error="task_id is required")
                task = await self.task_service.get_task(context.get("user_id"), task_id)
                return ToolResult(success=True, data={"task": task})
            
            elif action == "update":
                task_id = params.get("task_id")
                if not task_id:
                    return ToolResult(success=False, error="task_id is required")
                update_data = {k: v for k, v in params.items() 
                              if k in ["title", "description", "status", "priority", "due_date"] and v is not None}
                task = await self.task_service.update_task(context.get("user_id"), task_id, update_data)
                return ToolResult(
                    success=True,
                    data={"task": task},
                    followup_message="Task updated successfully"
                )
            
            elif action == "delete":
                task_id = params.get("task_id")
                if not task_id:
                    return ToolResult(success=False, error="task_id is required")
                await self.task_service.delete_task(context.get("user_id"), task_id)
                return ToolResult(success=True, data={"deleted": True})
            
            elif action == "toggle_status":
                task_id = params.get("task_id")
                if not task_id:
                    return ToolResult(success=False, error="task_id is required")
                completed = params.get("completed", True)
                task = await self.task_service.toggle_task_status(context.get("user_id"), task_id, completed)
                return ToolResult(
                    success=True,
                    data={"task": task},
                    followup_message=f"Task marked as {'completed' if completed else 'pending'}"
                )
            
            else:
                return ToolResult(success=False, error=f"Unknown action: {action}")
                
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class AnalysisTool(BaseTool):
    definition = ToolDefinition(
        name="analysis",
        description="Analyze tasks and provide insights",
        category="analysis",
        parameters=[
            ToolParameter(
                name="analysis_type",
                type="string",
                description="Type of analysis: summary, overdue, by_priority, by_status",
                required=True,
                enum=["summary", "overdue", "by_priority", "by_status"]
            ),
            ToolParameter(
                name="filter",
                type="object",
                description="Optional filters for analysis",
                required=False
            )
        ],
        requires_confirmation=False
    )
    
    def __init__(self, task_service: Callable):
        self.task_service = task_service
    
    async def execute(self, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> ToolResult:
        try:
            analysis_type = params.get("analysis_type")
            user_id = context.get("user_id")
            
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
                overdue = [t for t in tasks 
                          if t.get("due_date") and 
                          datetime.fromisoformat(t["due_date"].replace("Z", "+00:00")).replace(tzinfo=None) < now and
                          t.get("status") != "completed"]
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
            
            else:
                return ToolResult(success=False, error=f"Unknown analysis type: {analysis_type}")
                
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class MCPToolRegistry:
    _instance: Optional["MCPToolRegistry"] = None
    _tools: Dict[str, BaseTool] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register(self, tool: BaseTool):
        self._tools[tool.definition.name] = tool
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)
    
    def list_tools(self) -> List[ToolDefinition]:
        return [tool.definition for tool in self._tools.values()]
    
    def get_tools_by_category(self, category: str) -> List[BaseTool]:
        return [tool for tool in self._tools.values() if tool.definition.category == category]


def initialize_mcp_tools(task_service: Callable) -> MCPToolRegistry:
    registry = MCPToolRegistry()
    registry.register(TaskManagementTool(task_service))
    registry.register(AnalysisTool(task_service))
    return registry
