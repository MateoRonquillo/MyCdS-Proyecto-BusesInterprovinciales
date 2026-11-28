"""Añade imágenes opcionales para las ciudades del catálogo."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import MEDIUMTEXT

revision = "b10000000012"
down_revision = "b10000000011"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("imagenes_ciudad",
        sa.Column("ciudad_id", sa.String(150), primary_key=True),
        sa.Column("imagen", sa.Text().with_variant(MEDIUMTEXT(), "mysql"), nullable=False))


def downgrade():
    op.drop_table("imagenes_ciudad")
