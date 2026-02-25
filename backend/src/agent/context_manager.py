from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from sqlmodel import Session, select
import uuid


class ConversationContext(BaseModel):
    user_id: str
    last_task_id: Optional[str] = None
    pending_task: Optional[Dict[str, Any]] = None
    recent_tasks: List[Dict[str, Any]] = Field(default_factory=list)
    last_mentioned_task: Optional[Dict[str, Any]] = None
    conversation_turns: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(hours=24))
    
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at
    
    def add_turn(self, role: str, content: str, intent: Optional[str] = None, 
                 entities: Optional[Dict[str, Any]] = None):
        turn = {
            "role": role,
            "content": content,
            "intent": intent,
            "entities": entities or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        self.conversation_turns.append(turn)
        if len(self.conversation_turns) > 50:
            self.conversation_turns = self.conversation_turns[-50:]
        self.updated_at = datetime.utcnow()
    
    def set_pending_task(self, task_data: Dict[str, Any]):
        self.pending_task = task_data
        self.updated_at = datetime.utcnow()
    
    def clear_pending_task(self):
        self.pending_task = None
        self.updated_at = datetime.utcnow()
    
    def set_last_task_id(self, task_id: str):
        self.last_task_id = task_id
        self.updated_at = datetime.utcnow()
    
    def update_recent_tasks(self, tasks: List[Dict[str, Any]]):
        self.recent_tasks = tasks[:20]
        self.updated_at = datetime.utcnow()
    
    def set_last_mentioned_task(self, task: Dict[str, Any]):
        self.last_mentioned_task = task
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "last_task_id": self.last_task_id,
            "pending_task": self.pending_task,
            "recent_tasks": self.recent_tasks,
            "last_mentioned_task": self.last_mentioned_task,
            "conversation_turns": self.conversation_turns,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": self.expires_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationContext":
        return cls(
            user_id=data.get("user_id", ""),
            last_task_id=data.get("last_task_id"),
            pending_task=data.get("pending_task"),
            recent_tasks=data.get("recent_tasks", []),
            last_mentioned_task=data.get("last_mentioned_task"),
            conversation_turns=data.get("conversation_turns", []),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.utcnow(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.utcnow(),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else datetime.utcnow() + timedelta(hours=24)
        )


class FollowUpContextManager:
    _contexts: Dict[str, ConversationContext] = {}
    
    def __init__(self, session_factory):
        self.session_factory = session_factory
    
    def get_context(self, user_id: str) -> Optional[ConversationContext]:
        if user_id in self._contexts:
            context = self._contexts[user_id]
            if not context.is_expired():
                return context
            else:
                del self._contexts[user_id]
        
        with self.session_factory() as session:
            from ..models.agent import AgentSession
            stmt = select(AgentSession).where(AgentSession.user_id == uuid.UUID(user_id))
            agent_session = session.exec(stmt).first()
            
            if agent_session and agent_session.is_active:
                context_data = agent_session.context or {}
                context = ConversationContext.from_dict(context_data)
                if not context.is_expired():
                    self._contexts[user_id] = context
                    return context
                else:
                    agent_session.is_active = False
                    session.add(agent_session)
                    session.commit()
        
        return None
    
    def create_context(self, user_id: str) -> ConversationContext:
        context = ConversationContext(user_id=user_id)
        self._contexts[user_id] = context
        
        with self.session_factory() as session:
            from ..models.agent import AgentSession
            agent_session = AgentSession(
                user_id=uuid.UUID(user_id),
                session_id=str(uuid.uuid4()),
                context=context.to_dict()
            )
            session.add(agent_session)
            session.commit()
        
        return context
    
    def update_context(self, user_id: str, context: ConversationContext) -> None:
        context.updated_at = datetime.utcnow()
        self._contexts[user_id] = context
        
        with self.session_factory() as session:
            from ..models.agent import AgentSession
            stmt = select(AgentSession).where(AgentSession.user_id == uuid.UUID(user_id))
            agent_session = session.exec(stmt).first()
            
            if agent_session:
                agent_session.context = context.to_dict()
                agent_session.last_activity_at = datetime.utcnow()
                session.add(agent_session)
                session.commit()
    
    def add_conversation_turn(self, user_id: str, role: str, content: str, 
                              intent: Optional[str] = None, 
                              entities: Optional[Dict[str, Any]] = None) -> ConversationContext:
        context = self.get_context(user_id)
        if not context:
            context = self.create_context(user_id)
        
        context.add_turn(role, content, intent, entities)
        self.update_context(user_id, context)
        return context
    
    def set_pending_confirmation(self, user_id: str, task_data: Dict[str, Any]) -> ConversationContext:
        context = self.get_context(user_id)
        if not context:
            context = self.create_context(user_id)
        
        context.set_pending_task(task_data)
        self.update_context(user_id, context)
        return context
    
    def clear_pending_confirmation(self, user_id: str) -> None:
        context = self.get_context(user_id)
        if context:
            context.clear_pending_task()
            self.update_context(user_id, context)
    
    def get_pending_confirmation(self, user_id: str) -> Optional[Dict[str, Any]]:
        context = self.get_context(user_id)
        if context:
            return context.pending_task
        return None
    
    def update_recent_tasks(self, user_id: str, tasks: List[Dict[str, Any]]) -> None:
        context = self.get_context(user_id)
        if context:
            context.update_recent_tasks(tasks)
            self.update_context(user_id, context)
    
    def get_conversation_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        context = self.get_context(user_id)
        if context:
            return context.conversation_turns[-limit:]
        return []
    
    def resolve_follow_up_reference(self, user_id: str, reference: str) -> Optional[Dict[str, Any]]:
        context = self.get_context(user_id)
        if not context:
            return None
        
        reference_lower = reference.lower().strip()
        
        if reference_lower in ["this", "it", "the task", "that"]:
            if context.pending_task:
                return context.pending_task
            if context.last_mentioned_task:
                return context.last_mentioned_task
            if context.last_task_id:
                for task in context.recent_tasks:
                    if task.get("id") == context.last_task_id:
                        return task
        
        if reference_lower in ["these", "those", "all tasks"]:
            return {"type": "all", "tasks": context.recent_tasks}
        
        if reference_lower.startswith("the ") and reference_lower.endswith(" one"):
            if context.recent_tasks:
                return context.recent_tasks[-1]
        
        return None
    
    def cleanup_expired(self) -> int:
        expired_count = 0
        to_remove = []
        
        for user_id, context in self._contexts.items():
            if context.is_expired():
                to_remove.append(user_id)
        
        for user_id in to_remove:
            del self._contexts[user_id]
            expired_count += 1
        
        with self.session_factory() as session:
            from ..models.agent import AgentSession
            cutoff = datetime.utcnow() - timedelta(hours=24)
            stmt = select(AgentSession).where(AgentSession.last_activity_at < cutoff)
            expired_sessions = session.exec(stmt).all()
            
            for sess in expired_sessions:
                sess.is_active = False
                session.add(sess)
            
            session.commit()
        
        return expired_count
