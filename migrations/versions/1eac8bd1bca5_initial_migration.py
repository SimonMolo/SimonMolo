"""Initial migration

Revision ID: 1eac8bd1bca5
Revises: 
Create Date: 2023-12-23 01:12:14.337093

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1eac8bd1bca5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('SubscribeDate', sa.Date(), nullable=False),
    sa.Column('phone', sa.String(length=20), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('parrain_id', sa.Integer(), nullable=True),
    sa.Column('commentaire', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['parrain_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('filleul',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('filleul_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['filleul_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('filleul')
    op.drop_table('user')
    # ### end Alembic commands ###
