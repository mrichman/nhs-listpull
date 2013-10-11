"""empty message

Revision ID: 384cfaaaa0be
Revises: None
Create Date: 2013-10-11 16:36:34.696069

"""

# revision identifiers, used by Alembic.
revision = '384cfaaaa0be'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('list_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('job',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('list_type_id', sa.Integer(), nullable=False),
    sa.Column('record_count', sa.Integer(), nullable=False),
    sa.Column('status', sa.Integer(), nullable=False),
    sa.Column('sf_job_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('compressed_csv', sa.LargeBinary(), nullable=True),
    sa.ForeignKeyConstraint(['list_type_id'], ['list_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('job')
    op.drop_table('list_type')
    ### end Alembic commands ###
