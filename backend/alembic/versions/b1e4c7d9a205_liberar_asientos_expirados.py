"""liberar asientos de reservas expiradas

Revision ID: b1e4c7d9a205
Revises: a7c3e9d2f104
Create Date: 2026-11-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b1e4c7d9a205"
down_revision: Union[str, Sequence[str], None] = "a7c3e9d2f104"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "uq_reserva_asiento_activo",
        "reservas",
        type_="unique",
    )
    op.drop_column("reservas", "asiento_activo")
    op.add_column(
        "reservas",
        sa.Column(
            "asiento_activo",
            sa.Integer(),
            sa.Computed(
                "CASE WHEN estado IN ('CANCELADA', 'EXPIRADA') THEN NULL ELSE asiento END",
                persisted=True,
            ),
            nullable=True,
        ),
    )
    op.create_unique_constraint(
        "uq_reserva_asiento_activo",
        "reservas",
        ["frecuencia_id", "fecha_viaje", "asiento_activo"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_reserva_asiento_activo",
        "reservas",
        type_="unique",
    )
    op.drop_column("reservas", "asiento_activo")
    op.add_column(
        "reservas",
        sa.Column(
            "asiento_activo",
            sa.Integer(),
            sa.Computed(
                "CASE WHEN estado = 'CANCELADA' THEN NULL ELSE asiento END",
                persisted=True,
            ),
            nullable=True,
        ),
    )
    op.create_unique_constraint(
        "uq_reserva_asiento_activo",
        "reservas",
        ["frecuencia_id", "fecha_viaje", "asiento_activo"],
    )
