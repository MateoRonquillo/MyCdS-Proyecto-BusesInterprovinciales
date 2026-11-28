"""Catálogos de flota, ciudades complementarias y promociones."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import MEDIUMTEXT

revision = "b10000000005"
down_revision = "b10000000004"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("cooperativas") as batch:
        batch.add_column(sa.Column("ruc", sa.String(13), nullable=True))
        batch.add_column(sa.Column("razon_social", sa.String(150), nullable=True))
        batch.add_column(sa.Column("representante_legal", sa.String(150), nullable=True))
        batch.add_column(sa.Column("permiso_operacion", sa.String(150), nullable=True))
        batch.add_column(sa.Column("sitio_web", sa.String(255), nullable=True))
        batch.create_unique_constraint("uq_cooperativas_ruc", ["ruc"])
    op.create_table("ciudades_catalogo",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("clave", sa.String(100), nullable=False, unique=True),
        sa.Column("provincia_id", sa.String(2), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False))
    op.create_table("modelos_bus",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(100), nullable=False, unique=True),
        sa.Column("capacidad_asientos", sa.Integer(), nullable=False),
        sa.Column("chasis", sa.String(80), nullable=False),
        sa.Column("carroceria", sa.String(80), nullable=False),
        sa.Column("asientos_vip", sa.String(500), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False))
    op.create_table("grupos_bus",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cooperativa_id", sa.Integer(), sa.ForeignKey("cooperativas.id"), nullable=False),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.UniqueConstraint("cooperativa_id", "nombre", name="uq_grupo_bus_nombre"))
    with op.batch_alter_table("buses") as batch:
        batch.add_column(sa.Column("modelo_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("grupo_id", sa.Integer(), nullable=True))
        batch.create_foreign_key("fk_bus_modelo", "modelos_bus", ["modelo_id"], ["id"])
        batch.create_foreign_key("fk_bus_grupo", "grupos_bus", ["grupo_id"], ["id"])
    op.add_column("configuracion", sa.Column("precio_promocion_diaria", sa.Float(), server_default="0", nullable=False))
    op.add_column("configuracion", sa.Column("instrucciones_promocion", sa.String(500), server_default="", nullable=False))
    op.add_column("configuracion", sa.Column("aviso_operativo", sa.String(280), server_default="", nullable=False))
    op.create_table("promociones_ruta",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cooperativa_id", sa.Integer(), sa.ForeignKey("cooperativas.id"), nullable=False),
        sa.Column("ruta_id", sa.Integer(), sa.ForeignKey("rutas.id"), nullable=False),
        sa.Column("desde", sa.Date(), nullable=False),
        sa.Column("hasta", sa.Date(), nullable=False),
        sa.Column("monto", sa.Float(), nullable=False),
        sa.Column("referencia", sa.String(100), nullable=False),
        sa.Column("comprobante", sa.Text().with_variant(MEDIUMTEXT(), "mysql"), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("revisado_por_id", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=True),
        sa.Column("revisado_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column("motivo", sa.String(255), nullable=True),
        sa.UniqueConstraint("cooperativa_id", "referencia", name="uq_promocion_referencia"))
    op.create_index("ix_promocion_vigencia", "promociones_ruta", ["estado", "hasta", "desde"])


def downgrade():
    op.drop_table("promociones_ruta")
    op.drop_column("configuracion", "aviso_operativo")
    op.drop_column("configuracion", "instrucciones_promocion")
    op.drop_column("configuracion", "precio_promocion_diaria")
    with op.batch_alter_table("buses") as batch:
        batch.drop_constraint("fk_bus_grupo", type_="foreignkey")
        batch.drop_constraint("fk_bus_modelo", type_="foreignkey")
        batch.drop_column("grupo_id")
        batch.drop_column("modelo_id")
    op.drop_table("grupos_bus")
    op.drop_table("modelos_bus")
    op.drop_table("ciudades_catalogo")
    with op.batch_alter_table("cooperativas") as batch:
        batch.drop_constraint("uq_cooperativas_ruc", type_="unique")
        for campo in ("sitio_web", "permiso_operacion", "representante_legal", "razon_social", "ruc"):
            batch.drop_column(campo)
