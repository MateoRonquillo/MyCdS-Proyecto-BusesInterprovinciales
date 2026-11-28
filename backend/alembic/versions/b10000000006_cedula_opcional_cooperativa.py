"""Permite cuentas institucionales de cooperativa sin cédula personal."""
from alembic import op
import sqlalchemy as sa

revision = "b10000000006"
down_revision = "b10000000005"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("usuarios") as batch:
        batch.alter_column("cedula", existing_type=sa.String(15), nullable=True)


def downgrade():
    if op.get_bind().scalar(sa.text("SELECT 1 FROM usuarios WHERE cedula IS NULL LIMIT 1")):
        raise RuntimeError("Existen cuentas institucionales sin cédula. Asigna cédulas válidas antes de revertir.")
    with op.batch_alter_table("usuarios") as batch:
        batch.alter_column("cedula", existing_type=sa.String(15), nullable=False)
