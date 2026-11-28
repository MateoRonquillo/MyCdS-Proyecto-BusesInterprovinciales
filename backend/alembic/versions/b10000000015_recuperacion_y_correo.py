"""Guarda la vigencia del enlace de recuperación y el envío del boleto."""
from alembic import op
import sqlalchemy as sa

revision = "b10000000015"
down_revision = "b10000000014"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("usuarios", sa.Column("recuperacion_hash", sa.String(64), nullable=True))
    op.add_column("usuarios", sa.Column("recuperacion_vence", sa.DateTime(), nullable=True))
    op.create_unique_constraint("uq_usuario_recuperacion", "usuarios", ["recuperacion_hash"])
    op.add_column("boletos", sa.Column("correo_enviado_en", sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column("boletos", "correo_enviado_en")
    op.drop_constraint("uq_usuario_recuperacion", "usuarios", type_="unique")
    op.drop_column("usuarios", "recuperacion_vence")
    op.drop_column("usuarios", "recuperacion_hash")
