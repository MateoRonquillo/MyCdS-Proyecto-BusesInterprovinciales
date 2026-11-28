"""Vincula las cuentas de tripulación con cada bus."""
from alembic import op
import sqlalchemy as sa

revision = "b10000000013"
down_revision = "b10000000012"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("buses") as batch:
        for rol in ("chofer", "ayudante"):
            campo = f"{rol}_id"
            batch.add_column(sa.Column(campo, sa.Integer(), nullable=True))
            batch.create_foreign_key(f"fk_buses_{rol}", "usuarios", [campo], ["id"])


def downgrade():
    with op.batch_alter_table("buses") as batch:
        for rol in ("ayudante", "chofer"):
            batch.drop_constraint(f"fk_buses_{rol}", type_="foreignkey")
            batch.drop_column(f"{rol}_id")
