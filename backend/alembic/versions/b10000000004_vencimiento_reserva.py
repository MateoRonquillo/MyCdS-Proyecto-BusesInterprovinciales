"""Plazo de pago para las compras en línea."""
from alembic import op
import sqlalchemy as sa

revision = "b10000000004"
down_revision = "b10000000003"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("reservas", sa.Column("vence_en", sa.DateTime(), nullable=True))
    op.add_column("pagos", sa.Column("monto_lote", sa.Float(), nullable=True))


def downgrade():
    op.drop_column("pagos", "monto_lote")
    op.drop_column("reservas", "vence_en")
