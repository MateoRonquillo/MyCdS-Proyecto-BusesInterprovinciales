"""Amplía el almacenamiento de fotografías de buses."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import MEDIUMTEXT

revision = "b10000000010"
down_revision = "b10000000009"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("buses") as batch:
        batch.alter_column("fotografia_url", existing_type=sa.String(500),
            type_=sa.Text().with_variant(MEDIUMTEXT(), "mysql"), existing_nullable=True)


def downgrade():
    if op.get_bind().scalar(sa.text("SELECT 1 FROM buses WHERE LENGTH(fotografia_url) > 500 LIMIT 1")):
        raise RuntimeError("Retira las fotos adjuntas antes de revertir la migración.")
    with op.batch_alter_table("buses") as batch:
        batch.alter_column("fotografia_url", existing_type=sa.Text().with_variant(MEDIUMTEXT(), "mysql"),
            type_=sa.String(500), existing_nullable=True)
