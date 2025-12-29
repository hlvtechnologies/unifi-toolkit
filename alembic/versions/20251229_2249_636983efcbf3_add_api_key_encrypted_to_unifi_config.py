"""add api_key_encrypted to unifi_config

Revision ID: 636983efcbf3
Revises: 9ded46fa11ea
Create Date: 2025-12-29 22:49:18.764323+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '636983efcbf3'
down_revision: Union[str, None] = '9ded46fa11ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add api_key_encrypted column for UniFi OS API key authentication
    # Column is nullable since existing installations use username/password
    with op.batch_alter_table('unifi_config', schema=None) as batch_op:
        batch_op.add_column(sa.Column('api_key_encrypted', sa.LargeBinary(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('unifi_config', schema=None) as batch_op:
        batch_op.drop_column('api_key_encrypted')
