"""Añade historial de cambios a calles y tareas

Revision ID: 96a7478bc2a0
Revises: b690f93cc2d8
Create Date: 2023-06-28 07:34:42.389215

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2


# revision identifiers, used by Alembic.
revision = '96a7478bc2a0'
down_revision = 'b690f93cc2d8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('date', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('action', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['osm_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('history', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_history_date'), ['date'], unique=False)

    op.create_table('street_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('street_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['history.id'], ),
    sa.ForeignKeyConstraint(['street_id'], ['street.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('task_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('task_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['history.id'], ),
    sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('task_history')
    op.drop_table('street_history')
    with op.batch_alter_table('history', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_history_date'))

    op.drop_table('history')
    # ### end Alembic commands ###
