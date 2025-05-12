"""Remove api_key not null constraint from llm_providers

Revision ID: c6e9f2d4b8a0
Revises: b3c5d7e9f1a2
Create Date: 2024-05-13 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c6e9f2d4b8a0'
down_revision = 'b3c5d7e9f1a2'
branch_labels = None
depends_on = None

def upgrade():
    # 1. Remove NOT NULL constraint from api_key in llm_providers table
    op.alter_column('llm_providers', 'api_key', 
                    existing_type=sa.TEXT(), 
                    nullable=True)
    
    # 2. Make sure type column is nullable (just in case)
    op.alter_column('llm_providers', 'type', 
                    existing_type=sa.VARCHAR(32), 
                    nullable=True)

def downgrade():
    # Restore NOT NULL constraints
    op.alter_column('llm_providers', 'api_key', 
                    existing_type=sa.TEXT(), 
                    nullable=False)
    
    op.alter_column('llm_providers', 'type', 
                    existing_type=sa.VARCHAR(32), 
                    nullable=False) 