"""modify cameras table

Revision ID: 303cca746c34
Revises: 
Create Date: 2024-07-29 14:13:03.705311

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '303cca746c34'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('cameras', sa.Column('ipaddress', sa.Text))


def downgrade() -> None:
    pass
