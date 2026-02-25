# Database Schema Specification

## Overview
This document defines the database schema for the Hackathon-Todo application.

## Tables

### Users Table
```
users
- id (UUID, Primary Key, Default: gen_random_uuid())
- email (VARCHAR(255), UNIQUE, NOT NULL)
- username (VARCHAR(50), UNIQUE, NOT NULL)
- password_hash (VARCHAR(255), NOT NULL)
- first_name (VARCHAR(100))
- last_name (VARCHAR(100))
- avatar_url (TEXT)
- email_verified (BOOLEAN, DEFAULT: false)
- email_verification_token (VARCHAR(255))  -- For email verification
- password_reset_token (VARCHAR(255))      -- For password resets
- password_reset_expires (TIMESTAMP)       -- Expiration for reset tokens
- created_at (TIMESTAMP, DEFAULT: NOW())
- updated_at (TIMESTAMP, DEFAULT: NOW())
- last_login_at (TIMESTAMP)
- is_active (BOOLEAN, DEFAULT: true)
```

### Tasks Table
```
tasks
- id (UUID, Primary Key, Default: gen_random_uuid())
- user_id (UUID, Foreign Key -> users.id, NOT NULL)
- title (VARCHAR(255), NOT NULL)
- description (TEXT)
- status (VARCHAR(20), CHECK: 'pending', 'in-progress', 'completed', DEFAULT: 'pending')
- priority (VARCHAR(10), CHECK: 'low', 'medium', 'high', DEFAULT: 'medium')
- due_date (TIMESTAMP)
- completed_at (TIMESTAMP)
- created_at (TIMESTAMP, DEFAULT: NOW())
- updated_at (TIMESTAMP, DEFAULT: NOW())
```

### Projects Table (Optional)
```
projects
- id (UUID, Primary Key, Default: gen_random_uuid())
- user_id (UUID, Foreign Key -> users.id, NOT NULL)
- name (VARCHAR(255), NOT NULL)
- description (TEXT)
- color (VARCHAR(7))  -- Hex color code for UI
- created_at (TIMESTAMP, DEFAULT: NOW())
- updated_at (TIMESTAMP, DEFAULT: NOW())
```

### Sessions Table (For JWT management)
```
sessions
- id (UUID, Primary Key, Default: gen_random_uuid())
- user_id (UUID, Foreign Key -> users.id, NOT NULL)
- token (TEXT, NOT NULL)  -- Refresh token
- expires_at (TIMESTAMP, NOT NULL)
- created_at (TIMESTAMP, DEFAULT: NOW())
- is_revoked (BOOLEAN, DEFAULT: false)
```

### Conversations Table (Phase 3 - Chatbot)
```
conversations
- id (INTEGER, Primary Key, Auto Increment)
- user_id (UUID, Foreign Key -> users.id, NOT NULL)
- created_at (TIMESTAMP, DEFAULT: NOW())
- updated_at (TIMESTAMP, DEFAULT: NOW())
```

### Messages Table (Phase 3 - Chatbot)
```
messages
- id (INTEGER, Primary Key, Auto Increment)
- user_id (UUID, Foreign Key -> users.id, NOT NULL)
- conversation_id (INTEGER, Foreign Key -> conversations.id, NOT NULL)
- role (VARCHAR(20), NOT NULL, CHECK: 'user', 'assistant')
- content (TEXT, NOT NULL)
- created_at (TIMESTAMP, DEFAULT: NOW())
```

## Indexes
- Index on users.email for quick lookups
- Index on users.username for quick lookups
- Index on tasks.user_id for filtering tasks by user
- Index on tasks.status for filtering by status
- Index on tasks.due_date for sorting by due date
- Index on sessions.token for quick session validation
- Composite index on sessions.user_id and is_revoked for active session queries
- Index on conversations.user_id for filtering conversations by user (Phase 3)
- Index on conversations.created_at for sorting conversations (Phase 3)
- Index on messages.user_id for filtering messages by user (Phase 3)
- Index on messages.conversation_id for filtering messages by conversation (Phase 3)
- Index on messages.created_at for sorting messages (Phase 3)
- Composite index on messages(user_id, conversation_id) for user isolation queries (Phase 3)

## Relationships
- Users to Tasks: One-to-Many (One user can have many tasks)
- Users to Projects: One-to-Many (One user can have many projects)
- Users to Sessions: One-to-Many (One user can have many sessions)
- Projects to Tasks: One-to-Many (One project can have many tasks) - optional relation
- Users to Conversations: One-to-Many (One user can have many conversations) - Phase 3
- Conversations to Messages: One-to-Many (One conversation can have many messages) - Phase 3

## Constraints
- Users must have a unique email and username
- Tasks must belong to a valid user
- Tasks must have a title
- Tasks status must be one of the allowed values
- Tasks priority must be one of the allowed values
- Sessions must belong to a valid user
- Sessions must have an expiration date
- Conversations must belong to a valid user (Phase 3)
- Messages must belong to a valid user (Phase 3)
- Messages must belong to a valid conversation (Phase 3)
- Messages role must be 'user' or 'assistant' (Phase 3)
- Messages content must not be empty (Phase 3)
- Deleting a user cascades to all conversations and messages (Phase 3)
- Deleting a conversation cascades to all its messages (Phase 3)