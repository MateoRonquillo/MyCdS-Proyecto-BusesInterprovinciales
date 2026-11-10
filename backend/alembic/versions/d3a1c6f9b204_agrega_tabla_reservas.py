"""agrega tabla reservas

Revision ID: d3a1c6f9b204
Revises: 9c7f999a3974
Create Date: 2026-10-31 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d3a1c6f9b204"
down_revision: Union[str, Sequence[str], None] = "9c7f999a3974"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "reservas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("frecuencia_id", sa.Integer(), nullable=False),
        sa.Column("fecha_viaje", sa.Date(), nullable=False),
        sa.Column("asiento", sa.Integer(), nullable=False),
        sa.Column("precio", sa.Float(), nullable=False),
        sa.Column("estado", sa.String(length=30), nullable=False),
        sa.ForeignKeyConstraint(["frecuencia_id"], ["frecuencias.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_reservas_id"), "reservas", ["id"], unique=False)
    op.create_index(op.f("ix_reservas_usuario_id"), "reservas", ["usuario_id"], unique=False)
    op.create_index(op.f("ix_reservas_frecuencia_id"), "reservas", ["frecuencia_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_reservas_frecuencia_id"), table_name="reservas")
    op.drop_index(op.f("ix_reservas_usuario_id"), table_name="reservas")
    op.drop_index(op.f("ix_reservas_id"), table_name="reservas")
    op.drop_table("reservas")
