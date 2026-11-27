"""Asignación de ayudante por jornada."""
from alembic import op
import sqlalchemy as sa

revision = 'b10000000005'
down_revision = 'b10000000004'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('jornadas', sa.Column('ayudante_id', sa.Integer(), nullable=True))
    op.create_unique_constraint('uq_jornada_ayudante', 'jornadas', ['ayudante_id', 'fecha'])
    op.create_foreign_key('fk_jornada_ayudante', 'jornadas', 'usuarios', ['ayudante_id'], ['id'])


def downgrade():
    op.drop_constraint('fk_jornada_ayudante', 'jornadas', type_='foreignkey')
    op.drop_constraint('uq_jornada_ayudante', 'jornadas', type_='unique')
    op.drop_column('jornadas', 'ayudante_id')
