"""agrega historial de estados de pago

Revision ID: f2c8a6d1b903
Revises: c9f2d7a1b604
Create Date: 2026-11-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f2c8a6d1b903"
down_revision: Union[str, Sequence[str], None] = "c9f2d7a1b604"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pagos_estado_historial",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pago_id", sa.Integer(), nullable=False),
        sa.Column("estado_anterior", sa.String(length=20), nullable=True),
        sa.Column("estado_nuevo", sa.String(length=20), nullable=False),
        sa.Column("cambiado_por_id", sa.Integer(), nullable=False),
        sa.Column("motivo", sa.String(length=255), nullable=True),
        sa.Column(
            "cambiado_en",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["cambiado_por_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["pago_id"], ["pagos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_pagos_estado_historial_id"),
        "pagos_estado_historial",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_pagos_estado_historial_pago_id"),
        "pagos_estado_historial",
        ["pago_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_pagos_estado_historial_pago_id"),
        table_name="pagos_estado_historial",
    )
    op.drop_index(
        op.f("ix_pagos_estado_historial_id"),
        table_name="pagos_estado_historial",
    )
    op.drop_table("pagos_estado_historial")
