"""Datos de contacto de las cooperativas."""
from alembic import op
import sqlalchemy as sa

revision = "b10000000003"
down_revision = "b10000000002"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("cooperativas", sa.Column("telefono", sa.String(30), nullable=True))
    op.add_column("cooperativas", sa.Column("correo_contacto", sa.String(100), nullable=True))
    op.add_column("cooperativas", sa.Column("direccion", sa.String(255), nullable=True))


def downgrade():
    op.drop_column("cooperativas", "direccion")
    op.drop_column("cooperativas", "correo_contacto")
    op.drop_column("cooperativas", "telefono")
