# Phase III: Todo AI Chatbot

**Version**: 1.0.0  
**Status**: Draft  
**Created**: 2026-02-17  
**Last Updated**: 2026-02-17  

---

## 1. Overview

### 1.1 Purpose

This document specifies the requirements for an AI-powered chatbot interface that enables users to perform CRUD operations on their todo tasks using natural language conversations. The chatbot leverages the OpenAI Agents SDK and MCP (Model Context Protocol) tools to provide an intelligent, conversational task management experience.

### 1.2 Goals

- Provide a natural language interface for task management
- Enable users to create, read, update, complete, and delete tasks via conversation
- Maintain conversation history for context-aware follow-ups
- Implement confirmation flows for destructive operations
- Support stateless chat sessions with database-backed persistence

### 1.3 Non-Goals

- Voice-based interactions (future phase)
- Multi-language support beyond English (future phase)
- Integration with external calendar systems (future phase)
- Group/collaborative task management via chatbot (future phase)

---

## 2. Architecture

### 2.1 System Components

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   Chat API Gateway   │────▶│  OpenAI Agent   │
│   (React/Next)  │◀────│   (FastAPI)          │◀────│  (Agents SDK)   │
└─────────────────┘     └──────────────────────┘     └────────┬────────┘
                                                              │
                                                              ▼
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│   PostgreSQL    │◀────│   MCP Tool Layer     │◀────│  Tool Router    │
│   (Messages,    │     │   (add_task,         │     │                 │
│   Conversations)│     │    list_tasks,       │     │                 │
│                 │     │    update_task,      │     │                 │
│                 │     │    complete_task,    │     │                 │
│                 │     │    delete_task)      │     │                 │
└─────────────────┘     └──────────────────────┘     └─────────────────┘
```

### 2.2 Technology Stack

| Component | Technology | Justification |
|-----------|------------|---------------|
| Agent Framework | OpenAI Agents SDK | Official OpenAI library for agent orchestration, built-in tool calling |
| API Framework | FastAPI | Async support, automatic OpenAPI docs, existing backend compatibility |
| Database | PostgreSQL (existing) | Reuse existing infrastructure, ACID compliance |
| ORM | SQLModel | Type-safe, compatible with existing models |
| Authentication | JWT (existing) | Consistent with current auth system |
| MCP Protocol | Custom Implementation | Direct tool integration with confirmation flows |

### 2.3 Dependencies

- `openai-agents-sdk` >= 0.1.0
- `openai` >= 1.0.0
- Existing backend dependencies (FastAPI, SQLModel, psycopg2)

---

## 3. Database Models

### 3.1 Conversation Model

```python
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, index=True)
    session_id: str = Field(max_length=100, unique=True, index=True)
    title: Optional[str] = Field(default=None, max_length=255)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_message_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    messages: Optional[List["Message"]] = Relationship(back_populates="conversation")
```

### 3.2 Message Model

```python
class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(SQLModel, table=True):
    __tablename__ = "messages"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversations.id", nullable=False, index=True)
    role: MessageRole = Field(default=MessageRole.USER)
    content: str = Field(min_length=1, max_length=10000)
    
    # Agent metadata
    intent: Optional[str] = Field(default=None, max_length=200)
    entities: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    tool_calls: Optional[List[Dict[str, Any]]] = Field(default=None, sa_type=JSON)
    tool_results: Optional[List[Dict[str, Any]]] = Field(default=None, sa_type=JSON)
    
    # Confirmation tracking
    requires_confirmation: bool = Field(default=False)
    confirmation_status: Optional[ConfirmationType] = Field(default=None)
    pending_action: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
```

### 3.3 Existing Models (Reuse)

The following models from `backend/src/models/agent.py` are reused:

- `AgentTask` - Tracks agent task execution
- `ToolExecution` - Records individual tool invocations
- `ConversationTurn` - Alternative conversation history model (may be deprecated)
- `AgentSession` - Session management

---

## 4. MCP Tools Specification

### 4.1 Tool Definitions

All MCP tools follow a consistent interface with explicit input/output contracts.

#### 4.1.1 `add_task`

**Description**: Creates a new task in the user's todo list.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `title` | string | Yes | Task title (1-255 characters) |
| `description` | string | No | Optional task description (max 500 chars) |
| `priority` | string | No | Priority level: `low`, `medium`, `high`, `urgent` (default: `medium`) |
| `due_date` | string (ISO 8601) | No | Due date with timezone |

**Returns**:
```json
{
  "success": true,
  "task": {
    "id": "uuid",
    "title": "string",
    "description": "string|null",
    "status": "pending",
    "priority": "string",
    "due_date": "datetime|null",
    "created_at": "datetime",
    "user_id": "uuid"
  }
}
```

**Confirmation Required**: No (non-destructive)

**Error Codes**:
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid input parameters |
| `AUTHENTICATION_ERROR` | 401 | Invalid or missing JWT token |
| `DATABASE_ERROR` | 500 | Database operation failed |

---

#### 4.1.2 `list_tasks`

**Description**: Retrieves all tasks for the authenticated user with optional filtering.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `status` | string | No | Filter by status: `pending`, `in_progress`, `completed` |
| `priority` | string | No | Filter by priority |
| `limit` | integer | No | Maximum results (default: 50, max: 100) |
| `offset` | integer | No | Pagination offset (default: 0) |

**Returns**:
```json
{
  "success": true,
  "tasks": [
    {
      "id": "uuid",
      "title": "string",
      "description": "string|null",
      "status": "string",
      "priority": "string",
      "due_date": "datetime|null",
      "created_at": "datetime",
      "user_id": "uuid"
    }
  ],
  "total": 10,
  "has_more": false
}
```

**Confirmation Required**: No (read-only)

**Error Codes**:
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AUTHENTICATION_ERROR` | 401 | Invalid or missing JWT token |
| `DATABASE_ERROR` | 500 | Database query failed |

---

#### 4.1.3 `update_task`

**Description**: Updates an existing task's properties.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `task_id` | string (UUID) | Yes | ID of task to update |
| `title` | string | No | New title |
| `description` | string | No | New description |
| `status` | string | No | New status: `pending`, `in_progress`, `completed` |
| `priority` | string | No | New priority level |
| `due_date` | string (ISO 8601) | No | New due date |

**Returns**:
```json
{
  "success": true,
  "task": {
    "id": "uuid",
    "title": "string",
    "description": "string|null",
    "status": "string",
    "priority": "string",
    "due_date": "datetime|null",
    "updated_at": "datetime",
    "user_id": "uuid"
  }
}
```

**Confirmation Required**: No (reversible operation)

**Error Codes**:
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `NOT_FOUND` | 404 | Task with given ID does not exist |
| `FORBIDDEN` | 403 | User does not own this task |
| `VALIDATION_ERROR` | 400 | Invalid update parameters |
| `AUTHENTICATION_ERROR` | 401 | Invalid or missing JWT token |

---

#### 4.1.4 `complete_task`

**Description**: Marks a task as completed (sets status to `completed` and records completion timestamp).

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `task_id` | string (UUID) | Yes | ID of task to complete |

**Returns**:
```json
{
  "success": true,
  "task": {
    "id": "uuid",
    "title": "string",
    "status": "completed",
    "completed_at": "datetime",
    "user_id": "uuid"
  },
  "message": "Task completed successfully"
}
```

**Confirmation Required**: No (reversible via update)

**Error Codes**:
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `NOT_FOUND` | 404 | Task does not exist |
| `FORBIDDEN` | 403 | User does not own this task |
| `ALREADY_COMPLETED` | 400 | Task is already completed |
| `AUTHENTICATION_ERROR` | 401 | Invalid or missing JWT token |

---

#### 4.1.5 `delete_task`

**Description**: Permanently deletes a task from the user's todo list.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `task_id` | string (UUID) | Yes | ID of task to delete |

**Returns**:
```json
{
  "success": true,
  "deleted": true,
  "task_id": "uuid",
  "message": "Task deleted successfully"
}
```

**Confirmation Required**: **Yes** (destructive operation)

**Confirmation Message Template**:
```
Are you sure you want to delete the task "{task_title}"? This action cannot be undone.
```

**Error Codes**:
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `NOT_FOUND` | 404 | Task does not exist |
| `FORBIDDEN` | 403 | User does not own this task |
| `AUTHENTICATION_ERROR` | 401 | Invalid or missing JWT token |

---

### 4.2 Tool Registration

```python
def register_mcp_tools(agent: Agent, task_service: TaskService) -> None:
    """Register all MCP tools with the OpenAI Agent."""
    
    @agent.tool
    async def add_task(title: str, description: str = None, 
                       priority: str = "medium", due_date: str = None) -> dict:
        return await task_service.create_task(
            user_id=agent.context["user_id"],
            task_data={"title": title, "description": description, 
                      "priority": priority, "due_date": due_date}
        )
    
    @agent.tool
    async def list_tasks(status: str = None, priority: str = None,
                         limit: int = 50, offset: int = 0) -> dict:
        return await task_service.list_tasks(
            user_id=agent.context["user_id"],
            filters={"status": status, "priority": priority},
            limit=limit, offset=offset
        )
    
    @agent.tool
    async def update_task(task_id: str, **updates) -> dict:
        return await task_service.update_task(
            user_id=agent.context["user_id"],
            task_id=task_id,
            update_data=updates
        )
    
    @agent.tool
    async def complete_task(task_id: str) -> dict:
        return await task_service.complete_task(
            user_id=agent.context["user_id"],
            task_id=task_id
        )
    
    @agent.tool
    async def delete_task(task_id: str, confirmed: bool = False) -> dict:
        if not confirmed:
            return {
                "requires_confirmation": True,
                "confirmation_prompt": f"Are you sure you want to delete task {task_id}?"
            }
        return await task_service.delete_task(
            user_id=agent.context["user_id"],
            task_id=task_id
        )
```

---

## 5. API Specification

### 5.1 Chat Endpoint

#### POST `/api/v1/chat/message`

Sends a message to the chatbot and receives a response.

**Request Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "content": "Add a task to buy groceries tomorrow",
  "session_id": "optional-session-id-uuid"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `content` | string | Yes | User's message content (1-10000 chars) |
| `session_id` | string | No | Existing session ID for conversation continuity |

**Response (Success - No Confirmation Needed)**:
```json
{
  "success": true,
  "message_id": "uuid",
  "conversation_id": "uuid",
  "session_id": "uuid",
  "response": {
    "content": "I've added 'Buy groceries' to your todo list for tomorrow.",
    "intent": "create_task",
    "entities": {
      "title": "Buy groceries",
      "due_date": "2026-02-18"
    }
  },
  "tool_results": [
    {
      "tool_name": "add_task",
      "success": true,
      "data": {"task_id": "uuid", "title": "Buy groceries"}
    }
  ],
  "requires_confirmation": false,
  "created_at": "2026-02-17T10:30:00Z"
}
```

**Response (Confirmation Required)**:
```json
{
  "success": true,
  "message_id": "uuid",
  "conversation_id": "uuid",
  "session_id": "uuid",
  "response": {
    "content": "I'm ready to delete the task 'Old meeting notes'. Please confirm this action.",
    "intent": "delete_task",
    "pending_action": {
      "tool": "delete_task",
      "params": {"task_id": "uuid"}
    }
  },
  "requires_confirmation": true,
  "confirmation_prompt": "Are you sure you want to delete 'Old meeting notes'? This cannot be undone.",
  "pending_action_id": "uuid",
  "created_at": "2026-02-17T10:30:00Z"
}
```

**Response (Error)**:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Content is required and cannot be empty",
    "details": {"field": "content", "issue": "min_length"}
  },
  "created_at": "2026-02-17T10:30:00Z"
}
```

**Error Codes**:
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request body |
| `AUTHENTICATION_ERROR` | 401 | Invalid or missing JWT token |
| `SESSION_NOT_FOUND` | 404 | Provided session_id does not exist |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests (limit: 60/min) |
| `AGENT_ERROR` | 500 | OpenAI Agent processing failed |
| `DATABASE_ERROR` | 500 | Database operation failed |

---

#### POST `/api/v1/chat/confirm`

Confirms or rejects a pending action that requires confirmation.

**Request Body**:
```json
{
  "session_id": "session-id-uuid",
  "action_id": "pending-action-uuid",
  "confirmed": true,
  "modifications": null
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | string | Yes | Session ID from previous response |
| `action_id` | string | Yes | ID of pending action to confirm |
| `confirmed` | boolean | Yes | Whether user confirms the action |
| `modifications` | object | No | Optional modifications to the action |

**Response (Confirmed)**:
```json
{
  "success": true,
  "message_id": "uuid",
  "response": {
    "content": "Task 'Old meeting notes' has been deleted.",
    "intent": "delete_task_completed"
  },
  "tool_results": [
    {
      "tool_name": "delete_task",
      "success": true,
      "data": {"deleted": true}
    }
  ],
  "created_at": "2026-02-17T10:31:00Z"
}
```

**Response (Rejected)**:
```json
{
  "success": true,
  "message_id": "uuid",
  "response": {
    "content": "Okay, I won't delete the task. It's still in your todo list.",
    "intent": "delete_task_cancelled"
  },
  "action_status": "rejected",
  "created_at": "2026-02-17T10:31:00Z"
}
```

---

#### GET `/api/v1/chat/sessions`

Lists all active chat sessions for the authenticated user.

**Query Parameters**:
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `limit` | integer | 20 | Maximum sessions to return |
| `offset` | integer | 0 | Pagination offset |
| `include_inactive` | boolean | false | Include inactive sessions |

**Response**:
```json
{
  "success": true,
  "sessions": [
    {
      "session_id": "uuid",
      "title": "Task Management Chat",
      "last_message_at": "2026-02-17T10:30:00Z",
      "message_count": 15,
      "is_active": true
    }
  ],
  "total": 5,
  "has_more": false
}
```

---

#### DELETE `/api/v1/chat/sessions/{session_id}`

Deletes a chat session and all associated messages.

**Response**:
```json
{
  "success": true,
  "message": "Session deleted successfully",
  "session_id": "uuid"
}
```

---

#### GET `/api/v1/chat/sessions/{session_id}/messages`

Retrieves message history for a specific session.

**Query Parameters**:
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `limit` | integer | 50 | Maximum messages to return |
| `before` | datetime | null | Get messages before this timestamp |

**Response**:
```json
{
  "success": true,
  "messages": [
    {
      "id": "uuid",
      "role": "user",
      "content": "Add a task to buy groceries",
      "intent": "create_task",
      "entities": {"title": "buy groceries"},
      "created_at": "2026-02-17T10:30:00Z"
    },
    {
      "id": "uuid",
      "role": "assistant",
      "content": "I've added 'Buy groceries' to your todo list.",
      "intent": "create_task_completed",
      "tool_results": [{"tool_name": "add_task", "success": true}],
      "created_at": "2026-02-17T10:30:01Z"
    }
  ],
  "has_more": false
}
```

---

## 6. Conversational Interface Design

### 6.1 Intent Recognition

The chatbot recognizes the following intents from natural language input:

| Intent | Example Utterances | Mapped Tool |
|--------|-------------------|-------------|
| `create_task` | "Add a task to...", "I need to...", "Remind me to..." | `add_task` |
| `list_tasks` | "Show my tasks", "What do I have pending?", "List todos" | `list_tasks` |
| `update_task` | "Change the title of...", "Update my task...", "Edit task..." | `update_task` |
| `complete_task` | "Mark as done", "I finished...", "Complete task..." | `complete_task` |
| `delete_task` | "Delete task...", "Remove...", "Cancel this todo" | `delete_task` |
| `clarify_task` | "Which task?", "Tell me more about..." | N/A (follow-up) |
| `greeting` | "Hello", "Hi", "Good morning" | N/A (conversational) |
| `help` | "What can you do?", "Help me" | N/A (informational) |

### 6.2 Entity Extraction

The chatbot extracts the following entities from user input:

| Entity | Description | Examples |
|--------|-------------|----------|
| `task_title` | The title/name of a task | "Buy groceries", "Team meeting" |
| `task_id` | Reference to existing task | "the first task", "that meeting thing" |
| `priority` | Task priority level | "urgent", "high priority" |
| `due_date` | When task is due | "tomorrow", "next Friday", "in 2 hours" |
| `status` | Task completion status | "done", "pending", "in progress" |
| `description` | Additional task details | "at the supermarket", "with the team" |

### 6.3 Conversation Flows

#### 6.3.1 Simple Task Creation (No Confirmation)

```
User: "Add a task to call the dentist tomorrow"
Assistant: "I've added 'Call the dentist' to your todo list for tomorrow."
```

#### 6.3.2 Task Creation with Missing Information

```
User: "Add a task for the presentation"
Assistant: "Sure! When is the presentation due?"
User: "Next Friday"
Assistant: "Got it. I've added 'Prepare presentation' with due date next Friday."
```

#### 6.3.3 Destructive Operation (Confirmation Required)

```
User: "Delete the task about old meeting notes"
Assistant: "I found the task 'Old meeting notes' from Jan 15. Are you sure you want to delete it? This cannot be undone."
User: "Yes, delete it"
Assistant: "Task 'Old meeting notes' has been deleted."
```

#### 6.3.4 Ambiguous Task Reference (Clarification Required)

```
User: "Update the meeting task"
Assistant: "I found 3 tasks with 'meeting' in the title:
  1. Team meeting notes (Jan 10)
  2. Client meeting prep (due tomorrow)
  3. Weekly sync (recurring)
Which one would you like to update?"
User: "The second one"
Assistant: "Got it. What would you like to update about 'Client meeting prep'?"
```

#### 6.3.5 Follow-up Context Resolution

```
User: "Add a task to finish the report"
Assistant: "I've added 'Finish the report' to your todo list."
User: "Make it high priority"
Assistant: "Updated! 'Finish the report' is now marked as high priority."
```

### 6.4 Confirmation Behavior

#### 6.4.1 Operations Requiring Confirmation

| Operation | Confirmation Trigger | Confirmation Message |
|-----------|---------------------|---------------------|
| `delete_task` | Any delete request | "Are you sure you want to delete '{task_title}'? This cannot be undone." |
| `bulk_delete` | Deleting >3 tasks | "You're about to delete {count} tasks. This will permanently remove: {task_list}. Continue?" |
| `bulk_complete` | Completing >5 tasks | "Mark {count} tasks as completed? This includes: {task_list}." |

#### 6.4.2 Confirmation Response Handling

```python
CONFIRMATION_PATTERNS = {
    "affirmative": ["yes", "yeah", "sure", "go ahead", "confirm", "do it", "ok", "okay"],
    "negative": ["no", "nope", "cancel", "nevermind", "don't", "dont"],
    "modify": ["actually", "wait", "change", "instead"]
}

def parse_confirmation_response(user_input: str) -> ConfirmationType:
    """Parse user's confirmation response."""
    normalized = user_input.lower().strip()
    
    if any(pattern in normalized for pattern in CONFIRMATION_PATTERNS["affirmative"]):
        return ConfirmationType.APPROVE
    elif any(pattern in normalized for pattern in CONFIRMATION_PATTERNS["negative"]):
        return ConfirmationType.REJECT
    elif any(pattern in normalized for pattern in CONFIRMATION_PATTERNS["modify"]):
        return ConfirmationType.MODIFY
    else:
        return ConfirmationType.REJECT  # Default to reject on ambiguity
```

#### 6.4.3 Confirmation Timeout

- Pending confirmations expire after **24 hours**
- Expired confirmations are automatically rejected
- User is notified if attempting to confirm an expired action

---

## 7. Error Handling

### 7.1 Error Categories

#### 7.1.1 User Errors (4xx)

| Error | Cause | Response Strategy |
|-------|-------|-------------------|
| `INVALID_INPUT` | Empty content, invalid parameters | Return validation error with field details |
| `TASK_NOT_FOUND` | Referenced task doesn't exist | "I couldn't find a task with that ID/name" |
| `UNAUTHORIZED` | Missing/invalid JWT | Return 401, prompt to re-login |
| `FORBIDDEN` | User doesn't own task | "You don't have permission to modify this task" |
| `AMBIGUOUS_REFERENCE` | Multiple tasks match reference | List matching tasks, ask for clarification |

#### 7.1.2 System Errors (5xx)

| Error | Cause | Response Strategy |
|-------|-------|-------------------|
| `DATABASE_ERROR` | DB connection/query failure | "Sorry, I'm having trouble saving that. Please try again." |
| `AGENT_ERROR` | OpenAI Agent processing failure | "I encountered an error processing your request. Please try again." |
| `RATE_LIMIT_EXCEEDED` | Too many requests | "You're sending messages too quickly. Please wait a moment." |
| `EXTERNAL_SERVICE_ERROR` | OpenAI API unavailable | "I'm temporarily unable to process requests. Please try again in a few moments." |

### 7.2 Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "field_name",
      "issue": "specific_issue",
      "suggestion": "how_to_fix"
    }
  },
  "retryable": true,
  "created_at": "2026-02-17T10:30:00Z"
}
```

### 7.3 Retry Logic

```python
RETRY_CONFIG = {
    "max_retries": 3,
    "initial_delay_ms": 1000,
    "max_delay_ms": 10000,
    "backoff_multiplier": 2,
    "retryable_errors": [
        "DATABASE_ERROR",
        "AGENT_ERROR",
        "EXTERNAL_SERVICE_ERROR"
    ]
}

async def execute_with_retry(operation: Callable, context: dict) -> dict:
    """Execute operation with exponential backoff retry."""
    attempt = 0
    delay = RETRY_CONFIG["initial_delay_ms"]
    
    while attempt < RETRY_CONFIG["max_retries"]:
        try:
            return await operation()
        except RetryableError as e:
            attempt += 1
            if attempt == RETRY_CONFIG["max_retries"]:
                raise
            await asyncio.sleep(delay / 1000)
            delay *= RETRY_CONFIG["backoff_multiplier"]
```

### 7.4 Error Logging

All errors are logged with the following context:

```python
error_log = {
    "timestamp": datetime.utcnow().isoformat(),
    "user_id": str(user_id),
    "session_id": session_id,
    "message_id": str(message_id),
    "error_code": error.code,
    "error_message": str(error),
    "stack_trace": traceback.format_exc(),
    "request_context": {
        "content": user_input[:100],  # First 100 chars only
        "intent": detected_intent,
        "tool_calls": tool_call_count
    }
}
```

---

## 8. Acceptance Criteria

### 8.1 Functional Requirements

#### AC-1: Task Creation via Natural Language
- [ ] User can create a task by saying "Add a task to [action]"
- [ ] System extracts title, priority, and due_date from input
- [ ] Created task is persisted to database
- [ ] User receives confirmation with task details
- [ ] Task appears in subsequent `list_tasks` results

#### AC-2: Task Listing
- [ ] User can request task list with "Show my tasks" or similar
- [ ] System returns all tasks for authenticated user
- [ ] Response includes task count and summary
- [ ] Optional filtering by status/priority works correctly

#### AC-3: Task Update
- [ ] User can update task properties by reference
- [ ] System correctly identifies target task
- [ ] Updates are persisted atomically
- [ ] User receives confirmation of changes

#### AC-4: Task Completion
- [ ] User can mark tasks complete with "done", "finished", etc.
- [ ] `completed_at` timestamp is recorded
- [ ] Task status changes to "completed"
- [ ] Completion is reflected in list views

#### AC-5: Task Deletion with Confirmation
- [ ] Delete requests trigger confirmation prompt
- [ ] Confirmation message includes task title
- [ ] Delete only proceeds after explicit confirmation
- [ ] User can reject deletion with "no", "cancel", etc.
- [ ] Rejected deletions leave task unchanged

#### AC-6: Conversation Continuity
- [ ] Follow-up messages reference previous context
- [ ] Pronouns ("it", "that", "them") resolve correctly
- [ ] Session persists across requests via `session_id`
- [ ] Conversation history is queryable via API

#### AC-7: Ambiguity Resolution
- [ ] Ambiguous references trigger clarification flow
- [ ] System lists matching options for user to choose
- [ ] Clarification responses are processed correctly

#### AC-8: Error Handling
- [ ] Invalid inputs return descriptive error messages
- [ ] System errors are logged with full context
- [ ] Retryable errors attempt recovery
- [ ] User-facing errors are human-readable

### 8.2 Non-Functional Requirements

#### AC-9: Performance
- [ ] Chat response time p95 < 2 seconds (excluding OpenAI latency)
- [ ] Message persistence completes within 100ms
- [ ] Session lookup completes within 50ms

#### AC-10: Security
- [ ] All endpoints require valid JWT authentication
- [ ] Users can only access their own tasks
- [ ] Conversation data is isolated per user
- [ ] Sensitive data is not logged

#### AC-11: Reliability
- [ ] System handles OpenAI API failures gracefully
- [ ] Database failures trigger retry logic
- [ ] Rate limiting prevents abuse (60 req/min per user)
- [ ] Session state survives server restarts

#### AC-12: Observability
- [ ] All agent decisions are logged with reasoning
- [ ] Tool executions record inputs/outputs
- [ ] Error events include stack traces
- [ ] Metrics exposed for response time, error rate, tool usage

### 8.3 Edge Cases

#### AC-13: Boundary Conditions
- [ ] Empty task title is rejected with validation error
- [ ] Task titles >255 chars are truncated or rejected
- [ ] Invalid dates are rejected with helpful error
- [ ] Non-existent task IDs return "not found" error
- [ ] Concurrent modifications use optimistic locking

#### AC-14: Session Management
- [ ] New session created if `session_id` not provided
- [ ] Inactive sessions (>30 days) are auto-archived
- [ ] Session deletion cascades to messages
- [ ] Maximum 100 active sessions per user

---

## 9. Implementation Notes

### 9.1 OpenAI Agent Configuration

```python
from openai.agents import Agent

def create_chatbot_agent() -> Agent:
    """Configure the OpenAI Agent for todo chatbot."""
    return Agent(
        name="TodoAssistant",
        instructions="""You are a helpful todo management assistant. You help users manage their tasks through natural conversation.
        
Guidelines:
- Be concise and friendly in responses
- Always confirm task operations with specific details
- Request clarification when task references are ambiguous
- For destructive operations (delete), always confirm before proceeding
- Extract dates, priorities, and descriptions from natural language
- Use ISO 8601 format for all dates
- Reference tasks by title when possible for clarity""",
        model="gpt-4o",
        tools=[add_task, list_tasks, update_task, complete_task, delete_task],
        tool_choice="auto",
        parallel_tool_calls=False
    )
```

### 9.2 Session Management

```python
async def get_or_create_session(
    db: Session, 
    user_id: uuid.UUID, 
    session_id: Optional[str] = None
) -> Conversation:
    """Get existing session or create new one."""
    if session_id:
        session = await db.get(Conversation, session_id)
        if session and session.user_id == user_id:
            session.last_message_at = datetime.utcnow()
            session.is_active = True
            await db.commit()
            return session
    
    # Create new session
    session = Conversation(
        user_id=user_id,
        session_id=str(uuid.uuid4()),
        title="New Chat",
        is_active=True,
        last_message_at=datetime.utcnow()
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session
```

### 9.3 Message Persistence

```python
async def persist_message(
    db: Session,
    conversation_id: uuid.UUID,
    role: MessageRole,
    content: str,
    metadata: dict = None
) -> Message:
    """Persist a chat message to the database."""
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        intent=metadata.get("intent") if metadata else None,
        entities=metadata.get("entities") if metadata else None,
        tool_calls=metadata.get("tool_calls") if metadata else None,
        tool_results=metadata.get("tool_results") if metadata else None,
        requires_confirmation=metadata.get("requires_confirmation", False),
        pending_action=metadata.get("pending_action") if metadata else None
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message
```

---

## 10. Testing Strategy

### 10.1 Unit Tests

| Test Suite | Coverage Target |
|------------|-----------------|
| MCP Tool Execution | 100% |
| Intent Recognition | 95% |
| Entity Extraction | 95% |
| Confirmation Parsing | 100% |
| Error Handling | 90% |

### 10.2 Integration Tests

| Test Scenario | Description |
|---------------|-------------|
| End-to-end task creation | User input → Agent → Tool → DB → Response |
| Confirmation flow | Delete request → Confirm → Execute |
| Session persistence | Message across multiple requests |
| Error recovery | Simulated DB failure → Retry → Success |

### 10.3 Conversation Tests

Test the following conversation patterns:

```gherkin
Scenario: Create task with natural language
  Given user is authenticated
  When user sends "Add a task to call mom tomorrow at 3pm"
  Then task is created with title "Call mom"
  And due_date is set to tomorrow 15:00
  And response confirms task creation

Scenario: Delete with confirmation
  Given user has a task "Old notes"
  When user sends "Delete the old notes task"
  Then system asks for confirmation
  When user responds "yes"
  Then task is deleted
  And response confirms deletion

Scenario: Ambiguous reference
  Given user has 3 tasks containing "meeting"
  When user sends "Update the meeting task"
  Then system lists all 3 matching tasks
  And asks user to specify which one
```

---

## 11. Migration Plan

### 11.1 Database Migrations

```sql
-- Create conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_session_id ON conversations(session_id);

-- Create messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    intent VARCHAR(200),
    entities JSONB,
    tool_calls JSONB,
    tool_results JSONB,
    requires_confirmation BOOLEAN DEFAULT false,
    confirmation_status VARCHAR(20),
    pending_action JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
```

### 11.2 Backward Compatibility

- Existing `AgentTask`, `ToolExecution`, `ConversationTurn` models remain unchanged
- New `Conversation` and `Message` models are additive
- Chat API endpoints are new (`/api/v1/chat/*`)
- No breaking changes to existing task CRUD APIs

---

## 12. Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| OpenAI API latency | High | Medium | Implement streaming responses, show typing indicator |
| Cost overruns | Medium | Medium | Implement rate limits, monitor token usage |
| Ambiguous intent | Medium | High | Robust clarification flows, confidence thresholds |
| Data isolation breach | Critical | Low | Strict user_id filtering, audit logging |
| Session state loss | Medium | Low | Database persistence, session recovery logic |

---

## 13. Future Enhancements

- [ ] Voice input/output support
- [ ] Multi-language support
- [ ] Calendar integration (Google Calendar, Outlook)
- [ ] Recurring task creation via natural language
- [ ] Task dependencies ("after I finish X, remind me to do Y")
- [ ] Smart suggestions based on conversation patterns
- [ ] Export conversation history
- [ ] Customizable agent personality

---

## 14. References

- [OpenAI Agents SDK Documentation](https://platform.openai.com/docs/agents)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- Project Constitution: `.specify/memory/constitution.md`
- Existing Agent Models: `backend/src/models/agent.py`
- Existing MCP Tools: `backend/src/agent/mcp_tools.py`

---

**Document Status**: Ready for Review  
**Next Steps**: 
1. Technical review with backend team
2. Create implementation tasks (`/sp.tasks`)
3. Define API contract with frontend team
