"""Permitir reutilizar asientos cancelados.

Revision ID: a6c4e2b8d901
Revises: f8b1c9d2e3a4
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a6c4e2b8d901"
down_revision: Union[str, Sequence[str], None] = "f8b1c9d2e3a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "uq_reserva_frecuencia_fecha_asiento",
        "reservas",
        type_="unique",
    )

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


def downgrade() -> None:
    op.drop_constraint(
        "uq_reserva_asiento_activo",
        "reservas",
        type_="unique",
    )

    op.drop_column("reservas", "asiento_activo")

    op.create_unique_constraint(
        "uq_reserva_frecuencia_fecha_asiento",
        "reservas",
        ["frecuencia_id", "fecha_viaje", "asiento"],
    )
