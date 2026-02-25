"""Add Phase 3 chatbot tables: conversations, messages, pending_actions

Revision ID: phase3_chatbot
Revises: initial
Create Date: 2026-02-17

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'phase3_chatbot'
down_revision = None  # Set to initial migration if exists
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('session_id', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_message_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for conversations
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('ix_conversations_session_id', 'conversations', ['session_id'], unique=True)
    op.create_index('ix_conversations_user_created', 'conversations', ['user_id', 'created_at'])
    
    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('conversation_id', sa.UUID(), nullable=False),
        sa.Column('role', sa.Enum('user', 'assistant', 'system', name='messagerole'), nullable=False),
        sa.Column('content', sa.String(length=10000), nullable=False),
        sa.Column('intent', sa.String(length=200), nullable=True),
        sa.Column('entities', sa.JSON(), nullable=True),
        sa.Column('tool_calls', sa.JSON(), nullable=True),
        sa.Column('tool_results', sa.JSON(), nullable=True),
        sa.Column('requires_confirmation', sa.Boolean(), nullable=False, default=False),
        sa.Column('confirmation_status', sa.Enum('approve', 'reject', 'modify', 'skip', name='confirmationtype'), nullable=True),
        sa.Column('pending_action', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for messages
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('ix_messages_created_at', 'messages', ['created_at'])
    op.create_index('ix_messages_user_conversation', 'messages', ['conversation_id', 'created_at'])
    
    # Create pending_actions table
    op.create_table(
        'pending_actions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('conversation_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('tool_name', sa.String(length=100), nullable=False),
        sa.Column('action_params', sa.JSON(), nullable=False),
        sa.Column('confirmation_prompt', sa.String(length=1000), nullable=False),
        sa.Column('is_resolved', sa.Boolean(), nullable=False, default=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_value', sa.Enum('approve', 'reject', 'modify', 'skip', name='confirmationtype'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for pending_actions
    op.create_index('ix_pending_actions_conversation_id', 'pending_actions', ['conversation_id'])
    op.create_index('ix_pending_actions_user_id', 'pending_actions', ['user_id'])
    op.create_index('ix_pending_actions_is_resolved', 'pending_actions', ['is_resolved'])


def downgrade() -> None:
    # Drop tables in reverse order (due to foreign key constraints)
    op.drop_table('pending_actions')
    op.drop_table('messages')
    op.drop_table('conversations')
    
    # Drop enums if supported
    try:
        op.execute('DROP TYPE IF EXISTS messagerole')
        op.execute('DROP TYPE IF EXISTS confirmationtype')
    except:
        pass  # Some databases don't support DROP TYPE
