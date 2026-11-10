"""fusionar ramas de migracion

Revision ID: 4b8a5e4e36dc
Revises: c87d10f2a941, f715fa63d9b1
Create Date: 2026-10-24 20:15:54.864868

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b8a5e4e36dc'
down_revision: Union[str, Sequence[str], None] = ('c87d10f2a941', 'f715fa63d9b1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
