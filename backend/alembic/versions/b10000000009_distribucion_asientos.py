"""Distribución de asientos por piso y servicios a bordo."""
from alembic import op
import sqlalchemy as sa

revision = "b10000000009"
down_revision = "b10000000008"
branch_labels = None
depends_on = None


def upgrade():
    for tabla in ("modelos_bus", "plantillas_bus", "buses"):
        op.add_column(tabla, sa.Column("distribucion", sa.JSON(), nullable=True))


def downgrade():
    for tabla in ("buses", "plantillas_bus", "modelos_bus"):
        op.drop_column(tabla, "distribucion")
