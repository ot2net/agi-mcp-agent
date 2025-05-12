"""Fix provider types in llm_providers table

Revision ID: k2l4m6n8p0r2
Revises: e8f2g4h6i8j0
Create Date: 2024-05-13 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'k2l4m6n8p0r2'
down_revision = 'e8f2g4h6i8j0'
branch_labels = None
depends_on = None

def upgrade():
    # Update deepseek provider type from 'test' to 'deepseek'
    op.execute("UPDATE llm_providers SET type = 'deepseek' WHERE name = 'deepseek' AND type = 'test'")
    
    # Make sure other providers have correct types
    op.execute("UPDATE llm_providers SET type = 'openai' WHERE name = 'openai' AND (type IS NULL OR type != 'openai')")
    op.execute("UPDATE llm_providers SET type = 'anthropic' WHERE name = 'anthropic' AND (type IS NULL OR type != 'anthropic')")
    op.execute("UPDATE llm_providers SET type = 'google' WHERE name = 'google' AND (type IS NULL OR type != 'google')")
    op.execute("UPDATE llm_providers SET type = 'mistral' WHERE name = 'mistral' AND (type IS NULL OR type != 'mistral')")
    op.execute("UPDATE llm_providers SET type = 'rest' WHERE name = 'qwen' AND (type IS NULL OR type != 'rest')")

def downgrade():
    # Restore original values if needed
    op.execute("UPDATE llm_providers SET type = 'test' WHERE name = 'deepseek' AND type = 'deepseek'") 