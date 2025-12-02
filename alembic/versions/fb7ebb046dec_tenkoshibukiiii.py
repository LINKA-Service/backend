"""tenkoshibukiiii

Revision ID: fb7ebb046dec
Revises: 615699808b75
Create Date: 2025-12-02 14:02:57.893508

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "fb7ebb046dec"
down_revision: Union[str, None] = "615699808b75"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE casetype RENAME TO casetype_old")

    op.execute("""
        CREATE TYPE casetype AS ENUM (
            'delivery',
            'insurance',
            'door_to_door',
            'appointment',
            'rental',
            'romance',
            'smishing',
            'false_advertising',
            'secondhand_fraud',
            'investment_scam',
            'account_takeover',
            'other'
        )
    """)

    op.execute("""
        ALTER TABLE cases
        ALTER COLUMN case_type TYPE casetype
        USING LOWER(case_type::text)::casetype
    """)

    op.execute("DROP TYPE casetype_old")


def downgrade() -> None:
    pass
