# MCP Tools API Specification

**Version**: 1.0.0  
**Status**: Draft  
**Created**: 2026-02-17  
**Last Updated**: 2026-02-17  

---

## 1. Overview

This document defines the Model Context Protocol (MCP) tools for task management in the Todo AI Chatbot system. Each tool is a self-contained, callable function that performs a specific task operation while enforcing user isolation and security constraints.

### 1.1 Design Principles

- **User Isolation**: All tools enforce strict user ownership validation
- **Stateless Execution**: No in-memory state between tool invocations
- **Explicit Contracts**: Clear input/output schemas with validation
- **Error Transparency**: Descriptive error codes and messages
- **Confirmation Support**: Destructive operations support confirmation flows

### 1.2 Tool Registry

| Tool Name | Category | Requires Confirmation | Idempotent |
|-----------|----------|----------------------|------------|
| `add_task` | task | No | No |
| `list_tasks` | task | No | Yes |
| `update_task` | task | No | Yes |
| `complete_task` | task | No | Yes |
| `delete_task` | task | **Yes** | Yes |

---

## 2. Common Types and Schemas

### 2.1 Base Types

```typescript
// UUID string format (RFC 4122)
type UUID = string;  // e.g., "550e8400-e29b-41d4-a716-446655440000"

// ISO 8601 datetime string
type ISODateTime = string;  // e.g., "2026-02-17T10:30:00Z"

// Task status enumeration
type TaskStatus = "pending" | "in_progress" | "completed";

// Task priority enumeration
type TaskPriority = "low" | "medium" | "high" | "urgent";

// User context (extracted from JWT)
interface UserContext {
  user_id: UUID;
  email: string;
  iat: number;
  exp: number;
}
```

### 2.2 Task Object Schema

```typescript
interface Task {
  id: UUID;
  user_id: UUID;
  title: string;                    // 1-255 characters
  description: string | null;       // 0-500 characters
  status: TaskStatus;
  priority: TaskPriority;
  due_date: ISODateTime | null;
  created_at: ISODateTime;
  updated_at: ISODateTime;
  completed_at: ISODateTime | null;
}
```

### 2.3 Standard Response Envelope

All tool responses follow this envelope:

```typescript
interface ToolResponse<T = any> {
  success: boolean;
  data?: T;
  error?: ToolError;
  requires_confirmation?: boolean;
  confirmation_prompt?: string;
  pending_action_id?: UUID;
}

interface ToolError {
  code: ErrorCode;
  message: string;
  details?: Record<string, any>;
}
```

### 2.4 Error Code Taxonomy

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `SUCCESS` | 200 | Operation completed successfully |
| `VALIDATION_ERROR` | 400 | Invalid input parameters |
| `UNAUTHORIZED` | 401 | Missing or invalid authentication |
| `FORBIDDEN` | 403 | User lacks permission for this resource |
| `NOT_FOUND` | 404 | Requested resource does not exist |
| `CONFLICT` | 409 | Resource conflict (e.g., already completed) |
| `DATABASE_ERROR` | 500 | Database operation failed |
| `CONFIRMATION_REQUIRED` | 403 | Operation requires user confirmation |

---

## 3. Tool Definitions

### 3.1 `add_task`

Creates a new task in the user's todo list.

#### 3.1.1 Parameters

| Name | Type | Required | Default | Constraints | Description |
|------|------|----------|---------|-------------|-------------|
| `title` | string | **Yes** | - | 1-255 chars | Task title |
| `description` | string | No | `null` | 0-500 chars | Optional task description |
| `priority` | `TaskPriority` | No | `"medium"` | Enum | Task priority level |
| `due_date` | `ISODateTime` | No | `null` | Valid ISO 8601 | Due date with timezone |
| `status` | `TaskStatus` | No | `"pending"` | Enum | Initial task status |

#### 3.1.2 Return Schema

```typescript
interface AddTaskResponse {
  success: boolean;
  data?: {
    task: Task;
  };
  error?: ToolError;
}
```

#### 3.1.3 Example Input/Output

**Example 1: Basic Task Creation**

```json
// Input
{
  "title": "Buy groceries"
}

// Output
{
  "success": true,
  "data": {
    "task": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "660e8400-e29b-41d4-a716-446655440001",
      "title": "Buy groceries",
      "description": null,
      "status": "pending",
      "priority": "medium",
      "due_date": null,
      "created_at": "2026-02-17T10:30:00Z",
      "updated_at": "2026-02-17T10:30:00Z",
      "completed_at": null
    }
  }
}
```

**Example 2: Task with All Fields**

```json
// Input
{
  "title": "Prepare quarterly presentation",
  "description": "Create slides for Q1 review meeting",
  "priority": "high",
  "due_date": "2026-02-20T14:00:00Z",
  "status": "in_progress"
}

// Output
{
  "success": true,
  "data": {
    "task": {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "user_id": "660e8400-e29b-41d4-a716-446655440001",
      "title": "Prepare quarterly presentation",
      "description": "Create slides for Q1 review meeting",
      "status": "in_progress",
      "priority": "high",
      "due_date": "2026-02-20T14:00:00Z",
      "created_at": "2026-02-17T10:30:00Z",
      "updated_at": "2026-02-17T10:30:00Z",
      "completed_at": null
    }
  }
}
```

#### 3.1.4 Error Cases

| Error Code | Condition | Example Message |
|------------|-----------|-----------------|
| `VALIDATION_ERROR` | Missing title | "Parameter 'title' is required" |
| `VALIDATION_ERROR` | Title too long | "Parameter 'title' exceeds maximum length of 255 characters" |
| `VALIDATION_ERROR` | Invalid priority | "Parameter 'priority' must be one of: ['low', 'medium', 'high', 'urgent']" |
| `VALIDATION_ERROR` | Invalid date format | "Parameter 'due_date' must be a valid ISO 8601 datetime string" |
| `VALIDATION_ERROR` | Description too long | "Parameter 'description' exceeds maximum length of 500 characters" |
| `UNAUTHORIZED` | Missing/invalid JWT | "Authentication required. Please provide a valid token." |
| `DATABASE_ERROR` | DB connection failure | "Failed to create task. Database connection error." |

#### 3.1.5 Implementation Notes

```python
async def add_task(
    title: str,
    description: Optional[str] = None,
    priority: str = "medium",
    due_date: Optional[str] = None,
    status: str = "pending",
    context: UserContext = None
) -> AddTaskResponse:
    """
    Create a new task for the authenticated user.
    
    User Isolation: Task is created with user_id from JWT context.
    """
    # Validate parameters
    if not title or len(title) > 255:
        return ToolResponse(
            success=False,
            error=ToolError(
                code="VALIDATION_ERROR",
                message="Parameter 'title' is required and must be 1-255 characters"
            )
        )
    
    # Create task with user isolation
    task = Task(
        user_id=context.user_id,  # Enforce ownership
        title=title,
        description=description,
        priority=priority,
        due_date=due_date,
        status=status
    )
    
    # Persist to database
    session.add(task)
    session.commit()
    session.refresh(task)
    
    return ToolResponse(
        success=True,
        data={"task": task.model_dump()}
    )
```

---

### 3.2 `list_tasks`

Retrieves all tasks for the authenticated user with optional filtering and pagination.

#### 3.2.1 Parameters

| Name | Type | Required | Default | Constraints | Description |
|------|------|----------|---------|-------------|-------------|
| `status` | `TaskStatus` | No | `null` | Enum | Filter by status |
| `priority` | `TaskPriority` | No | `null` | Enum | Filter by priority |
| `limit` | integer | No | `50` | 1-100 | Maximum results to return |
| `offset` | integer | No | `0` | >= 0 | Pagination offset |
| `search` | string | No | `null` | 1-100 chars | Search in title/description |

#### 3.2.2 Return Schema

```typescript
interface ListTasksResponse {
  success: boolean;
  data?: {
    tasks: Task[];
    total: number;
    has_more: boolean;
    filters: {
      status?: TaskStatus;
      priority?: TaskPriority;
      search?: string;
    };
  };
  error?: ToolError;
}
```

#### 3.2.3 Example Input/Output

**Example 1: List All Tasks**

```json
// Input
{}

// Output
{
  "success": true,
  "data": {
    "tasks": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "user_id": "660e8400-e29b-41d4-a716-446655440001",
        "title": "Buy groceries",
        "description": null,
        "status": "pending",
        "priority": "medium",
        "due_date": null,
        "created_at": "2026-02-17T10:30:00Z",
        "updated_at": "2026-02-17T10:30:00Z",
        "completed_at": null
      },
      {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "user_id": "660e8400-e29b-41d4-a716-446655440001",
        "title": "Prepare quarterly presentation",
        "description": "Create slides for Q1 review meeting",
        "status": "in_progress",
        "priority": "high",
        "due_date": "2026-02-20T14:00:00Z",
        "created_at": "2026-02-16T09:00:00Z",
        "updated_at": "2026-02-17T08:00:00Z",
        "completed_at": null
      }
    ],
    "total": 2,
    "has_more": false,
    "filters": {}
  }
}
```

**Example 2: Filter by Status**

```json
// Input
{
  "status": "pending",
  "limit": 10
}

// Output
{
  "success": true,
  "data": {
    "tasks": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "user_id": "660e8400-e29b-41d4-a716-446655440001",
        "title": "Buy groceries",
        "description": null,
        "status": "pending",
        "priority": "medium",
        "due_date": null,
        "created_at": "2026-02-17T10:30:00Z",
        "updated_at": "2026-02-17T10:30:00Z",
        "completed_at": null
      }
    ],
    "total": 1,
    "has_more": false,
    "filters": {
      "status": "pending"
    }
  }
}
```

**Example 3: Pagination**

```json
// Input
{
  "limit": 2,
  "offset": 0
}

// Output
{
  "success": true,
  "data": {
    "tasks": [...],
    "total": 50,
    "has_more": true,
    "filters": {}
  }
}
```

#### 3.2.4 Error Cases

| Error Code | Condition | Example Message |
|------------|-----------|-----------------|
| `VALIDATION_ERROR` | Invalid status value | "Parameter 'status' must be one of: ['pending', 'in_progress', 'completed']" |
| `VALIDATION_ERROR` | Limit out of range | "Parameter 'limit' must be between 1 and 100" |
| `VALIDATION_ERROR` | Negative offset | "Parameter 'offset' must be >= 0" |
| `UNAUTHORIZED` | Missing/invalid JWT | "Authentication required. Please provide a valid token." |
| `DATABASE_ERROR` | DB query failure | "Failed to retrieve tasks. Database query error." |

#### 3.2.5 Implementation Notes

```python
async def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    search: Optional[str] = None,
    context: UserContext = None
) -> ListTasksResponse:
    """
    List tasks for the authenticated user with optional filtering.
    
    User Isolation: Query includes WHERE user_id = context.user_id
    """
    # Validate parameters
    if limit < 1 or limit > 100:
        return ToolResponse(
            success=False,
            error=ToolError(
                code="VALIDATION_ERROR",
                message="Parameter 'limit' must be between 1 and 100"
            )
        )
    
    if offset < 0:
        return ToolResponse(
            success=False,
            error=ToolError(
                code="VALIDATION_ERROR",
                message="Parameter 'offset' must be >= 0"
            )
        )
    
    # Build query with user isolation
    query = select(Task).where(Task.user_id == context.user_id)
    
    # Apply filters
    if status:
        query = query.where(Task.status == status)
    if priority:
        query = query.where(Task.priority == priority)
    if search:
        query = query.where(
            or_(
                Task.title.ilike(f"%{search}%"),
                Task.description.ilike(f"%{search}%")
            )
        )
    
    # Get total count
    total_query = select(func.count()).select_from(query.subquery())
    total = session.exec(total_query).one()
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    tasks = session.exec(query).all()
    
    return ToolResponse(
        success=True,
        data={
            "tasks": [task.model_dump() for task in tasks],
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
```

---

### 3.3 `update_task`

Updates an existing task's properties. Only provided fields are updated.

#### 3.3.1 Parameters

| Name | Type | Required | Default | Constraints | Description |
|------|------|----------|---------|-------------|-------------|
| `task_id` | `UUID` | **Yes** | - | Valid UUID | ID of task to update |
| `title` | string | No | - | 1-255 chars | New title |
| `description` | string | No | - | 0-500 chars | New description |
| `status` | `TaskStatus` | No | - | Enum | New status |
| `priority` | `TaskPriority` | No | - | Enum | New priority |
| `due_date` | `ISODateTime` | No | - | Valid ISO 8601 | New due date |

#### 3.3.2 Return Schema

```typescript
interface UpdateTaskResponse {
  success: boolean;
  data?: {
    task: Task;
  };
  error?: ToolError;
}
```

#### 3.3.3 Example Input/Output

**Example 1: Update Title**

```json
// Input
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries and household items"
}

// Output
{
  "success": true,
  "data": {
    "task": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "660e8400-e29b-41d4-a716-446655440001",
      "title": "Buy groceries and household items",
      "description": null,
      "status": "pending",
      "priority": "medium",
      "due_date": null,
      "created_at": "2026-02-17T10:30:00Z",
      "updated_at": "2026-02-17T11:00:00Z",
      "completed_at": null
    }
  }
}
```

**Example 2: Update Multiple Fields**

```json
// Input
{
  "task_id": "550e8400-e29b-41d4-a716-446655440002",
  "priority": "urgent",
  "due_date": "2026-02-18T09:00:00Z",
  "status": "in_progress"
}

// Output
{
  "success": true,
  "data": {
    "task": {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "user_id": "660e8400-e29b-41d4-a716-446655440001",
      "title": "Prepare quarterly presentation",
      "description": "Create slides for Q1 review meeting",
      "status": "in_progress",
      "priority": "urgent",
      "due_date": "2026-02-18T09:00:00Z",
      "created_at": "2026-02-16T09:00:00Z",
      "updated_at": "2026-02-17T11:00:00Z",
      "completed_at": null
    }
  }
}
```

#### 3.3.4 Error Cases

| Error Code | Condition | Example Message |
|------------|-----------|-----------------|
| `VALIDATION_ERROR` | Missing task_id | "Parameter 'task_id' is required" |
| `VALIDATION_ERROR` | Invalid UUID format | "Parameter 'task_id' must be a valid UUID" |
| `VALIDATION_ERROR` | Title too long | "Parameter 'title' exceeds maximum length of 255 characters" |
| `VALIDATION_ERROR` | Invalid status | "Parameter 'status' must be one of: ['pending', 'in_progress', 'completed']" |
| `NOT_FOUND` | Task doesn't exist | "Task not found with ID: 550e8400-e29b-41d4-a716-446655440000" |
| `FORBIDDEN` | User doesn't own task | "You do not have permission to modify this task" |
| `UNAUTHORIZED` | Missing/invalid JWT | "Authentication required. Please provide a valid token." |
| `DATABASE_ERROR` | DB update failure | "Failed to update task. Database error." |

#### 3.3.5 Implementation Notes

```python
async def update_task(
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    context: UserContext = None
) -> UpdateTaskResponse:
    """
    Update an existing task.
    
    User Isolation: Query includes WHERE user_id = context.user_id AND id = task_id
    """
    # Validate task_id
    try:
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        return ToolResponse(
            success=False,
            error=ToolError(
                code="VALIDATION_ERROR",
                message="Parameter 'task_id' must be a valid UUID"
            )
        )
    
    # Find task with user isolation
    query = select(Task).where(
        Task.id == task_uuid,
        Task.user_id == context.user_id  # Enforce ownership
    )
    task = session.exec(query).first()
    
    if not task:
        # Check if task exists but belongs to different user
        task_check = session.get(Task, task_uuid)
        if task_check:
            return ToolResponse(
                success=False,
                error=ToolError(
                    code="FORBIDDEN",
                    message="You do not have permission to modify this task"
                )
            )
        else:
            return ToolResponse(
                success=False,
                error=ToolError(
                    code="NOT_FOUND",
                    message=f"Task not found with ID: {task_id}"
                )
            )
    
    # Update fields (only provided values)
    update_data = {
        k: v for k, v in {
            "title": title,
            "description": description,
            "status": status,
            "priority": priority,
            "due_date": due_date
        }.items() if v is not None
    }
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    task.updated_at = datetime.utcnow()
    
    session.add(task)
    session.commit()
    session.refresh(task)
    
    return ToolResponse(
        success=True,
        data={"task": task.model_dump()}
    )
```

---

### 3.4 `complete_task`

Marks a task as completed by setting status to "completed" and recording completion timestamp.

#### 3.4.1 Parameters

| Name | Type | Required | Default | Constraints | Description |
|------|------|----------|---------|-------------|-------------|
| `task_id` | `UUID` | **Yes** | - | Valid UUID | ID of task to complete |

#### 3.4.2 Return Schema

```typescript
interface CompleteTaskResponse {
  success: boolean;
  data?: {
    task: Task;
  };
  error?: ToolError;
}
```

#### 3.4.3 Example Input/Output

**Example 1: Complete a Task**

```json
// Input
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}

// Output
{
  "success": true,
  "data": {
    "task": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "660e8400-e29b-41d4-a716-446655440001",
      "title": "Buy groceries",
      "description": null,
      "status": "completed",
      "priority": "medium",
      "due_date": null,
      "created_at": "2026-02-17T10:30:00Z",
      "updated_at": "2026-02-17T12:00:00Z",
      "completed_at": "2026-02-17T12:00:00Z"
    }
  },
  "message": "Task marked as completed"
}
```

**Example 2: Already Completed Task**

```json
// Input
{
  "task_id": "550e8400-e29b-41d4-a716-446655440001"
}

// Output
{
  "success": false,
  "error": {
    "code": "CONFLICT",
    "message": "Task is already completed",
    "details": {
      "task_id": "550e8400-e29b-41d4-a716-446655440001",
      "current_status": "completed",
      "completed_at": "2026-02-16T10:00:00Z"
    }
  }
}
```

#### 3.4.4 Error Cases

| Error Code | Condition | Example Message |
|------------|-----------|-----------------|
| `VALIDATION_ERROR` | Missing task_id | "Parameter 'task_id' is required" |
| `VALIDATION_ERROR` | Invalid UUID format | "Parameter 'task_id' must be a valid UUID" |
| `NOT_FOUND` | Task doesn't exist | "Task not found with ID: 550e8400-e29b-41d4-a716-446655440000" |
| `FORBIDDEN` | User doesn't own task | "You do not have permission to modify this task" |
| `CONFLICT` | Task already completed | "Task is already completed" |
| `UNAUTHORIZED` | Missing/invalid JWT | "Authentication required. Please provide a valid token." |
| `DATABASE_ERROR` | DB update failure | "Failed to complete task. Database error." |

#### 3.4.5 Implementation Notes

```python
async def complete_task(
    task_id: str,
    context: UserContext = None
) -> CompleteTaskResponse:
    """
    Mark a task as completed.
    
    User Isolation: Query includes WHERE user_id = context.user_id AND id = task_id
    """
    # Validate task_id
    try:
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        return ToolResponse(
            success=False,
            error=ToolError(
                code="VALIDATION_ERROR",
                message="Parameter 'task_id' must be a valid UUID"
            )
        )
    
    # Find task with user isolation
    query = select(Task).where(
        Task.id == task_uuid,
        Task.user_id == context.user_id  # Enforce ownership
    )
    task = session.exec(query).first()
    
    if not task:
        task_check = session.get(Task, task_uuid)
        if task_check:
            return ToolResponse(
                success=False,
                error=ToolError(
                    code="FORBIDDEN",
                    message="You do not have permission to modify this task"
                )
            )
        else:
            return ToolResponse(
                success=False,
                error=ToolError(
                    code="NOT_FOUND",
                    message=f"Task not found with ID: {task_id}"
                )
            )
    
    # Check if already completed
    if task.status == "completed":
        return ToolResponse(
            success=False,
            error=ToolError(
                code="CONFLICT",
                message="Task is already completed",
                details={
                    "task_id": str(task.id),
                    "current_status": task.status,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None
                }
            )
        )
    
    # Update status
    task.status = "completed"
    task.completed_at = datetime.utcnow()
    task.updated_at = task.completed_at
    
    session.add(task)
    session.commit()
    session.refresh(task)
    
    return ToolResponse(
        success=True,
        data={"task": task.model_dump()}
    )
```

---

### 3.5 `delete_task`

Permanently deletes a task from the user's todo list. Requires confirmation.

#### 3.5.1 Parameters

| Name | Type | Required | Default | Constraints | Description |
|------|------|----------|---------|-------------|-------------|
| `task_id` | `UUID` | **Yes** | - | Valid UUID | ID of task to delete |
| `confirmed` | boolean | No | `false` | - | Confirmation flag (skip confirmation if true) |

#### 3.5.2 Return Schema

```typescript
interface DeleteTaskResponse {
  success: boolean;
  data?: {
    deleted: boolean;
    task_id: UUID;
  };
  error?: ToolError;
  requires_confirmation?: boolean;
  confirmation_prompt?: string;
  pending_action_id?: UUID;
}
```

#### 3.5.3 Example Input/Output

**Example 1: Delete Request (Confirmation Required)**

```json
// Input
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}

// Output
{
  "success": true,
  "requires_confirmation": true,
  "confirmation_prompt": "Are you sure you want to delete the task 'Buy groceries'? This action cannot be undone.",
  "pending_action_id": "770e8400-e29b-41d4-a716-446655440003",
  "data": {
    "pending_action": {
      "tool": "delete_task",
      "params": {
        "task_id": "550e8400-e29b-41d4-a716-446655440000"
      }
    }
  }
}
```

**Example 2: Delete Confirmed**

```json
// Input
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "confirmed": true
}

// Output
{
  "success": true,
  "data": {
    "deleted": true,
    "task_id": "550e8400-e29b-41d4-a716-446655440000"
  },
  "message": "Task deleted successfully"
}
```

**Example 3: Skip Confirmation (Programmatic)**

```json
// Input
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "confirmed": true
}

// Output
{
  "success": true,
  "data": {
    "deleted": true,
    "task_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

#### 3.5.4 Error Cases

| Error Code | Condition | Example Message |
|------------|-----------|-----------------|
| `VALIDATION_ERROR` | Missing task_id | "Parameter 'task_id' is required" |
| `VALIDATION_ERROR` | Invalid UUID format | "Parameter 'task_id' must be a valid UUID" |
| `NOT_FOUND` | Task doesn't exist | "Task not found with ID: 550e8400-e29b-41d4-a716-446655440000" |
| `FORBIDDEN` | User doesn't own task | "You do not have permission to delete this task" |
| `UNAUTHORIZED` | Missing/invalid JWT | "Authentication required. Please provide a valid token." |
| `DATABASE_ERROR` | DB delete failure | "Failed to delete task. Database error." |

#### 3.5.5 Implementation Notes

```python
async def delete_task(
    task_id: str,
    confirmed: bool = False,
    context: UserContext = None
) -> DeleteTaskResponse:
    """
    Delete a task permanently.
    
    User Isolation: Query includes WHERE user_id = context.user_id AND id = task_id
    Confirmation: Required unless confirmed=true
    """
    # Validate task_id
    try:
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        return ToolResponse(
            success=False,
            error=ToolError(
                code="VALIDATION_ERROR",
                message="Parameter 'task_id' must be a valid UUID"
            )
        )
    
    # Find task with user isolation
    query = select(Task).where(
        Task.id == task_uuid,
        Task.user_id == context.user_id  # Enforce ownership
    )
    task = session.exec(query).first()
    
    if not task:
        task_check = session.get(Task, task_uuid)
        if task_check:
            return ToolResponse(
                success=False,
                error=ToolError(
                    code="FORBIDDEN",
                    message="You do not have permission to delete this task"
                )
            )
        else:
            return ToolResponse(
                success=False,
                error=ToolError(
                    code="NOT_FOUND",
                    message=f"Task not found with ID: {task_id}"
                )
            )
    
    # Check confirmation
    if not confirmed:
        # Generate pending action ID
        pending_action_id = uuid.uuid4()
        
        # Store pending action for later confirmation
        pending_action = {
            "id": str(pending_action_id),
            "tool": "delete_task",
            "params": {"task_id": str(task_uuid)},
            "user_id": str(context.user_id),
            "task_title": task.title,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # In production, persist to database
        # await cache.set(f"pending_action:{pending_action_id}", pending_action, ttl=86400)
        
        return ToolResponse(
            success=True,
            requires_confirmation=True,
            confirmation_prompt=f"Are you sure you want to delete the task '{task.title}'? This action cannot be undone.",
            pending_action_id=pending_action_id,
            data={"pending_action": pending_action}
        )
    
    # Confirmed - proceed with deletion
    session.delete(task)
    session.commit()
    
    return ToolResponse(
        success=True,
        data={
            "deleted": True,
            "task_id": str(task_uuid)
        }
    )
```

---

## 4. User Isolation Enforcement

### 4.1 Security Model

All MCP tools enforce strict user isolation through the following mechanisms:

1. **JWT Authentication**: Every tool invocation requires a valid JWT token
2. **User Context Extraction**: User ID is extracted from JWT, not from parameters
3. **Query Scoping**: All database queries include `WHERE user_id = :context_user_id`
4. **Ownership Validation**: Read/Update/Delete operations verify task ownership

### 4.2 Implementation Pattern

```python
# CORRECT: User isolation enforced
async def get_task(task_id: str, context: UserContext):
    query = select(Task).where(
        Task.id == task_uuid,
        Task.user_id == context.user_id  # ✓ Enforced
    )
    task = session.exec(query).first()

# INCORRECT: Missing user isolation
async def get_task(task_id: str, context: UserContext):
    query = select(Task).where(Task.id == task_uuid)  # ✗ Missing user_id filter
    task = session.exec(query).first()
```

### 4.3 Error Response for Cross-User Access

When a user attempts to access another user's task:

```json
{
  "success": false,
  "error": {
    "code": "FORBIDDEN",
    "message": "You do not have permission to modify this task",
    "details": {
      "reason": "task_ownership_violation",
      "task_id": "550e8400-e29b-41d4-a716-446655440000",
      "expected_user_id": "660e8400-e29b-41d4-a716-446655440001",
      "actual_user_id": "660e8400-e29b-41d4-a716-446655440002"
    }
  }
}
```

### 4.4 Audit Logging

All tool invocations are logged with user context:

```python
audit_log = {
    "timestamp": datetime.utcnow().isoformat(),
    "user_id": str(context.user_id),
    "tool_name": "update_task",
    "parameters": {
        "task_id": task_id,
        "updated_fields": list(update_data.keys())
    },
    "result": "success" | "error",
    "error_code": error.code if error else None
}
```

---

## 5. Confirmation Protocol

### 5.1 Confirmation Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   User      │────▶│  delete_task│────▶│  Pending    │────▶│  Confirm    │
│   Request   │     │   Tool      │     │  Action     │     │  Endpoint   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │  Execute    │
                                        │  Delete     │
                                        └─────────────┘
```

### 5.2 Confirmation Endpoint

```python
@router.post("/chat/confirm")
async def confirm_action(
    request: ConfirmActionRequest,
    context: UserContext = Depends(get_current_user)
):
    """
    Confirm or reject a pending action.
    """
    # Retrieve pending action
    pending_action = await get_pending_action(
        request.action_id,
        context.user_id
    )
    
    if request.confirmed:
        # Execute the pending action
        if pending_action.tool == "delete_task":
            return await delete_task(
                task_id=pending_action.params["task_id"],
                confirmed=True,
                context=context
            )
    else:
        # Reject the action
        await delete_pending_action(request.action_id)
        return {
            "success": True,
            "message": "Action cancelled",
            "action_status": "rejected"
        }
```

### 5.3 Confirmation Timeout

- Pending actions expire after **24 hours**
- Expired actions are automatically rejected
- User receives appropriate message on timeout

---

## 6. Testing Guidelines

### 6.1 Unit Test Examples

```python
class TestAddTask:
    async def test_create_task_success(self, mock_session, mock_user_context):
        result = await add_task(
            title="Test task",
            priority="high",
            context=mock_user_context
        )
        assert result.success is True
        assert result.data["task"]["title"] == "Test task"
        assert result.data["task"]["user_id"] == str(mock_user_context.user_id)
    
    async def test_create_task_missing_title(self, mock_user_context):
        result = await add_task(context=mock_user_context)
        assert result.success is False
        assert result.error.code == "VALIDATION_ERROR"
    
    async def test_create_task_enforces_user_isolation(self, mock_session, mock_user_context):
        await add_task(title="Test", context=mock_user_context)
        # Verify task was created with correct user_id
        call_args = mock_session.add.call_args[0][0]
        assert call_args.user_id == mock_user_context.user_id


class TestDeleteTask:
    async def test_delete_requires_confirmation(self, mock_session, mock_user_context, mock_task):
        result = await delete_task(
            task_id=str(mock_task.id),
            context=mock_user_context
        )
        assert result.requires_confirmation is True
        assert result.confirmation_prompt is not None
    
    async def test_delete_with_confirmation(self, mock_session, mock_user_context, mock_task):
        result = await delete_task(
            task_id=str(mock_task.id),
            confirmed=True,
            context=mock_user_context
        )
        assert result.success is True
        assert result.data["deleted"] is True
        mock_session.delete.assert_called_once()
    
    async def test_delete_foreign_task_returns_forbidden(self, mock_session, mock_user_context, other_user_task):
        result = await delete_task(
            task_id=str(other_user_task.id),
            confirmed=True,
            context=mock_user_context
        )
        assert result.success is False
        assert result.error.code == "FORBIDDEN"
```

### 6.2 Integration Test Checklist

- [ ] All tools require valid JWT authentication
- [ ] User isolation prevents cross-user access
- [ ] Validation errors return appropriate error codes
- [ ] Delete operations require confirmation
- [ ] Confirmation timeout expires after 24 hours
- [ ] Database transactions rollback on error
- [ ] Audit logs capture all tool invocations

---

## 7. References

- Chatbot Feature Spec: `specs/features/chatbot.md`
- Constitution: `.specify/memory/constitution.md`
- Existing MCP Tools: `backend/src/agent/mcp_tools.py`
- Task Routes: `backend/src/routes/tasks.py`
- Task Models: `backend/src/models/task.py`

---

**Document Status**: Ready for Implementation  
**Next Steps**:
1. Implement tool functions in `backend/src/agent/mcp_tools.py`
2. Add confirmation endpoint to chat API
3. Write unit tests for all tools
4. Integration testing with chatbot agent
