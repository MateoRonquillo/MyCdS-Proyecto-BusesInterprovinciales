"""agrega boletos con código QR"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a7c3e9d2f104"
down_revision: Union[str, Sequence[str], None] = "f2c8a6d1b903"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "boletos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("reserva_id", sa.Integer(), nullable=False),
        sa.Column("codigo", sa.String(length=64), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["reserva_id"], ["reservas.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("codigo"),
        sa.UniqueConstraint("reserva_id"),
    )
    op.create_index(op.f("ix_boletos_id"), "boletos", ["id"], unique=False)
    op.create_index(op.f("ix_boletos_reserva_id"), "boletos", ["reserva_id"], unique=True)
    op.create_index(op.f("ix_boletos_codigo"), "boletos", ["codigo"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_boletos_codigo"), table_name="boletos")
    op.drop_index(op.f("ix_boletos_reserva_id"), table_name="boletos")
    op.drop_index(op.f("ix_boletos_id"), table_name="boletos")
    op.drop_table("boletos")
