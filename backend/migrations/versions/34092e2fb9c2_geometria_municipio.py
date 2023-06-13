"""Geometria municipio

Revision ID: 34092e2fb9c2
Revises: e7a6232f234a
Create Date: 2023-06-05 11:08:01.958318

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision = '34092e2fb9c2'
down_revision = 'e7a6232f234a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('municipality', schema=None) as batch_op:
        batch_op.add_column(sa.Column('geom', Geometry(geometry_type='GEOMETRYCOLLECTION', srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=True))
        # batch_op.create_index('idx_municipality_geom', ['geom'], unique=False, postgresql_using='gist')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('municipality', schema=None) as batch_op:
        # batch_op.drop_index('idx_municipality_geom', postgresql_using='gist')
        batch_op.drop_column('geom')

    # ### end Alembic commands ###