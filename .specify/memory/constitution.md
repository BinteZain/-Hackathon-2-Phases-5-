<!--
SYNC IMPACT REPORT
==================
Version change: 0.0.0 → 3.0.0
Modified principles: None (initial Phase 3 constitution)
Added sections:
  - I. Stateless Architecture
  - II. Agent-First Design
  - III. Tool Chaining Protocol
  - IV. Confirmation & Clarification
  - V. Follow-up Context Preservation
  - VI. Multi-Step Reasoning
  - VII. Error Recovery & Resilience
  - VIII. Observability & Audit Trail
Removed sections: None
Templates requiring updates: ✅ N/A (Phase 3 specific)
Follow-up TODOs: None
-->

# Hackathon-Todo Phase 3 Constitution

## Core Principles

### I. Stateless Architecture
All agent operations MUST be stateless at the API layer. Session state MUST be persisted to the database. Each request MUST contain all necessary context for execution. No in-memory state between requests.

### II. Agent-First Design
Every agent task MUST be treated as an autonomous unit of work. Agent tasks MUST be self-describing with clear intent, plan, and execution context. Agent decisions MUST be logged and auditable.

### III. Tool Chaining Protocol
MCP tools MUST be chainable with explicit dependencies between steps. Each tool execution MUST declare its inputs, outputs, and side effects. Tool chains MUST support rollback on failure.

### IV. Confirmation & Clarification
Agent MUST request confirmation before destructive operations (delete, bulk update). Agent MUST request clarification when intent is ambiguous with multiple valid interpretations. Confirmation prompts MUST be human-readable and specific.

### V. Follow-up Context Preservation
Agent MUST maintain conversation context across follow-up interactions. Follow-up responses (yes/ok/do it) MUST resolve to the most recent pending task. Context MUST include user intent, entities, and execution state.

### VI. Multi-Step Reasoning
Agent MUST decompose complex tasks into executable steps. Each step MUST have clear success criteria and failure handling. Reasoning chains MUST be logged for debugging and audit.

### VII. Error Recovery & Resilience
Agent MUST handle tool failures gracefully with retry logic where appropriate. Failed operations MUST provide actionable error messages. Agent MUST offer recovery paths or alternative approaches.

### VIII. Observability & Audit Trail
All agent decisions MUST be logged with reasoning context. Tool executions MUST record inputs, outputs, and timing. Agent sessions MUST be traceable end-to-end.

## Additional Constraints

**Security Requirements**:
- All agent operations MUST enforce user ownership validation
- Tool executions MUST validate user permissions before execution
- Sensitive operations MUST require explicit user confirmation

**Performance Standards**:
- Agent task planning MUST complete within 2 seconds
- Tool execution MUST have configurable timeouts (default 30s)
- Follow-up context lookup MUST complete within 100ms

**Data Retention**:
- Agent task history MUST be retained for 90 days
- Conversation turns MUST be retained for 30 days
- Tool execution logs MUST be retained for 14 days

## Development Workflow

**Code Review Requirements**:
- All agent logic changes MUST include test coverage
- Tool definitions MUST include parameter validation
- Confirmation flows MUST be tested end-to-end

**Quality Gates**:
- Agent reasoning MUST be deterministic for same inputs
- Tool chains MUST have rollback tests
- Follow-up resolution MUST have edge case coverage

## Governance

This constitution supersedes all other development practices for Phase 3. Amendments require documentation in ADR format and migration plan for existing agent tasks.

**Version**: 3.0.0 | **Ratified**: 2026-02-16 | **Last Amended**: 2026-02-16
