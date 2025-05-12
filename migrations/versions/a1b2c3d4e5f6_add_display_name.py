"""Add display_name to llm_providers table

Revision ID: a1b2c3d4e5f6
Revises: 
Create Date: 2024-05-12 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Skip adding display_name if it already exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('llm_providers')]
    if 'display_name' not in columns:
        op.add_column('llm_providers', sa.Column('display_name', sa.String(200), nullable=True))
        # Update existing records with display_name = name
        op.execute("UPDATE llm_providers SET display_name = name WHERE display_name IS NULL")
        # Make display_name not nullable after setting default values
        op.alter_column('llm_providers', 'display_name', nullable=False)

def downgrade():
    # Remove display_name column from llm_providers table
    op.drop_column('llm_providers', 'display_name') 