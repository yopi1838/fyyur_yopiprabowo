"""empty message

Revision ID: 66834b2983a7
Revises: 
Create Date: 2020-05-31 15:16:24.499593

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '66834b2983a7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'seeking_talent')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('seeking_talent', sa.BOOLEAN(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###