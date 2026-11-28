"""Guarda el correo de contacto y el envío individual del boleto."""
from alembic import op
import sqlalchemy as sa

revision = "b10000000017"
down_revision = "b10000000016"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("reservas", sa.Column("pasajero_correo", sa.String(100), nullable=True))
    op.add_column("boletos", sa.Column("correo_pasajero_enviado_en", sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column("boletos", "correo_pasajero_enviado_en")
    op.drop_column("reservas", "pasajero_correo")
