"""empty message

Revision ID: 582f981ffa5e
Revises: None
Create Date: 2013-10-12 09:24:53.387086

./run.py db --help
usage: Perform database migrations

positional arguments:
  {upgrade,migrate,current,stamp,init,downgrade,history,revision}
    upgrade             Upgrade to a later version
    migrate             Alias for 'revision --autogenerate'
    current             Display the current revision for each database.
    stamp               'stamp' the revision table with the given revision;
                        don't run any migrations
    init                Generates a new migration
    downgrade           Revert to a previous version
    history             List changeset scripts in chronological order.
    revision            Create a new revision file.

optional arguments:
  -h, --help            show this help message and exit
"""

# revision identifiers, used by Alembic.
revision = '582f981ffa5e'
down_revision = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('list_type',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=80), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('name'))

    op.create_table('job',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('list_type_id', sa.Integer(), nullable=False),
                    sa.Column('record_count', sa.Integer(), nullable=False),
                    sa.Column('status', sa.Integer(), nullable=False),
                    sa.Column('sf_job_id', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('compressed_csv', sa.LargeBinary(),
                              nullable=True),
                    sa.ForeignKeyConstraint(['list_type_id'],
                                            ['list_type.id'], ),
                    sa.PrimaryKeyConstraint('id'))
    ### end Alembic commands ###

    # Create an ad-hoc table to use for the insert statement.
    list_type_table = table('list_type',
                            column('id', Integer),
                            column('name', String))

    op.bulk_insert(list_type_table, [
        {'id': 1, 'name': 'Entire House File + Autoship'},
        {'id': 2, 'name': 'Entire House File - Autoship'},
        {'id': 3, 'name': 'Re-engagement Files'},
        {'id': 4, 'name': 'Autoship Only'},
        {'id': 5, 'name': 'Category Cross-Sell'},
        {'id': 6, 'name': 'By Product Purchased'}])


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('job')
    op.drop_table('list_type')
    ### end Alembic commands ###
