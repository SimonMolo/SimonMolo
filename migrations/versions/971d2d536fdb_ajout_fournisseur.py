"""Ajout fournisseur

Revision ID: 971d2d536fdb
Revises: 1eac8bd1bca5
Create Date: 2023-12-23 16:26:06.542085

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '971d2d536fdb'
down_revision = '1eac8bd1bca5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('filleul', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])
        batch_op.create_foreign_key(None, 'user', ['filleul_id'], ['id'])

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('fournisseur', sa.String(length=55), nullable=False))
        batch_op.alter_column('commentaire',
               existing_type=mysql.TEXT(),
               nullable=False)
        batch_op.create_foreign_key(None, 'user', ['parrain_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('commentaire',
               existing_type=mysql.TEXT(),
               nullable=True)
        batch_op.drop_column('fournisseur')

    with op.batch_alter_table('filleul', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')

    # ### end Alembic commands ###
