from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field
from enum import Enum


class AmbiguityType(str, Enum):
    MISSING_ENTITY = "missing_entity"
    MULTIPLE_MATCHES = "multiple_matches"
    UNCLEAR_INTENT = "unclear_intent"
    PARAMETER_CONFLICT = "parameter_conflict"
    TEMPORAL_AMBIGUITY = "temporal_ambiguity"
    REFERENCE_AMBIGUITY = "reference_ambiguity"


class AmbiguityResolution(BaseModel):
    ambiguity_type: AmbiguityType
    description: str
    options: List[Dict[str, Any]] = Field(default_factory=list)
    suggested_option: Optional[int] = None
    resolution_question: str = ""


class AmbiguityResolver:
    INTENT_SYNONYMS = {
        "create": ["add", "make", "new", "set up", "start"],
        "update": ["edit", "change", "modify", "adjust", "fix"],
        "delete": ["remove", "drop", "destroy", "kill", "erase"],
        "list": ["show", "get", "fetch", "retrieve", "view", "display", "all"],
        "complete": ["finish", "done", "check", "tick", "accomplish"],
        "analyze": ["summary", "report", "stats", "overview", "breakdown"]
    }
    
    PRIORITY_ORDER = {"urgent": 4, "high": 3, "medium": 2, "low": 1}
    
    STATUS_SYNONYMS = {
        "pending": ["todo", "not started", "open", "new"],
        "in_progress": ["working", "active", "ongoing", "started"],
        "completed": ["done", "finished", "accomplished", "closed"]
    }
    
    def __init__(self):
        pass
    
    def resolve_ambiguity(self, user_input: str, context: Optional[Dict[str, Any]] = None, 
                         entities: Optional[Dict[str, Any]] = None) -> List[AmbiguityResolution]:
        ambiguities = []
        
        intent_ambiguity = self._check_intent_ambiguity(user_input, context)
        if intent_ambiguity:
            ambiguities.append(intent_ambiguity)
        
        entity_ambiguity = self._check_entity_ambiguity(user_input, entities, context)
        if entity_ambiguity:
            ambiguities.append(entity_ambiguity)
        
        reference_ambiguity = self._check_reference_ambiguity(user_input, context)
        if reference_ambiguity:
            ambiguities.append(reference_ambiguity)
        
        parameter_ambiguity = self._check_parameter_conflict(entities)
        if parameter_ambiguity:
            ambiguities.append(parameter_ambiguity)
        
        return ambiguities
    
    def _check_intent_ambiguity(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Optional[AmbiguityResolution]:
        user_input_lower = user_input.lower()
        
        matched_intents = []
        for intent, synonyms in self.INTENT_SYNONYMS.items():
            for synonym in synonyms:
                if synonym in user_input_lower:
                    matched_intents.append(intent)
                    break
        
        if len(matched_intents) > 1:
            return AmbiguityResolution(
                ambiguity_type=AmbiguityType.UNCLEAR_INTENT,
                description="Multiple possible actions detected in your request",
                options=[{"intent": intent, "description": f"{intent.capitalize()} tasks"} for intent in matched_intents],
                suggested_option=0,
                resolution_question=f"I notice you mentioned multiple actions: {', '.join(matched_intents)}. Which would you like me to do first?"
            )
        
        if len(matched_intents) == 0:
            keywords = [w for w in user_input_lower.split() if len(w) > 3]
            if keywords and context and context.get("pending_task"):
                return AmbiguityResolution(
                    ambiguity_type=AmbiguityType.UNCLEAR_INTENT,
                    description="I'm not sure what action you want to take",
                    options=[
                        {"intent": "execute_pending", "description": "Proceed with pending task"},
                        {"intent": "clarify", "description": "Let me clarify what you want"}
                    ],
                    suggested_option=1,
                    resolution_question="Could you clarify what you'd like me to do? You can say 'yes' to proceed with the pending task, or tell me more specifically."
                )
        
        return None
    
    def _check_entity_ambiguity(self, user_input: str, entities: Optional[Dict[str, Any]] = None,
                                context: Optional[Dict[str, Any]] = None) -> Optional[AmbiguityResolution]:
        entities = entities or {}
        
        if "task_title" in entities and context and context.get("recent_tasks"):
            matching_tasks = []
            title_query = entities["task_title"].lower()
            
            for task in context["recent_tasks"]:
                if title_query in task.get("title", "").lower():
                    matching_tasks.append(task)
            
            if len(matching_tasks) > 1:
                options = [
                    {"task_id": t["id"], "title": t["title"], "status": t.get("status", "pending")}
                    for t in matching_tasks
                ]
                return AmbiguityResolution(
                    ambiguity_type=AmbiguityType.MULTIPLE_MATCHES,
                    description=f"Found {len(matching_tasks)} tasks matching '{entities['task_title']}'",
                    options=options,
                    suggested_option=0,
                    resolution_question=f"I found {len(matching_tasks)} similar tasks. Which one did you mean?"
                )
        
        if not entities.get("task_id") and not entities.get("task_title"):
            if any(word in user_input.lower() for word in ["task", "todo", "item"]):
                if context and context.get("recent_tasks") and len(context["recent_tasks"]) == 1:
                    return None
                return AmbiguityResolution(
                    ambiguity_type=AmbiguityType.MISSING_ENTITY,
                    description="No specific task identified",
                    options=[],
                    suggested_option=None,
                    resolution_question="Which task are you referring to? You can provide the task title or describe it."
                )
        
        return None
    
    def _check_reference_ambiguity(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Optional[AmbiguityResolution]:
        reference_words = ["this", "that", "it", "these", "those", "the task", "the previous one"]
        
        has_reference = any(ref in user_input.lower() for ref in reference_words)
        
        if has_reference and context:
            if context.get("last_mentioned_task"):
                return None
            elif context.get("pending_task"):
                return None
            else:
                return AmbiguityResolution(
                    ambiguity_type=AmbiguityType.REFERENCE_AMBIGUITY,
                    description="Reference detected but no clear antecedent",
                    options=[],
                    suggested_option=None,
                    resolution_question="I'm not sure which task you're referring to. Could you be more specific?"
                )
        
        return None
    
    def _check_parameter_conflict(self, entities: Optional[Dict[str, Any]] = None) -> Optional[AmbiguityResolution]:
        entities = entities or {}
        
        if entities.get("priority") and entities.get("priority") not in ["low", "medium", "high", "urgent"]:
            return AmbiguityResolution(
                ambiguity_type=AmbiguityType.PARAMETER_CONFLICT,
                description=f"Unknown priority level: {entities.get('priority')}",
                options=[
                    {"value": "low", "description": "Low priority"},
                    {"value": "medium", "description": "Medium priority"},
                    {"value": "high", "description": "High priority"},
                    {"value": "urgent", "description": "Urgent priority"}
                ],
                suggested_option=1,
                resolution_question=f"Priority '{entities.get('priority')}' is not recognized. Did you mean low, medium, high, or urgent?"
            )
        
        if entities.get("status") and entities.get("status") not in ["pending", "in_progress", "completed"]:
            normalized = self._normalize_status(entities.get("status"))
            if normalized:
                return AmbiguityResolution(
                    ambiguity_type=AmbiguityType.PARAMETER_CONFLICT,
                    description=f"Status '{entities.get('status')}' normalized to '{normalized}'",
                    options=[{"value": normalized}],
                    suggested_option=0,
                    resolution_question=f"I'll interpret '{entities.get('status')}' as '{normalized}'. Is that correct?"
                )
        
        return None
    
    def _normalize_status(self, status: str) -> Optional[str]:
        status_lower = status.lower()
        for canonical, synonyms in self.STATUS_SYNONYMS.items():
            if status_lower == canonical or status_lower in synonyms:
                return canonical
        return None
    
    def generate_clarification_options(self, ambiguity: AmbiguityResolution) -> Dict[str, Any]:
        response = {
            "question": ambiguity.resolution_question,
            "options": ambiguity.options,
            "suggested": ambiguity.suggested_option,
            "response_hints": []
        }
        
        if ambiguity.ambiguity_type == AmbiguityType.MULTIPLE_MATCHES:
            for i, opt in enumerate(ambiguity.options):
                response["response_hints"].append(f"Say '{i + 1}' or '{opt.get('title', 'option ' + str(i + 1))}'")
        
        elif ambiguity.ambiguity_type == AmbiguityType.MISSING_ENTITY:
            response["response_hints"] = [
                "Provide the task title",
                "Describe the task",
                "Say 'list tasks' to see all tasks"
            ]
        
        elif ambiguity.ambiguity_type == AmbiguityType.UNCLEAR_INTENT:
            response["response_hints"] = [
                "Say 'create' to make a new task",
                "Say 'update' to modify a task",
                "Say 'delete' to remove a task",
                "Say 'list' to see all tasks"
            ]
        
        return response
    
    def resolve_from_follow_up(self, follow_up_input: str, ambiguity: AmbiguityResolution,
                               context: Optional[Dict[str, Any]] = None) -> Tuple[bool, Optional[Dict[str, Any]]]:
        follow_up_lower = follow_up_input.lower().strip()
        
        try:
            num = int(follow_up_lower)
            if 1 <= num <= len(ambiguity.options):
                return True, ambiguity.options[num - 1]
        except ValueError:
            pass
        
        for i, opt in enumerate(ambiguity.options):
            opt_text = str(opt.get("title", opt.get("value", opt.get("intent", "")))).lower()
            if opt_text and opt_text in follow_up_lower:
                return True, opt
        
        if ambiguity.suggested_option is not None:
            if any(word in follow_up_lower for word in ["yes", "yeah", "yep", "sure", "ok", "okay", "correct", "that one"]):
                return True, ambiguity.options[ambiguity.suggested_option]
        
        if any(word in follow_up_lower for word in ["none", "never mind", "cancel", "forget it"]):
            return True, {"action": "cancel"}
        
        return False, None
