"""Add indexes to Package model

Revision ID: 940380ab1998
Revises: 
Create Date: 2025-10-22 15:56:01.961324

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '940380ab1998'
down_revision = '0001_add_query_table'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(sa.text('CREATE INDEX IF NOT EXISTS ix_package_destination ON package (destination)'))
    op.execute(sa.text('CREATE INDEX IF NOT EXISTS ix_package_duration ON package (duration)'))
    op.execute(sa.text('CREATE INDEX IF NOT EXISTS ix_package_price ON package (price)'))
    op.execute(sa.text('CREATE INDEX IF NOT EXISTS ix_package_title ON package (title)'))


def downgrade():
    op.execute(sa.text('DROP INDEX IF EXISTS ix_package_title'))
    op.execute(sa.text('DROP INDEX IF EXISTS ix_package_price'))
    op.execute(sa.text('DROP INDEX IF EXISTS ix_package_duration'))
    op.execute(sa.text('DROP INDEX IF EXISTS ix_package_destination'))
