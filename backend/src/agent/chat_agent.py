"""
OpenAI Agents SDK Integration for Todo AI Chatbot.

This module provides the agent orchestration layer using the official
OpenAI Agents SDK with MCP tools integration.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID
import logging
import json

from ..agent.mcp_service import MCPTaskService, MCPToolError, ToolResponse
from ..models.chat import MessageRole, ConfirmationType

logger = logging.getLogger(__name__)

try:
    from agents import Agent, Runner, function_tool
    OPENAI_AGENTS_AVAILABLE = True
except ImportError:
    OPENAI_AGENTS_AVAILABLE = False
    logger.warning("OpenAI Agents SDK not available. Using fallback implementation.")


class ChatContext:
    """Context object passed to agent tools."""

    def __init__(self, user_id: str, conversation_id: Optional[str] = None):
        self.user_id = user_id
        self.conversation_id = conversation_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "conversation_id": self.conversation_id
        }


class TodoAgent:
    """
    Todo AI Chatbot Agent using OpenAI Agents SDK.

    Provides natural language task management capabilities.
    """

    SYSTEM_INSTRUCTION = """You are a helpful Todo AI Assistant. You help users manage their tasks through natural conversation.

Your capabilities:
- Create new tasks with titles, descriptions, priorities, and due dates
- List and show existing tasks with optional filtering
- Update task details (title, description, status, priority, due date)
- Mark tasks as completed
- Delete tasks (requires user confirmation)

Guidelines:
1. Be concise and friendly in your responses
2. Always confirm what action you're taking
3. For destructive operations (delete), ensure user confirmation
4. When listing tasks, present them in a readable format
5. Handle ambiguous references by asking for clarification
6. Extract relevant entities like dates, priorities, and task titles from user input

Response style:
- Use natural, conversational language
- Summarize actions taken clearly
- When showing multiple tasks, use bullet points or numbered lists
"""

    def __init__(self, mcp_service: MCPTaskService, api_key: Optional[str] = None):
        self.mcp_service = mcp_service
        self.api_key = api_key
        self._agent = None

        if not OPENAI_AGENTS_AVAILABLE:
            logger.warning("OpenAI Agents SDK not installed. Agent features will be limited.")

    def _create_tools(self, context: ChatContext) -> List:
        """Create tool functions for the agent."""

        @function_tool
        async def add_task(title: str, description: str = None,
                          priority: str = "medium", due_date: str = None) -> dict:
            """Create a new task in the user's todo list."""
            try:
                result = await self.mcp_service.add_task(
                    title=title,
                    description=description,
                    priority=priority,
                    due_date=due_date,
                    context=context.to_dict()
                )
                return result.model_dump()
            except MCPToolError as e:
                return {
                    "success": False,
                    "error": {"code": e.code, "message": e.message}
                }

        @function_tool
        async def list_tasks(status: str = None, priority: str = None,
                            limit: int = 50, offset: int = 0) -> dict:
            """List all tasks for the user with optional filtering."""
            try:
                result = await self.mcp_service.list_tasks(
                    status=status,
                    priority=priority,
                    limit=limit,
                    offset=offset,
                    context=context.to_dict()
                )
                return result.model_dump()
            except MCPToolError as e:
                return {
                    "success": False,
                    "error": {"code": e.code, "message": e.message}
                }

        @function_tool
        async def update_task(task_id: str, title: str = None,
                             description: str = None, status: str = None,
                             priority: str = None, due_date: str = None) -> dict:
            """Update an existing task's properties."""
            try:
                result = await self.mcp_service.update_task(
                    task_id=task_id,
                    title=title,
                    description=description,
                    status=status,
                    priority=priority,
                    due_date=due_date,
                    context=context.to_dict()
                )
                return result.model_dump()
            except MCPToolError as e:
                return {
                    "success": False,
                    "error": {"code": e.code, "message": e.message}
                }

        @function_tool
        async def complete_task(task_id: str) -> dict:
            """Mark a task as completed."""
            try:
                result = await self.mcp_service.complete_task(
                    task_id=task_id,
                    context=context.to_dict()
                )
                return result.model_dump()
            except MCPToolError as e:
                return {
                    "success": False,
                    "error": {"code": e.code, "message": e.message}
                }

        @function_tool
        async def delete_task(task_id: str, confirmed: bool = False) -> dict:
            """Delete a task. Requires confirmation for destructive operation."""
            try:
                result = await self.mcp_service.delete_task(
                    task_id=task_id,
                    confirmed=confirmed,
                    context=context.to_dict()
                )
                return result.model_dump()
            except MCPToolError as e:
                return {
                    "success": False,
                    "error": {"code": e.code, "message": e.message}
                }

        return [add_task, list_tasks, update_task, complete_task, delete_task]

    def _get_agent(self, context: ChatContext):
        """Get or create the agent instance."""
        if self._agent is None and OPENAI_AGENTS_AVAILABLE:
            tools = self._create_tools(context)
            self._agent = Agent(
                name="TodoAssistant",
                instructions=self.SYSTEM_INSTRUCTION,
                tools=tools,
                model="gpt-4o-mini"
            )
        return self._agent

    async def process_message(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        context: Optional[ChatContext] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and return agent response.

        Args:
            user_message: The user's input message
            conversation_history: Previous messages in the conversation
            context: Chat context with user_id and conversation_id

        Returns:
            Dictionary with response content, intent, entities, and tool results
        """
        if context is None:
            context = ChatContext(user_id="unknown")

        if OPENAI_AGENTS_AVAILABLE and self.api_key:
            return await self._process_with_sdk(user_message, conversation_history, context)
        else:
            return await self._process_fallback(user_message, context)

    async def _process_with_sdk(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]],
        context: ChatContext
    ) -> Dict[str, Any]:
        """Process message using OpenAI Agents SDK."""
        try:
            agent = self._get_agent(context)

            # Build input messages
            messages = []
            if conversation_history:
                messages.extend(conversation_history)
            messages.append({"role": "user", "content": user_message})

            # Run the agent
            from agents import Runner
            result = await Runner.run(agent, messages)

            # Extract response
            response_content = result.final_output

            # Parse tool calls if any
            tool_results = []
            intent = "general"
            entities = {}

            if hasattr(result, 'tool_calls') and result.tool_calls:
                for tool_call in result.tool_calls:
                    tool_results.append({
                        "tool_name": tool_call.get("name", "unknown"),
                        "success": True,
                        "data": tool_call.get("arguments", {})
                    })
                    # Infer intent from tool name
                    tool_name = tool_call.get("name", "")
                    if tool_name == "add_task":
                        intent = "create_task"
                        entities = tool_call.get("arguments", {})
                    elif tool_name == "list_tasks":
                        intent = "list_tasks"
                    elif tool_name == "update_task":
                        intent = "update_task"
                        entities = tool_call.get("arguments", {})
                    elif tool_name == "complete_task":
                        intent = "complete_task"
                        entities = {"task_id": tool_call.get("arguments", {}).get("task_id")}
                    elif tool_name == "delete_task":
                        intent = "delete_task"
                        entities = {"task_id": tool_call.get("arguments", {}).get("task_id")}

            return {
                "content": response_content,
                "intent": intent,
                "entities": entities,
                "tool_results": tool_results,
                "requires_confirmation": False
            }

        except Exception as e:
            logger.error(f"Error processing with SDK: {str(e)}")
            return {
                "content": "I encountered an error processing your request. Please try again.",
                "intent": "error",
                "entities": {},
                "tool_results": [],
                "requires_confirmation": False,
                "error": str(e)
            }

    async def _process_fallback(
        self,
        user_message: str,
        context: ChatContext
    ) -> Dict[str, Any]:
        """
        Fallback implementation when OpenAI Agents SDK is not available.

        This provides basic keyword-based intent recognition and tool execution.
        """
        user_message_lower = user_message.lower().strip()

        # Simple intent recognition
        intent = self._detect_intent(user_message_lower)
        entities = self._extract_entities(user_message_lower)

        try:
            if intent == "create_task":
                result = await self.mcp_service.add_task(
                    title=entities.get("title", "Untitled Task"),
                    description=entities.get("description"),
                    priority=entities.get("priority", "medium"),
                    due_date=entities.get("due_date"),
                    context=context.to_dict()
                )
                if result.success:
                    task = result.data["task"]
                    return {
                        "content": f"I've added '{task['title']}' to your todo list.",
                        "intent": "create_task",
                        "entities": entities,
                        "tool_results": [{"tool_name": "add_task", "success": True, "data": {"task_id": task["id"]}}],
                        "requires_confirmation": False
                    }
                else:
                    return {
                        "content": f"Sorry, I couldn't create the task: {result.error.get('message', 'Unknown error')}",
                        "intent": "error",
                        "entities": {},
                        "tool_results": [],
                        "requires_confirmation": False
                    }

            elif intent == "list_tasks":
                result = await self.mcp_service.list_tasks(
                    status=entities.get("status"),
                    priority=entities.get("priority"),
                    context=context.to_dict()
                )
                if result.success:
                    tasks = result.data["tasks"]
                    if not tasks:
                        return {
                            "content": "You don't have any tasks yet. Would you like to add one?",
                            "intent": "list_tasks",
                            "entities": {},
                            "tool_results": [{"tool_name": "list_tasks", "success": True, "data": {"tasks": []}}],
                            "requires_confirmation": False
                        }

                    task_list = "\n".join([f"{i+1}. {t['title']} ({t['status']})" for i, t in enumerate(tasks)])
                    return {
                        "content": f"Here are your tasks:\n{task_list}",
                        "intent": "list_tasks",
                        "entities": {},
                        "tool_results": [{"tool_name": "list_tasks", "success": True, "data": {"total": len(tasks)}}],
                        "requires_confirmation": False
                    }
                else:
                    return {
                        "content": f"Sorry, I couldn't retrieve your tasks: {result.error.get('message', 'Unknown error')}",
                        "intent": "error",
                        "entities": {},
                        "tool_results": [],
                        "requires_confirmation": False
                    }

            elif intent == "complete_task":
                if "task_id" in entities:
                    result = await self.mcp_service.complete_task(
                        task_id=entities["task_id"],
                        context=context.to_dict()
                    )
                    if result.success:
                        return {
                            "content": "Task marked as completed!",
                            "intent": "complete_task",
                            "entities": entities,
                            "tool_results": [{"tool_name": "complete_task", "success": True}],
                            "requires_confirmation": False
                        }
                return {
                    "content": "Which task would you like to mark as complete? Please provide the task ID or title.",
                    "intent": "clarify_task",
                    "entities": {},
                    "tool_results": [],
                    "requires_confirmation": False
                }

            elif intent == "delete_task":
                if "task_id" in entities:
                    result = await self.mcp_service.delete_task(
                        task_id=entities["task_id"],
                        confirmed=False,
                        context=context.to_dict()
                    )
                    if result.requires_confirmation:
                        return {
                            "content": result.confirmation_prompt,
                            "intent": "delete_task",
                            "entities": entities,
                            "tool_results": [],
                            "requires_confirmation": True,
                            "pending_action_id": str(result.pending_action_id)
                        }
                    elif result.success:
                        return {
                            "content": "Task deleted successfully.",
                            "intent": "delete_task",
                            "entities": entities,
                            "tool_results": [{"tool_name": "delete_task", "success": True}],
                            "requires_confirmation": False
                        }
                return {
                    "content": "Which task would you like to delete? Please provide the task ID or title.",
                    "intent": "clarify_task",
                    "entities": {},
                    "tool_results": [],
                    "requires_confirmation": False
                }

            elif intent == "greeting":
                return {
                    "content": "Hello! I'm your Todo AI Assistant. I can help you manage your tasks. What would you like to do?",
                    "intent": "greeting",
                    "entities": {},
                    "tool_results": [],
                    "requires_confirmation": False
                }

            elif intent == "help":
                return {
                    "content": "I can help you:\n• Add new tasks (e.g., 'Add a task to buy groceries')\n• List your tasks (e.g., 'Show my tasks')\n• Complete tasks (e.g., 'Mark task as done')\n• Delete tasks (e.g., 'Delete the task about meeting')\n\nWhat would you like to do?",
                    "intent": "help",
                    "entities": {},
                    "tool_results": [],
                    "requires_confirmation": False
                }

            else:
                return {
                    "content": "I'm not sure I understood. You can ask me to add, list, update, complete, or delete tasks. For example: 'Add a task to call the dentist tomorrow'.",
                    "intent": "unclear",
                    "entities": {},
                    "tool_results": [],
                    "requires_confirmation": False
                }

        except MCPToolError as e:
            return {
                "content": f"Sorry, I encountered an error: {e.message}",
                "intent": "error",
                "entities": {},
                "tool_results": [],
                "requires_confirmation": False
            }
        except Exception as e:
            logger.error(f"Fallback processing error: {str(e)}")
            return {
                "content": "I encountered an error processing your request. Please try again.",
                "intent": "error",
                "entities": {},
                "tool_results": [],
                "requires_confirmation": False
            }

    def _detect_intent(self, message: str) -> str:
        """Detect intent from user message using keyword matching."""
        # Greetings
        if any(word in message for word in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
            return "greeting"

        # Help
        if any(word in message for word in ["help", "what can you do", "how to", "what do you do"]):
            return "help"

        # Create task
        if any(phrase in message for phrase in ["add a task", "add task", "create a task", "create task",
                                                  "i need to", "i want to", "remind me to", "todo"]):
            return "create_task"

        # List tasks
        if any(phrase in message for phrase in ["show my tasks", "list tasks", "my tasks", "what do i have",
                                                  "pending tasks", "all tasks", "view tasks"]):
            return "list_tasks"

        # Complete task
        if any(phrase in message for phrase in ["complete", "mark as done", "finished", "done with"]):
            return "complete_task"

        # Delete task
        if any(phrase in message for phrase in ["delete", "remove", "cancel", "get rid of"]):
            return "delete_task"

        # Update task
        if any(phrase in message for phrase in ["update", "change", "edit", "modify"]):
            return "update_task"

        return "unclear"

    def _extract_entities(self, message: str) -> Dict[str, Any]:
        """Extract entities from user message."""
        entities = {}

        # Extract priority
        if any(word in message for word in ["urgent", "urgently"]):
            entities["priority"] = "urgent"
        elif any(word in message for word in ["high priority", "important"]):
            entities["priority"] = "high"
        elif "low priority" in message:
            entities["priority"] = "low"

        # Extract simple date references
        if "tomorrow" in message:
            from datetime import datetime, timedelta
            tomorrow = datetime.utcnow() + timedelta(days=1)
            entities["due_date"] = tomorrow.isoformat() + "Z"
        elif "today" in message:
            from datetime import datetime
            today = datetime.utcnow()
            entities["due_date"] = today.isoformat() + "Z"
        elif "next week" in message:
            from datetime import datetime, timedelta
            next_week = datetime.utcnow() + timedelta(weeks=1)
            entities["due_date"] = next_week.isoformat() + "Z"

        # Extract task title (simplified - after common verbs)
        title_markers = ["task to ", "task: ", "todo: ", "to "]
        for marker in title_markers:
            if marker in message:
                start_idx = message.find(marker) + len(marker)
                potential_title = message[start_idx:].strip()
                # Clean up the title
                for end_word in [" tomorrow", " today", " next week", " urgent", " high priority"]:
                    if end_word in potential_title:
                        potential_title = potential_title.split(end_word)[0].strip()
                if potential_title:
                    entities["title"] = potential_title
                    break

        return entities


def create_todo_agent(mcp_service: MCPTaskService, api_key: Optional[str] = None) -> TodoAgent:
    """Factory function to create a TodoAgent instance."""
    return TodoAgent(mcp_service=mcp_service, api_key=api_key)
