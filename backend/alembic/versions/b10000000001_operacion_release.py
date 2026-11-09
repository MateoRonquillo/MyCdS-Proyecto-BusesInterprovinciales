"""Operación de la primera release: catálogos, tramos, comprobantes y abordaje.

Requiere respaldo previo. La reversión se realiza restaurando el respaldo:
los boletos por tramos no son representables en el esquema anterior.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = "b10000000001"
down_revision = "b1e4c7d9a205"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("usuarios", sa.Column("cooperativa_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_usuario_cooperativa", "usuarios", "cooperativas", ["cooperativa_id"], ["id"])
    op.add_column("cooperativas", sa.Column("activo", sa.Boolean(), nullable=False, server_default="1"))
    for nombre, tipo, defecto in [("chasis", sa.String(80), ""), ("carroceria", sa.String(80), ""), ("asientos_vip", sa.String(500), "")]:
        op.add_column("buses", sa.Column(nombre, tipo, nullable=False, server_default=defecto))
    op.add_column("buses", sa.Column("fotografia_url", sa.String(500), nullable=True))
    op.add_column("frecuencias", sa.Column("resolucion_ant", sa.String(150), nullable=True))
    op.add_column("reservas", sa.Column("origen_orden", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("reservas", sa.Column("destino_orden", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("reservas", sa.Column("pasajero_nombre", sa.String(100), nullable=True))
    op.add_column("reservas", sa.Column("pasajero_cedula", sa.String(15), nullable=True))
    op.add_column("pagos", sa.Column("comprobante", sa.Text().with_variant(mysql.MEDIUMTEXT(), "mysql"), nullable=True))
    op.drop_constraint("uq_reserva_asiento_activo", "reservas", type_="unique")
    op.drop_column("reservas", "asiento_activo")
    # La revisión anterior duplicaba cada índice único de boletos.
    op.drop_index("codigo", table_name="boletos")
    op.drop_index("reserva_id", table_name="boletos")
    # Las frecuencias históricas requieren completar su respaldo antes de vender.
    op.execute("UPDATE frecuencias SET activo = 0 WHERE resolucion_ant IS NULL")
    op.create_table('paradas',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('ruta_id', sa.Integer(), sa.ForeignKey('rutas.id'), nullable=False),
        sa.Column('orden', sa.Integer(), nullable=False),
        sa.Column('ciudad', sa.String(100), nullable=False),
        sa.Column('minutos', sa.Integer(), nullable=False),
        sa.Column('proporcion_tarifa', sa.Float(), nullable=False),
        sa.UniqueConstraint('ruta_id', 'orden', name='uq_parada_orden'),
    )
    op.create_table('ocupaciones_asientos',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('reserva_id', sa.Integer(), sa.ForeignKey('reservas.id'), nullable=False),
        sa.Column('frecuencia_id', sa.Integer(), sa.ForeignKey('frecuencias.id'), nullable=False),
        sa.Column('fecha_viaje', sa.Date(), nullable=False),
        sa.Column('asiento', sa.Integer(), nullable=False),
        sa.Column('segmento', sa.Integer(), nullable=False),
        sa.UniqueConstraint('frecuencia_id', 'fecha_viaje', 'asiento', 'segmento', name='uq_ocupacion_segmento'),
    )
    op.create_index('ix_ocupaciones_asientos_reserva_id', 'ocupaciones_asientos', ['reserva_id'], unique=False)
    op.create_table('jornadas',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('fecha', sa.Date(), nullable=False),
        sa.Column('bus_id', sa.Integer(), sa.ForeignKey('buses.id'), nullable=False),
        sa.Column('frecuencia_id', sa.Integer(), sa.ForeignKey('frecuencias.id'), nullable=True),
        sa.UniqueConstraint('bus_id', 'fecha', name='uq_jornada_bus'),
        sa.UniqueConstraint('frecuencia_id', 'fecha', name='uq_jornada_frecuencia'),
    )
    op.create_table('abordajes',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('boleto_id', sa.Integer(), sa.ForeignKey('boletos.id'), unique=True, nullable=False),
        sa.Column('registrado_por_id', sa.Integer(), sa.ForeignKey('usuarios.id'), nullable=False),
        sa.Column('creado_en', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table('notificaciones',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('usuario_id', sa.Integer(), sa.ForeignKey('usuarios.id'), nullable=False),
        sa.Column('mensaje', sa.String(500), nullable=False),
        sa.Column('leida', sa.Boolean(), server_default='0', nullable=False),
        sa.Column('creado_en', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_notificaciones_usuario_id', 'notificaciones', ['usuario_id'], unique=False)
    op.create_table('configuracion',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('nombre', sa.String(100), nullable=False),
        sa.Column('logo_url', sa.String(500), nullable=True),
        sa.Column('color_principal', sa.String(7), nullable=False),
        sa.Column('soporte', sa.String(150), nullable=False),
        sa.Column('redes_sociales', sa.String(500), nullable=False),
    )
    # Las reservas históricas cubrían la ruta completa (un segmento).
    op.execute("INSERT INTO ocupaciones_asientos (reserva_id, frecuencia_id, fecha_viaje, asiento, segmento) SELECT id, frecuencia_id, fecha_viaje, asiento, 0 FROM reservas WHERE estado NOT IN ('CANCELADA', 'EXPIRADA')")
    op.execute("UPDATE reservas SET pasajero_nombre = (SELECT nombre FROM usuarios WHERE usuarios.id = reservas.usuario_id), pasajero_cedula = (SELECT cedula FROM usuarios WHERE usuarios.id = reservas.usuario_id)")


def downgrade():
    raise RuntimeError("Restaurar el respaldo previo: el esquema anterior no admite boletos por tramos")
