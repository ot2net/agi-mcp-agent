"""Add type column to llm_providers table

Revision ID: d7e1f3c5b9a2
Revises: c6e9f2d4b8a0
Create Date: 2024-05-13 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd7e1f3c5b9a2'
down_revision = 'c6e9f2d4b8a0'
branch_labels = None
depends_on = None

def upgrade():
    # Check if the type column exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [column['name'] for column in inspector.get_columns('llm_providers')]
    
    # Add the type column if it doesn't exist
    if 'type' not in columns:
        op.add_column('llm_providers', sa.Column('type', sa.String(50), nullable=True))
        
        # Update type based on name for existing providers
        op.execute("""
            UPDATE llm_providers
            SET type = name
            WHERE type IS NULL
        """)

def downgrade():
    # Drop the type column if it was added by this migration
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [column['name'] for column in inspector.get_columns('llm_providers')]
    
    if 'type' in columns:
        op.drop_column('llm_providers', 'type') 