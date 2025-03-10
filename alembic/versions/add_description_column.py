# alembic/versions/add_description_column.py
"""Add description column to wines table

Revision ID: add_description_column
Revises: previous_revision_id  # replace with your latest revision ID
Create Date: 2023-03-08

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = 'add_description_column'
down_revision = None  # replace with your latest revision ID
branch_labels = None
depends_on = None


def upgrade():
    # Add the description column to the wines table
    op.add_column('wines', sa.Column('description', sa.Text(), nullable=True))


def downgrade():
    # Remove the description column
    op.drop_column('wines', 'description')