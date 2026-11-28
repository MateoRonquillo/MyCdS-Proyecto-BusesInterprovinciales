"""Identifica las reservas y los pagos que pertenecen a un mismo lote."""
from alembic import op
import sqlalchemy as sa

revision = "b10000000016"
down_revision = "b10000000015"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("reservas", sa.Column("compra_id", sa.String(32), nullable=True))
    op.create_index("ix_reservas_compra_id", "reservas", ["compra_id"])
    op.add_column("pagos", sa.Column("lote_id", sa.String(32), nullable=True))
    op.create_index("ix_pagos_lote_id", "pagos", ["lote_id"])


def downgrade():
    op.drop_index("ix_pagos_lote_id", table_name="pagos")
    op.drop_column("pagos", "lote_id")
    op.drop_index("ix_reservas_compra_id", table_name="reservas")
    op.drop_column("reservas", "compra_id")
