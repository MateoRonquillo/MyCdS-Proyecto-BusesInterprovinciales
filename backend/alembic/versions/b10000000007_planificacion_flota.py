"""Plantillas propias y asignaciones de flota por salida."""
from alembic import op
import sqlalchemy as sa

revision = "b10000000007"
down_revision = "b10000000006"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("plantillas_bus",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cooperativa_id", sa.Integer(), sa.ForeignKey("cooperativas.id"), nullable=False),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("capacidad_asientos", sa.Integer(), nullable=False),
        sa.Column("chasis", sa.String(80), nullable=False),
        sa.Column("carroceria", sa.String(80), nullable=False),
        sa.Column("asientos_vip", sa.String(500), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.UniqueConstraint("cooperativa_id", "nombre", name="uq_plantilla_bus_nombre"))
    with op.batch_alter_table("buses") as batch:
        batch.add_column(sa.Column("plantilla_id", sa.Integer(), nullable=True))
        batch.create_foreign_key("fk_bus_plantilla", "plantillas_bus", ["plantilla_id"], ["id"])
    with op.batch_alter_table("frecuencias") as batch:
        batch.add_column(sa.Column("grupo_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("fecha_inicio", sa.Date(), nullable=True))
        batch.create_foreign_key("fk_frecuencia_grupo", "grupos_bus", ["grupo_id"], ["id"])
    with op.batch_alter_table("reservas") as batch:
        batch.add_column(sa.Column("bus_asignado_id", sa.Integer(), nullable=True))
        batch.create_foreign_key("fk_reserva_bus_asignado", "buses", ["bus_asignado_id"], ["id"])
    op.create_index("ix_jornada_bus_fecha", "jornadas", ["bus_id", "fecha"])
    with op.batch_alter_table("jornadas") as batch:
        batch.drop_constraint("uq_jornada_bus", type_="unique")


def downgrade():
    if op.get_bind().scalar(sa.text("SELECT 1 FROM jornadas GROUP BY bus_id, fecha HAVING COUNT(*) > 1 LIMIT 1")):
        raise RuntimeError("Existen varias salidas por bus y día, incompatibles con la versión anterior.")
    with op.batch_alter_table("jornadas") as batch:
        batch.create_unique_constraint("uq_jornada_bus", ["bus_id", "fecha"])
    op.drop_index("ix_jornada_bus_fecha", table_name="jornadas")
    for tabla, fk, campo in (
        ("reservas", "fk_reserva_bus_asignado", "bus_asignado_id"),
        ("frecuencias", "fk_frecuencia_grupo", "grupo_id"),
        ("buses", "fk_bus_plantilla", "plantilla_id"),
    ):
        with op.batch_alter_table(tabla) as batch:
            batch.drop_constraint(fk, type_="foreignkey")
            batch.drop_column(campo)
    op.drop_column("frecuencias", "fecha_inicio")
    op.drop_table("plantillas_bus")
