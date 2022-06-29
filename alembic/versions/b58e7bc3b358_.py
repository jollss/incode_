"""empty message

Revision ID: b58e7bc3b358
Revises: 94d659857a32
Create Date: 2022-06-29 13:43:49.787550

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = 'b58e7bc3b358'
down_revision = '94d659857a32'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('curp_verifications', sa.Column('result', sa.String(length=255), nullable=True))
    op.add_column('sessions', sa.Column('retries', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sessions', 'retries')
    op.drop_column('curp_verifications', 'result')
    # ### end Alembic commands ###
