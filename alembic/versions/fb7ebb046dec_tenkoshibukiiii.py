"""update casetype enum to lowercase

Revision ID: fb7ebb046dec
Revises: 615699808b75
Create Date: 2025-12-02 05:06:00.000000

"""

import sqlalchemy as sa

from alembic import op

revision = "fb7ebb046dec"
down_revision = "615699808b75"
branch_labels = None
depends_on = None


def upgrade():
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

    op.execute("""
        ALTER TABLE lawyers
        ALTER COLUMN specializations TYPE casetype[]
        USING (
            SELECT array_agg(LOWER(elem::text)::casetype)
            FROM (SELECT unnest(specializations::text[]) AS elem) sub
        )
    """)

    op.execute("""
        ALTER TABLE lawyer_reviews
        ALTER COLUMN case_type TYPE casetype
        USING LOWER(case_type::text)::casetype
    """)

    op.execute("DROP TYPE casetype_old CASCADE")


def downgrade():
    pass
