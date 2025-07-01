"""
Initialisation.

Revision ID: 1d68ab53e0bb
Revises:
Create Date: 2025-06-30 10:53:51.305527
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = '1d68ab53e0bb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # check if tables already exist
    bind = op.get_bind()
    insp = Inspector.from_engine(bind)
    all_table_names = insp.get_table_names()

    if 'ckanpackager_stats' not in all_table_names:
        op.create_table(
            'ckanpackager_stats',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('inserted_on', sa.DateTime, default=sa.func.now()),
            sa.Column('count', sa.Integer),
            sa.Column('resource_id', sa.UnicodeText),
        )

    if 'gbif_downloads' not in all_table_names:
        op.create_table(
            'gbif_downloads',
            sa.Column('doi', sa.UnicodeText, primary_key=True),
            sa.Column('date', sa.DateTime),
            sa.Column('inserted_on', sa.DateTime, default=sa.func.now()),
            sa.Column('count', sa.Integer),
        )


def downgrade():
    op.drop_table('ckanpackager_stats')
    op.drop_table('gbif_downloads')
