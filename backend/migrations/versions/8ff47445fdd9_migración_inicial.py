"""Migración inicial

Revision ID: 8ff47445fdd9
Revises: 
Create Date: 2023-04-22 07:30:09.680415

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2
from geoalchemy2 import Geometry
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8ff47445fdd9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('task',
    sa.Column('muncode', sa.String(), nullable=False),
    sa.Column('localId', sa.String(), nullable=False),
    sa.Column('zone', sa.String(), nullable=True),
    sa.Column('type', sa.String(), nullable=True),
    sa.Column('parts', sa.Integer(), nullable=True),
    sa.Column('task_status', sa.Integer(), nullable=True),
    sa.Column('geom', Geometry(geometry_type='MULTIPOLYGON', srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=True),
    sa.PrimaryKeyConstraint('muncode', 'localId')
    )
    # with op.batch_alter_table('task', schema=None) as batch_op:
    #     batch_op.create_index('idx_task_geom', ['geom'], unique=False, postgresql_using='gist')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # with op.batch_alter_table('task', schema=None) as batch_op:
    #     batch_op.drop_index('idx_task_geom', postgresql_using='gist')

    op.drop_table('task')
    # ### end Alembic commands ###
