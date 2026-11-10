"""agrega pagos y revisión de pagos

Revision ID: b8d4f2a6c901
Revises: e4b7a2c1d609
Create Date: 2026-11-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b8d4f2a6c901"
down_revision: Union[str, Sequence[str], None] = "e4b7a2c1d609"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pagos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("reserva_id", sa.Integer(), nullable=False),
        sa.Column("registrado_por_id", sa.Integer(), nullable=False),
        sa.Column("revisado_por_id", sa.Integer(), nullable=True),
        sa.Column("metodo_pago", sa.String(length=20), nullable=False),
        sa.Column("monto", sa.Float(), nullable=False),
        sa.Column("referencia", sa.String(length=100), nullable=True),
        sa.Column("estado", sa.String(length=20), nullable=False),
        sa.Column("motivo_rechazo", sa.String(length=255), nullable=True),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("revisado_en", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["registrado_por_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["reserva_id"], ["reservas.id"]),
        sa.ForeignKeyConstraint(["revisado_por_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pagos_id"), "pagos", ["id"], unique=False)
    op.create_index(op.f("ix_pagos_reserva_id"), "pagos", ["reserva_id"], unique=False)
    op.create_index(op.f("ix_pagos_estado"), "pagos", ["estado"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_pagos_estado"), table_name="pagos")
    op.drop_index(op.f("ix_pagos_reserva_id"), table_name="pagos")
    op.drop_index(op.f("ix_pagos_id"), table_name="pagos")
    op.drop_table("pagos")
