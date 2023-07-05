"""Separa bloqueo de historial de tarea

Revision ID: bd17058f2eb4
Revises: e8338fc6e522
Create Date: 2023-07-05 16:19:00.351646

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2


# revision identifiers, used by Alembic.
revision = 'bd17058f2eb4'
down_revision = 'e8338fc6e522'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('task_lock',
    sa.Column('timeout', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('text', sa.String(), nullable=True),
    sa.Column('buildings', sa.Boolean(), nullable=False),
    sa.Column('addresses', sa.Boolean(), nullable=False),
    sa.CheckConstraint('buildings OR addresses', name='ck_bd_or_ad'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    with op.batch_alter_table('task_lock', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_task_lock_date'), ['date'], unique=False)

    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.add_column(sa.Column('lock_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('ix_task_lock_date', 'task_lock', ['lock_id'], ['id'])

    with op.batch_alter_table('task_history', schema=None) as batch_op:
        batch_op.add_column(sa.Column('text', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('task_history', schema=None) as batch_op:
        batch_op.drop_column('text')

    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.drop_constraint('ix_task_lock_date', type_='foreignkey')
        batch_op.drop_column('lock_id')

    with op.batch_alter_table('task_lock', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_task_lock_date'))

    op.drop_table('task_lock')
    # ### end Alembic commands ###