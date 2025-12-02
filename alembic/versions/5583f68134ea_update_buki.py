"""update_buki

Revision ID: 5583f68134ea
Revises: fb7ebb046dec
Create Date: 2025-12-02 15:09:55.916853

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "5583f68134ea"
down_revision: Union[str, None] = "fb7ebb046dec"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE casestatus RENAME TO casestatus_old")

    op.execute("""
        CREATE TYPE casestatus AS ENUM (
            'pending',
            'approved',
            'rejected'
        )
    """)

    op.execute("""
        ALTER TABLE cases
        ALTER COLUMN status TYPE casestatus
        USING LOWER(status::text)::casestatus
    """)

    op.execute("DROP TYPE casestatus_old")


def downgrade() -> None:
    pass
