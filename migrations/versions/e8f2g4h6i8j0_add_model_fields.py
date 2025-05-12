"""Add missing fields to llm_models table

Revision ID: e8f2g4h6i8j0
Revises: d7e1f3c5b9a2
Create Date: 2024-05-13 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e8f2g4h6i8j0'
down_revision = 'd7e1f3c5b9a2'
branch_labels = None
depends_on = None

def upgrade():
    # Check if columns exist before adding them
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_columns = [column['name'] for column in inspector.get_columns('llm_models')]
    
    # Check for model_name column which might be used instead of name
    has_model_name = 'model_name' in existing_columns
    
    # 1. Add 'name' column if it doesn't exist (and is needed)
    if 'name' not in existing_columns:
        op.add_column('llm_models', sa.Column('name', sa.String(100), nullable=True))
        # If model_name exists, use it to populate name
        if has_model_name:
            op.execute("UPDATE llm_models SET name = model_name WHERE name IS NULL")
        # Make it not nullable after setting values
        op.alter_column('llm_models', 'name', nullable=False)
    
    # 2. Add model_id if it doesn't exist
    if 'model_id' not in existing_columns:
        op.add_column('llm_models', sa.Column('model_id', sa.String(200), nullable=True))
        
        # Set model_id based on available columns (name or model_name)
        if 'name' in existing_columns:
            op.execute("UPDATE llm_models SET model_id = name WHERE model_id IS NULL")
        elif has_model_name:
            op.execute("UPDATE llm_models SET model_id = model_name WHERE model_id IS NULL")
        else:
            # If neither exists, use a placeholder and let application fix it
            op.execute("UPDATE llm_models SET model_id = 'unknown' WHERE model_id IS NULL")
            
        # Make it not nullable after setting values
        op.alter_column('llm_models', 'model_id', nullable=False)
    
    # 3. Add display_name if it doesn't exist
    if 'display_name' not in existing_columns:
        op.add_column('llm_models', sa.Column('display_name', sa.String(200), nullable=True))
        
        # Set display_name based on available columns
        if 'name' in existing_columns:
            op.execute("UPDATE llm_models SET display_name = name WHERE display_name IS NULL")
        elif has_model_name:
            op.execute("UPDATE llm_models SET display_name = model_name WHERE display_name IS NULL")
    
    # 4. Add model_type if it doesn't exist
    if 'model_type' not in existing_columns:
        op.add_column('llm_models', sa.Column('model_type', sa.String(50), nullable=True))
        
        # Check if capability column exists
        if 'capability' in existing_columns:
            # Map capability values to model_type values
            op.execute("UPDATE llm_models SET model_type = capability WHERE model_type IS NULL")
        else:
            # Default to 'chat' if capability doesn't exist
            op.execute("UPDATE llm_models SET model_type = 'chat' WHERE model_type IS NULL")

    # 5. Add is_enabled if it doesn't exist
    if 'is_enabled' not in existing_columns:
        op.add_column('llm_models', sa.Column('is_enabled', sa.Boolean(), server_default='true', nullable=False))
        
        # If status column exists, use it to set is_enabled
        if 'status' in existing_columns:
            op.execute("UPDATE llm_models SET is_enabled = (status = 'enabled') WHERE status IS NOT NULL")

def downgrade():
    # Drop columns in reverse order
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_columns = [column['name'] for column in inspector.get_columns('llm_models')]
    
    if 'is_enabled' in existing_columns:
        op.drop_column('llm_models', 'is_enabled')
    
    if 'model_type' in existing_columns:
        op.drop_column('llm_models', 'model_type')
    
    if 'display_name' in existing_columns:
        op.drop_column('llm_models', 'display_name')
    
    if 'model_id' in existing_columns:
        op.drop_column('llm_models', 'model_id') 