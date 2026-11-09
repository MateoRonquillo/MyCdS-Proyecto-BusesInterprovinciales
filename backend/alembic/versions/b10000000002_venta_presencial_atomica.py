"""Venta presencial atómica con clave de reintento."""
from alembic import op
import sqlalchemy as sa

revision = 'b10000000002'
down_revision = 'b10000000001'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('ventas_presenciales',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('clave', sa.String(64), nullable=False, unique=True),
        sa.Column('huella', sa.String(64), nullable=False),
        sa.Column('usuario_id', sa.Integer(), sa.ForeignKey('usuarios.id'), nullable=False),
        sa.Column('reserva_id', sa.Integer(), sa.ForeignKey('reservas.id'), nullable=False, unique=True),
        sa.Column('pago_id', sa.Integer(), sa.ForeignKey('pagos.id'), nullable=False, unique=True))


def downgrade():
    op.drop_table('ventas_presenciales')
