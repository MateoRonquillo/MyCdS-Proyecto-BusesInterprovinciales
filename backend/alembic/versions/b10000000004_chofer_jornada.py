"""Asignación de chofer por jornada."""
from alembic import op
import sqlalchemy as sa

revision = 'b10000000004'
down_revision = 'b10000000003'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('jornadas', sa.Column('chofer_id', sa.Integer(), nullable=True))
    op.create_unique_constraint('uq_jornada_chofer', 'jornadas', ['chofer_id', 'fecha'])
    op.create_foreign_key('fk_jornada_chofer', 'jornadas', 'usuarios', ['chofer_id'], ['id'])


def downgrade():
    op.drop_constraint('fk_jornada_chofer', 'jornadas', type_='foreignkey')
    op.drop_constraint('uq_jornada_chofer', 'jornadas', type_='unique')
    op.drop_column('jornadas', 'chofer_id')
