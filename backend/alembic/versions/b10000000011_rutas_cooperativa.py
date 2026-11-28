"""Asigna las rutas a sus cooperativas operadoras."""
from alembic import op
import sqlalchemy as sa

revision = "b10000000011"
down_revision = "b10000000010"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("rutas") as batch:
        batch.add_column(sa.Column("cooperativa_id", sa.Integer(), nullable=True))
        batch.create_foreign_key("fk_rutas_cooperativa", "cooperativas", ["cooperativa_id"], ["id"])
        batch.create_index("ix_rutas_cooperativa_id", ["cooperativa_id"])
    enlace = sa.table("frecuencias", sa.column("ruta_id"), sa.column("bus_id"))
    buses = sa.table("buses", sa.column("id"), sa.column("cooperativa_id"))
    rutas = sa.table("rutas", sa.column("id"), sa.column("cooperativa_id"))
    propietario = (sa.select(sa.func.min(buses.c.cooperativa_id))
        .select_from(enlace.join(buses, buses.c.id == enlace.c.bus_id))
        .where(enlace.c.ruta_id == rutas.c.id)
        .having(sa.func.count(sa.distinct(buses.c.cooperativa_id)) == 1)
        .scalar_subquery())
    op.execute(rutas.update().values(cooperativa_id=propietario))


def downgrade():
    with op.batch_alter_table("rutas") as batch:
        batch.drop_constraint("fk_rutas_cooperativa", type_="foreignkey")
        batch.drop_index("ix_rutas_cooperativa_id")
        batch.drop_column("cooperativa_id")
