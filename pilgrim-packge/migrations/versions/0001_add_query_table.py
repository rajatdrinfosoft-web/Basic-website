"""add query table

Revision ID: 0001_add_query_table
Revises: 
Create Date: 2024-06-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_add_query_table'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'query',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('customer_name', sa.String(length=100), nullable=False),
        sa.Column('customer_email', sa.String(length=100), nullable=False),
        sa.Column('customer_phone', sa.String(length=20), nullable=True),
        sa.Column('query_type', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='Open'),
        sa.Column('assigned_staff_id', sa.Integer, sa.ForeignKey('user.id'), nullable=True),
        sa.Column('priority', sa.String(length=50), nullable=True, server_default='Normal'),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp()),
        sa.Column('sla_deadline', sa.DateTime, nullable=True)
    )


def downgrade():
    op.drop_table('query')
