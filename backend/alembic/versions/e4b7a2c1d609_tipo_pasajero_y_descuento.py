"""agrega categoria de pasajero a reservas

Revision ID: e4b7a2c1d609
Revises: d3a1c6f9b204
Create Date: 2026-10-31 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e4b7a2c1d609"
down_revision: Union[str, Sequence[str], None] = "d3a1c6f9b204"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "reservas",
        sa.Column(
            "tipo_pasajero",
            sa.String(length=30),
            server_default="GENERAL",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("reservas", "tipo_pasajero")
