from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
import re


class IntentType(str, Enum):
    CREATE_TASK = "create_task"
    UPDATE_TASK = "update_task"
    DELETE_TASK = "delete_task"
    GET_TASK = "get_task"
    LIST_TASKS = "list_tasks"
    TOGGLE_TASK = "toggle_task"
    ANALYZE_TASKS = "analyze_tasks"
    FOLLOW_UP_APPROVE = "follow_up_approve"
    FOLLOW_UP_CLARIFY = "follow_up_clarify"
    FOLLOW_UP_REJECT = "follow_up_reject"
    UNKNOWN = "unknown"


class ParsedIntent(BaseModel):
    intent: IntentType
    confidence: float = 1.0
    entities: Dict[str, Any] = Field(default_factory=dict)
    requires_confirmation: bool = False
    requires_clarification: bool = False
    clarification_points: List[str] = Field(default_factory=list)
    follow_up_context: Optional[str] = None


class ReasoningStep(BaseModel):
    step_number: int
    action: str
    tool_name: str
    tool_params: Dict[str, Any]
    description: str
    requires_confirmation: bool = False
    depends_on: List[int] = Field(default_factory=list)


class ReasoningChain(BaseModel):
    intent: ParsedIntent
    steps: List[ReasoningStep] = Field(default_factory=list)
    total_steps: int = 0
    estimated_time_seconds: int = 0
    risk_level: str = "low"
    
    def add_step(self, action: str, tool_name: str, tool_params: Dict[str, Any], 
                 description: str, requires_confirmation: bool = False, 
                 depends_on: Optional[List[int]] = None):
        step = ReasoningStep(
            step_number=len(self.steps) + 1,
            action=action,
            tool_name=tool_name,
            tool_params=tool_params,
            description=description,
            requires_confirmation=requires_confirmation,
            depends_on=depends_on or []
        )
        self.steps.append(step)
        self.total_steps = len(self.steps)
        return step


class ReasoningEngine:
    FOLLOW_UP_PATTERNS = [
        r'\b(yes|yeah|yep|sure|ok|okay|do it|go ahead|proceed)\b',
        r'\b(no|nope|don\'t|do not|cancel|stop)\b',
        r'\b(modify|change|edit|update)\b'
    ]
    
    DELETE_KEYWORDS = ['delete', 'remove', 'drop', 'destroy']
    BULK_KEYWORDS = ['all', 'every', 'bulk', 'multiple']
    CREATE_KEYWORDS = ['create', 'add', 'new', 'make', 'set up']
    UPDATE_KEYWORDS = ['update', 'edit', 'change', 'modify', 'set']
    LIST_KEYWORDS = ['list', 'show', 'get', 'fetch', 'retrieve', 'view', 'all']
    TOGGLE_KEYWORDS = ['complete', 'finish', 'done', 'mark', 'toggle']
    ANALYZE_KEYWORDS = ['analyze', 'summary', 'report', 'stats', 'overview', 'how many']
    
    def __init__(self):
        pass
    
    def parse_intent(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> ParsedIntent:
        user_input = user_input.lower().strip()
        
        follow_up_check = self._check_follow_up(user_input, context)
        if follow_up_check[0]:
            return follow_up_check[1]
        
        intent, confidence, entities = self._detect_intent(user_input)
        
        requires_confirmation = self._check_confirmation_needed(intent, entities, user_input)
        requires_clarification, clarification_points = self._check_clarification_needed(intent, entities, user_input)
        
        return ParsedIntent(
            intent=intent,
            confidence=confidence,
            entities=entities,
            requires_confirmation=requires_confirmation,
            requires_clarification=requires_clarification,
            clarification_points=clarification_points,
            follow_up_context=context.get("last_task_id") if context else None
        )
    
    def _check_follow_up(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Tuple[bool, Optional[ParsedIntent]]:
        if not context or not context.get("pending_task"):
            return False, None
        
        for pattern in self.FOLLOW_UP_PATTERNS:
            if re.search(pattern, user_input, re.IGNORECASE):
                if any(word in user_input for word in ['no', 'nope', "don't", 'do not', 'cancel', 'stop']):
                    return True, ParsedIntent(
                        intent=IntentType.FOLLOW_UP_REJECT,
                        confidence=0.95,
                        entities={"task_id": context.get("pending_task").get("id")},
                        follow_up_context=context.get("last_task_id")
                    )
                elif any(word in user_input for word in ['modify', 'change', 'edit', 'update']):
                    return True, ParsedIntent(
                        intent=IntentType.FOLLOW_UP_CLARIFY,
                        confidence=0.9,
                        entities={"task_id": context.get("pending_task").get("id")},
                        follow_up_context=context.get("last_task_id")
                    )
                else:
                    return True, ParsedIntent(
                        intent=IntentType.FOLLOW_UP_APPROVE,
                        confidence=0.95,
                        entities={"task_id": context.get("pending_task").get("id")},
                        follow_up_context=context.get("last_task_id")
                    )
        
        return False, None
    
    def _detect_intent(self, user_input: str) -> Tuple[IntentType, float, Dict[str, Any]]:
        entities = self._extract_entities(user_input)
        
        if any(kw in user_input for kw in self.DELETE_KEYWORDS):
            if not entities.get("task_id") and not entities.get("task_title"):
                return IntentType.DELETE_TASK, 0.6, entities
            return IntentType.DELETE_TASK, 0.9, entities
        
        if any(kw in user_input for kw in self.BULK_KEYWORDS) and any(kw in user_input for kw in self.DELETE_KEYWORDS + self.UPDATE_KEYWORDS):
            return IntentType.UPDATE_TASK, 0.7, entities
        
        if any(kw in user_input for kw in self.CREATE_KEYWORDS):
            return IntentType.CREATE_TASK, 0.9, entities
        
        if any(kw in user_input for kw in self.UPDATE_KEYWORDS):
            if entities.get("task_id") or entities.get("task_title"):
                return IntentType.UPDATE_TASK, 0.85, entities
            return IntentType.UPDATE_TASK, 0.6, entities
        
        if any(kw in user_input for kw in self.LIST_KEYWORDS):
            return IntentType.LIST_TASKS, 0.95, entities
        
        if any(kw in user_input for kw in self.TOGGLE_KEYWORDS):
            return IntentType.TOGGLE_TASK, 0.8, entities
        
        if any(kw in user_input for kw in self.ANALYZE_KEYWORDS):
            analysis_type = "summary"
            if "overdue" in user_input:
                analysis_type = "overdue"
            elif "priority" in user_input:
                analysis_type = "by_priority"
            elif "status" in user_input:
                analysis_type = "by_status"
            entities["analysis_type"] = analysis_type
            return IntentType.ANALYZE_TASKS, 0.9, entities
        
        if "get" in user_input or "find" in user_input or "task" in user_input:
            if entities.get("task_id") or entities.get("task_title"):
                return IntentType.GET_TASK, 0.85, entities
        
        return IntentType.UNKNOWN, 0.3, entities
    
    def _extract_entities(self, user_input: str) -> Dict[str, Any]:
        entities = {}
        
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        uuid_match = re.search(uuid_pattern, user_input, re.IGNORECASE)
        if uuid_match:
            entities["task_id"] = uuid_match.group()
        
        date_pattern = r'\b(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4})\b'
        date_match = re.search(date_pattern, user_input)
        if date_match:
            entities["due_date"] = date_match.group()
        
        priority_match = re.search(r'\b(low|medium|high|urgent)\b', user_input, re.IGNORECASE)
        if priority_match:
            entities["priority"] = priority_match.group().lower()
        
        status_match = re.search(r'\b(pending|in_progress|completed|done)\b', user_input, re.IGNORECASE)
        if status_match:
            status = status_match.group().lower()
            if status == "done":
                status = "completed"
            entities["status"] = status
        
        title_match = re.search(r'["\']([^"\']+)["\']', user_input)
        if title_match:
            entities["task_title"] = title_match.group(1)
        else:
            task_words = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', user_input)
            if task_words and len(task_words) <= 5:
                potential_title = ' '.join(task_words[:3])
                if not any(kw in potential_title.lower() for kw in ['create', 'add', 'delete', 'update']):
                    entities["task_title"] = potential_title
        
        return entities
    
    def _check_confirmation_needed(self, intent: IntentType, entities: Dict[str, Any], user_input: str) -> bool:
        if intent == IntentType.DELETE_TASK:
            return True
        
        if intent == IntentType.UPDATE_TASK and any(kw in user_input for kw in self.BULK_KEYWORDS):
            return True
        
        if entities.get("task_id") and intent in [IntentType.UPDATE_TASK, IntentType.DELETE_TASK]:
            return True
        
        return False
    
    def _check_clarification_needed(self, intent: IntentType, entities: Dict[str, Any], user_input: str) -> Tuple[bool, List[str]]:
        clarification_points = []
        
        if intent == IntentType.UNKNOWN:
            clarification_points.append("I'm not sure what you'd like me to do. Could you clarify?")
            return True, clarification_points
        
        if intent == IntentType.CREATE_TASK:
            if not entities.get("task_title") and "title" not in user_input and "task" not in user_input:
                clarification_points.append("What title would you like for this task?")
        
        if intent == IntentType.UPDATE_TASK:
            if not entities.get("task_id") and not entities.get("task_title"):
                clarification_points.append("Which task would you like to update?")
            if not any(k in user_input for k in ["title", "description", "status", "priority", "due"]):
                clarification_points.append("What would you like to change about the task?")
        
        if intent == IntentType.DELETE_TASK:
            if not entities.get("task_id") and not entities.get("task_title"):
                clarification_points.append("Which task would you like to delete?")
        
        if intent == IntentType.TOGGLE_TASK:
            if not entities.get("task_id") and not entities.get("task_title"):
                clarification_points.append("Which task would you like to mark as complete?")
        
        if intent == IntentType.GET_TASK:
            if not entities.get("task_id") and not entities.get("task_title"):
                clarification_points.append("Which task would you like to view?")
        
        return len(clarification_points) > 0, clarification_points
    
    def create_reasoning_chain(self, parsed_intent: ParsedIntent, user_id: str) -> ReasoningChain:
        chain = ReasoningChain(intent=parsed_intent)
        
        if parsed_intent.intent == IntentType.CREATE_TASK:
            chain.add_step(
                action="create",
                tool_name="task_management",
                tool_params={
                    "action": "create",
                    "title": parsed_intent.entities.get("task_title", "Untitled Task"),
                    "description": parsed_intent.entities.get("description"),
                    "priority": parsed_intent.entities.get("priority", "medium"),
                    "due_date": parsed_intent.entities.get("due_date")
                },
                description=f"Create new task: {parsed_intent.entities.get('task_title', 'Untitled Task')}",
                requires_confirmation=False
            )
            chain.risk_level = "low"
            chain.estimated_time_seconds = 2
        
        elif parsed_intent.intent == IntentType.UPDATE_TASK:
            chain.add_step(
                action="update",
                tool_name="task_management",
                tool_params={
                    "action": "update",
                    "task_id": parsed_intent.entities.get("task_id"),
                    "title": parsed_intent.entities.get("title"),
                    "description": parsed_intent.entities.get("description"),
                    "status": parsed_intent.entities.get("status"),
                    "priority": parsed_intent.entities.get("priority"),
                    "due_date": parsed_intent.entities.get("due_date")
                },
                description=f"Update task with provided changes",
                requires_confirmation=parsed_intent.requires_confirmation,
                depends_on=[]
            )
            chain.risk_level = "medium"
            chain.estimated_time_seconds = 3
        
        elif parsed_intent.intent == IntentType.DELETE_TASK:
            chain.add_step(
                action="delete",
                tool_name="task_management",
                tool_params={
                    "action": "delete",
                    "task_id": parsed_intent.entities.get("task_id")
                },
                description=f"Delete task permanently",
                requires_confirmation=True,
                depends_on=[]
            )
            chain.risk_level = "high"
            chain.estimated_time_seconds = 2
        
        elif parsed_intent.intent == IntentType.LIST_TASKS:
            chain.add_step(
                action="list",
                tool_name="task_management",
                tool_params={"action": "list"},
                description="Retrieve all tasks for the user",
                requires_confirmation=False
            )
            chain.risk_level = "low"
            chain.estimated_time_seconds = 2
        
        elif parsed_intent.intent == IntentType.GET_TASK:
            chain.add_step(
                action="read",
                tool_name="task_management",
                tool_params={
                    "action": "read",
                    "task_id": parsed_intent.entities.get("task_id")
                },
                description=f"Retrieve specific task details",
                requires_confirmation=False
            )
            chain.risk_level = "low"
            chain.estimated_time_seconds = 2
        
        elif parsed_intent.intent == IntentType.TOGGLE_TASK:
            chain.add_step(
                action="toggle",
                tool_name="task_management",
                tool_params={
                    "action": "toggle_status",
                    "task_id": parsed_intent.entities.get("task_id"),
                    "completed": True
                },
                description="Mark task as completed",
                requires_confirmation=False
            )
            chain.risk_level = "low"
            chain.estimated_time_seconds = 2
        
        elif parsed_intent.intent == IntentType.ANALYZE_TASKS:
            chain.add_step(
                action="analyze",
                tool_name="analysis",
                tool_params={
                    "analysis_type": parsed_intent.entities.get("analysis_type", "summary")
                },
                description=f"Generate {parsed_intent.entities.get('analysis_type', 'summary')} analysis of tasks",
                requires_confirmation=False
            )
            chain.risk_level = "low"
            chain.estimated_time_seconds = 3
        
        elif parsed_intent.intent == IntentType.FOLLOW_UP_APPROVE:
            chain.add_step(
                action="execute_pending",
                tool_name="task_management",
                tool_params=parsed_intent.entities.get("pending_params", {}),
                description="Execute previously pending operation with user approval",
                requires_confirmation=False
            )
            chain.risk_level = "medium"
            chain.estimated_time_seconds = 3
        
        elif parsed_intent.intent == IntentType.FOLLOW_UP_REJECT:
            chain.add_step(
                action="cancel_pending",
                tool_name="task_management",
                tool_params={"action": "cancel"},
                description="Cancel previously pending operation",
                requires_confirmation=False
            )
            chain.risk_level = "low"
            chain.estimated_time_seconds = 1
        
        return chain
    
    def generate_clarification_response(self, parsed_intent: ParsedIntent) -> str:
        if not parsed_intent.clarification_points:
            return ""
        
        response = "I need a bit more information to help you with that:\n\n"
        for i, point in enumerate(parsed_intent.clarification_points, 1):
            response += f"{i}. {point}\n"
        response += "\nPlease provide these details so I can proceed."
        return response
    
    def generate_confirmation_prompt(self, chain: ReasoningChain) -> str:
        if chain.risk_level == "high":
            return f"⚠️ This action is **permanent**.\n\nI'm about to: {chain.steps[0].description}\n\nAre you sure you want to proceed? Please confirm with 'yes' or 'do it'."
        elif chain.risk_level == "medium":
            return f"I'm about to: {chain.steps[0].description}\n\nShould I proceed? (yes/no)"
        else:
            return f"Ready to: {chain.steps[0].description}\n\nShall I continue? (yes/no)"
