"""Cola transaccional para entregar boletos por correo."""
from alembic import op
import sqlalchemy as sa

revision = 'b10000000003'
down_revision = 'b10000000002'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'correos_boletos',
        sa.Column('reserva_id', sa.Integer(), sa.ForeignKey('reservas.id'), primary_key=True),
        sa.Column('destinatario', sa.String(254), nullable=False),
        sa.Column('estado', sa.String(16), nullable=False, server_default='PENDIENTE'),
        sa.Column('intentos', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('disponible_en', sa.DateTime(), nullable=False),
        sa.Column('reclamo', sa.String(32), nullable=True),
    )
    op.create_index('ix_correos_boletos_pendientes', 'correos_boletos', ['estado', 'disponible_en'])


def downgrade():
    op.drop_table('correos_boletos')
