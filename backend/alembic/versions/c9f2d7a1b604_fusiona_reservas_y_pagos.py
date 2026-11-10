"""fusiona las migraciones de reservas y pagos

Revision ID: c9f2d7a1b604
Revises: a6c4e2b8d901, b8d4f2a6c901
Create Date: 2026-11-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "c9f2d7a1b604"
down_revision: Union[str, Sequence[str], None] = (
    "a6c4e2b8d901",
    "b8d4f2a6c901",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
