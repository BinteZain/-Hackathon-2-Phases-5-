# Chatbot Database Schema

**Version**: 1.0.0  
**Status**: Draft  
**Created**: 2026-02-17  
**Last Updated**: 2026-02-17  

---

## 1. Overview

This document defines the database schema for the Todo AI Chatbot conversation system. The schema is designed for simplicity and performance, with user isolation enforced at the database level.

---

## 2. Schema Diagram

```
┌─────────────────┐         ┌─────────────────┐
│   conversations │         │      users      │
├─────────────────┤         ├─────────────────┤
│ id (PK)         │         │ id (PK)         │
│ user_id (FK)    │◀────────│ email           │
│ created_at      │         │ ...             │
│ updated_at      │         └─────────────────┘
└─────────────────┘
        │
        │ 1:N
        ▼
┌─────────────────┐
│    messages     │
├─────────────────┤
│ id (PK)         │
│ user_id (FK)    │
│ conversation_id │
│ role            │
│ content         │
│ created_at      │
└─────────────────┘
```

---

## 3. Table Definitions

### 3.1 `conversations` Table

Stores conversation sessions between users and the AI chatbot.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique conversation identifier |
| `user_id` | UUID | NOT NULL, FOREIGN KEY → user.id | Owner of the conversation |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | When conversation was created |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last message timestamp |

**Indexes**:
- `idx_conversations_user_id` on `user_id`
- `idx_conversations_created_at` on `created_at`

**Constraints**:
- Foreign key on `user_id` references `user(id)` with `ON DELETE CASCADE`

---

### 3.2 `messages` Table

Stores individual messages within conversations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique message identifier |
| `user_id` | UUID | NOT NULL, FOREIGN KEY → user.id | Message owner (for isolation) |
| `conversation_id` | INTEGER | NOT NULL, FOREIGN KEY → conversations.id | Parent conversation |
| `role` | TEXT | NOT NULL, CHECK IN ('user', 'assistant') | Message sender |
| `content` | TEXT | NOT NULL | Message content (max 10000 chars) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | When message was sent |

**Indexes**:
- `idx_messages_user_id` on `user_id`
- `idx_messages_conversation_id` on `conversation_id`
- `idx_messages_created_at` on `created_at`
- `idx_messages_user_conversation` on `(user_id, conversation_id)` (composite)

**Constraints**:
- Foreign key on `user_id` references `user(id)` with `ON DELETE CASCADE`
- Foreign key on `conversation_id` references `conversations(id)` with `ON DELETE CASCADE`
- Check constraint: `role IN ('user', 'assistant')`

---

## 4. SQL DDL

### 4.1 PostgreSQL Migration

```sql
-- Create conversations table
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create index on user_id for efficient user-based queries
CREATE INDEX idx_conversations_user_id ON conversations(user_id);

-- Create index on created_at for sorting
CREATE INDEX idx_conversations_created_at ON conversations(created_at);

-- Create messages table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for efficient queries
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_user_conversation ON messages(user_id, conversation_id);

-- Trigger to update conversation.updated_at on new message
CREATE OR REPLACE FUNCTION update_conversation_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_conversation_timestamp
    AFTER INSERT ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_timestamp();
```

### 4.2 SQLite Migration (for local development)

```sql
-- Create conversations table
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at);

-- Create messages table
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_user_conversation ON messages(user_id, conversation_id);

-- SQLite trigger for conversation timestamp update
CREATE TRIGGER update_conversation_timestamp 
AFTER INSERT ON messages
BEGIN
    UPDATE conversations 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.conversation_id;
END;
```

---

## 5. SQLModel Definitions

### 5.1 Conversation Model

```python
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func
from datetime import datetime
from typing import TYPE_CHECKING, Optional, List
import uuid


class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", 
        nullable=False, 
        index=True,
        description="Owner of the conversation"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )
    
    # Relationships
    messages: Optional[List["Message"]] = Relationship(
        back_populates="conversation",
        cascade_delete=True
    )
```

### 5.2 Message Model

```python
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, Text, CheckConstraint, func
from datetime import datetime
from typing import TYPE_CHECKING, Optional
import uuid
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class Message(SQLModel, table=True):
    __tablename__ = "messages"
    
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant')", name="check_message_role"),
    )
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id",
        nullable=False,
        index=True,
        description="Message owner for isolation"
    )
    conversation_id: int = Field(
        foreign_key="conversations.id",
        nullable=False,
        index=True,
        description="Parent conversation"
    )
    role: MessageRole = Field(
        default=MessageRole.USER,
        description="Message sender (user or assistant)"
    )
    content: str = Field(
        min_length=1,
        max_length=10000,
        sa_column=Column(Text, nullable=False),
        description="Message content"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, server_default=func.now())
    )
    
    # Relationships
    conversation: Optional["Conversation"] = Relationship(
        back_populates="messages"
    )
```

### 5.3 Pydantic Schemas for API

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
import uuid


class MessageRoleEnum(str):
    USER = "user"
    ASSISTANT = "assistant"


class MessageCreate(BaseModel):
    role: MessageRoleEnum
    content: str = Field(min_length=1, max_length=10000)


class MessageRead(BaseModel):
    id: int
    user_id: uuid.UUID
    conversation_id: int
    role: str
    content: str
    created_at: datetime


class ConversationCreate(BaseModel):
    user_id: uuid.UUID


class ConversationRead(BaseModel):
    id: int
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    messages: Optional[List[MessageRead]] = None


class ConversationListResponse(BaseModel):
    success: bool
    conversations: List[ConversationRead]
    total: int
```

---

## 6. Common Queries

### 6.1 Create New Conversation

```sql
INSERT INTO conversations (user_id)
VALUES ($1)
RETURNING id, created_at, updated_at;
```

### 6.2 Add Message to Conversation

```sql
INSERT INTO messages (user_id, conversation_id, role, content)
VALUES ($1, $2, $3, $4)
RETURNING id, created_at;
```

### 6.3 Get Messages for Conversation (with user isolation)

```sql
SELECT m.id, m.user_id, m.conversation_id, m.role, m.content, m.created_at
FROM messages m
INNER JOIN conversations c ON m.conversation_id = c.id
WHERE m.conversation_id = $1 
  AND c.user_id = $2  -- Enforce user isolation
ORDER BY m.created_at ASC
LIMIT $3 OFFSET $4;
```

### 6.4 Get Recent Conversations for User

```sql
SELECT c.id, c.user_id, c.created_at, c.updated_at,
       COUNT(m.id) as message_count
FROM conversations c
LEFT JOIN messages m ON c.id = m.conversation_id
WHERE c.user_id = $1
GROUP BY c.id, c.user_id, c.created_at, c.updated_at
ORDER BY c.updated_at DESC
LIMIT $2 OFFSET $3;
```

### 6.5 Get Latest Message in Conversation

```sql
SELECT role, content, created_at
FROM messages
WHERE conversation_id = $1
  AND user_id = $2  -- Enforce user isolation
ORDER BY created_at DESC
LIMIT 1;
```

### 6.6 Delete Old Conversations (Cleanup)

```sql
DELETE FROM conversations
WHERE user_id = $1
  AND created_at < $2;  -- e.g., older than 90 days
-- Messages cascade delete automatically
```

---

## 7. User Isolation Enforcement

### 7.1 Query Pattern

All queries MUST include user_id filtering:

```sql
-- CORRECT: User isolation enforced
SELECT m.* 
FROM messages m
JOIN conversations c ON m.conversation_id = c.id
WHERE c.user_id = :user_id  -- ✓ Enforced
  AND m.conversation_id = :conversation_id;

-- INCORRECT: Missing user isolation
SELECT * FROM messages 
WHERE conversation_id = :conversation_id;  -- ✗ No user check
```

### 7.2 Application-Level Enforcement

```python
async def get_messages(
    conversation_id: int, 
    user_id: uuid.UUID,
    session: Session
) -> List[Message]:
    """
    Get messages with user isolation.
    """
    statement = (
        select(Message)
        .join(Conversation)
        .where(
            Message.conversation_id == conversation_id,
            Conversation.user_id == user_id  # Enforce isolation
        )
        .order_by(Message.created_at.asc())
    )
    return session.exec(statement).all()
```

---

## 8. Data Retention

| Data Type | Retention Period | Cleanup Method |
|-----------|-----------------|----------------|
| Conversations | 90 days of inactivity | Scheduled job deletes conversations with `updated_at < NOW() - INTERVAL '90 days'` |
| Messages | Tied to conversation | Cascade delete with parent conversation |

### 8.1 Cleanup Job

```sql
-- Run daily via cron or scheduled task
DELETE FROM conversations
WHERE updated_at < NOW() - INTERVAL '90 days';
```

---

## 9. Performance Considerations

### 9.1 Indexing Strategy

| Query Pattern | Index |
|---------------|-------|
| Get user's conversations | `idx_conversations_user_id` |
| Get conversation messages | `idx_messages_conversation_id` |
| Get user's messages | `idx_messages_user_id` |
| Get messages with isolation | `idx_messages_user_conversation` (composite) |
| Sort by time | `idx_messages_created_at`, `idx_conversations_created_at` |

### 9.2 Expected Scale

| Metric | Estimate |
|--------|----------|
| Conversations per user | 10-50 active |
| Messages per conversation | 20-100 |
| Total messages per user | 500-5000 |
| Read latency (p95) | < 50ms |
| Write latency (p95) | < 20ms |

---

## 10. Migration from Existing Models

### 10.1 Relationship to Agent Models

The existing models in `backend/src/models/agent.py` remain for agent task tracking:

- `AgentTask` - Continues to track agent task execution
- `ToolExecution` - Records tool invocations
- `AgentSession` - Session management (may be deprecated)

The new `Conversation` and `Message` models are simpler and focused on chat history.

### 10.2 Data Migration (if needed)

```sql
-- Optional: Migrate existing ConversationTurn data
INSERT INTO messages (user_id, conversation_id, role, content, created_at)
SELECT 
    at.user_id,
    c.id,
    ct.role,
    ct.content,
    ct.created_at
FROM conversation_turn ct
JOIN agent_task at ON ct.agent_task_id = at.id
JOIN conversations c ON at.user_id = c.user_id;
```

---

## 11. References

- Chatbot Feature Spec: `specs/features/chatbot.md`
- MCP Tools Spec: `specs/api/mcp-tools.md`
- Constitution: `.specify/memory/constitution.md`
- Existing Agent Models: `backend/src/models/agent.py`

---

**Document Status**: Ready for Implementation  
**Migration File**: `backend/migrations/versions/XXXX_add_chatbot_schema.py`
