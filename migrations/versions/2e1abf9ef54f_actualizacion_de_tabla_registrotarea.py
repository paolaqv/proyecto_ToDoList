"""actualizacion de tabla registroTarea

Revision ID: 2e1abf9ef54f
Revises: 126fca0c0fbd
Create Date: 2024-03-11 16:36:59.145290

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2e1abf9ef54f'
down_revision = '126fca0c0fbd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('registro_tareas', schema=None) as batch_op:
        batch_op.alter_column('recordar',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.String(length=255),
               existing_nullable=True)
        batch_op.drop_constraint('registro_tareas_usuario_id_fkey', type_='foreignkey')
        batch_op.drop_column('usuario_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('registro_tareas', schema=None) as batch_op:
        batch_op.add_column(sa.Column('usuario_id', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.create_foreign_key('registro_tareas_usuario_id_fkey', 'usuarios', ['usuario_id'], ['id'])
        batch_op.alter_column('recordar',
               existing_type=sa.String(length=255),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)

    # ### end Alembic commands ###
