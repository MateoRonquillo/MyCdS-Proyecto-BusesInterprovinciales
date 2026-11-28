"""Almacena logos adjuntos en los catálogos de identidad."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import MEDIUMTEXT

revision = "b10000000008"
down_revision = "b10000000007"
branch_labels = None
depends_on = None


def upgrade():
    for tabla, longitud in (("cooperativas", 255), ("configuracion", 500)):
        with op.batch_alter_table(tabla) as batch:
            batch.alter_column("logo_url", existing_type=sa.String(longitud),
                type_=sa.Text().with_variant(MEDIUMTEXT(), "mysql"), existing_nullable=True)


def downgrade():
    for tabla, longitud in (("cooperativas", 255), ("configuracion", 500)):
        if op.get_bind().scalar(sa.text(f"SELECT 1 FROM {tabla} WHERE LENGTH(logo_url) > :limite LIMIT 1"), {"limite": longitud}):
            raise RuntimeError("Retira los logos adjuntos antes de revertir la migración.")
    for tabla, longitud in (("cooperativas", 255), ("configuracion", 500)):
        with op.batch_alter_table(tabla) as batch:
            batch.alter_column("logo_url", existing_type=sa.Text().with_variant(MEDIUMTEXT(), "mysql"),
                type_=sa.String(longitud), existing_nullable=True)
