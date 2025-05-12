"""Add metadata to llm_models and make type nullable in llm_providers

Revision ID: b3c5d7e9f1a2
Revises: a1b2c3d4e5f6
Create Date: 2024-05-12 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b3c5d7e9f1a2'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None

def upgrade():
    # Add metadata column to llm_models table
    op.add_column('llm_models', sa.Column('metadata', sa.JSON(), nullable=True))
    # Make type column nullable in llm_providers table
    op.alter_column('llm_providers', 'type', existing_type=sa.String(), nullable=True)

def downgrade():
    # Remove metadata column from llm_models table
    op.drop_column('llm_models', 'metadata')
    # Make type column not nullable in llm_providers table
    op.alter_column('llm_providers', 'type', existing_type=sa.String(), nullable=False) 