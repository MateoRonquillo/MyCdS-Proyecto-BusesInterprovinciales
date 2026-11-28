"""Guarda la imagen ilustrativa de cada promoción."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import MEDIUMTEXT

revision = "b10000000014"
down_revision = "b10000000013"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("promociones_ruta", sa.Column(
        "imagen", sa.Text().with_variant(MEDIUMTEXT(), "mysql"), nullable=True))


def downgrade():
    op.drop_column("promociones_ruta", "imagen")
