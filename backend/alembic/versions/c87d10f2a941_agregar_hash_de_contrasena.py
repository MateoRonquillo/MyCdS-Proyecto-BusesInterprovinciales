"""Agregar hash de contrasena a usuarios."""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c87d10f2a941"
down_revision: Union[str, Sequence[str], None] = "44fa5271591b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column("password_hash", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("usuarios", "password_hash")