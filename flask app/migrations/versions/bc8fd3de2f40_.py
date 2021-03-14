"""empty message

Revision ID: bc8fd3de2f40
Revises: d633c23a41de
Create Date: 2021-03-11 17:42:45.883536

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bc8fd3de2f40'
down_revision = 'd633c23a41de'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('transfer',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('from_id', sa.Integer(), nullable=False),
    sa.Column('to_id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transfer')
    # ### end Alembic commands ###
