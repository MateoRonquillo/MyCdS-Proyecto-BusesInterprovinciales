"""restringe duplicidad de asientos por viaje

Revision ID: f8b1c9d2e3a4
Revises: e4b7a2c1d609
Create Date: 2026-10-31 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "f8b1c9d2e3a4"
down_revision: Union[str, Sequence[str], None] = "e4b7a2c1d609"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_reserva_frecuencia_fecha_asiento",
        "reservas",
        ["frecuencia_id", "fecha_viaje", "asiento"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_reserva_frecuencia_fecha_asiento",
        "reservas",
        type_="unique",
    )