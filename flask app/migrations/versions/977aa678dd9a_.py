"""empty message

Revision ID: 977aa678dd9a
Revises: 
Create Date: 2021-03-11 16:18:14.141859

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '977aa678dd9a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    # ### end Alembic commands ###