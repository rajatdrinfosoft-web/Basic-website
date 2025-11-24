"""Enhance query management and add response tracking

Revision ID: 2a1c3e2b3f1d
Revises: 940380ab1998
Create Date: 2025-11-24 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2a1c3e2b3f1d'
down_revision = '940380ab1998'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('query', sa.Column('response_due_at', sa.DateTime(), nullable=True))
    op.add_column('query', sa.Column('first_response_at', sa.DateTime(), nullable=True))
    op.add_column('query', sa.Column('resolved_at', sa.DateTime(), nullable=True))
    op.add_column('query', sa.Column('escalated_at', sa.DateTime(), nullable=True))
    op.add_column('query', sa.Column('escalation_reason', sa.String(length=255), nullable=True))
    op.add_column('query', sa.Column('last_contact_channel', sa.String(length=50), nullable=True))
    op.add_column('query', sa.Column('last_response_summary', sa.Text(), nullable=True))
    op.add_column('query', sa.Column('ticket_number', sa.String(length=20), nullable=True))
    op.add_column('query', sa.Column('tags', sa.String(length=255), nullable=True))
    op.add_column('query', sa.Column('source', sa.String(length=50), nullable=True))
    op.create_index('ix_query_ticket_number', 'query', ['ticket_number'], unique=True)

    op.create_table(
        'query_response_template',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('subject', sa.String(length=200), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('TRUE'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'query_response',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('query_id', sa.Integer(), nullable=False),
        sa.Column('staff_id', sa.Integer(), nullable=True),
        sa.Column('subject', sa.String(length=200), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('channel', sa.String(length=50), nullable=True),
        sa.Column('attachment_urls', sa.Text(), nullable=True),
        sa.Column('used_template_id', sa.Integer(), nullable=True),
        sa.Column('status_after', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['query_id'], ['query.id'], ),
        sa.ForeignKeyConstraint(['staff_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['used_template_id'], ['query_response_template.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('query_response')
    op.drop_table('query_response_template')
    op.drop_index('ix_query_ticket_number', table_name='query')
    op.drop_column('query', 'source')
    op.drop_column('query', 'tags')
    op.drop_column('query', 'ticket_number')
    op.drop_column('query', 'last_response_summary')
    op.drop_column('query', 'last_contact_channel')
    op.drop_column('query', 'escalation_reason')
    op.drop_column('query', 'escalated_at')
    op.drop_column('query', 'resolved_at')
    op.drop_column('query', 'first_response_at')
    op.drop_column('query', 'response_due_at')

