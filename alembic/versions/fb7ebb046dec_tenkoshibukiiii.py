"""update casetype enum to lowercase

Revision ID: fb7ebb046dec
"""

import sqlalchemy as sa

from alembic import op


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
            SELECT ARRAY_AGG(LOWER(elem::text)::casetype)
            FROM UNNEST(specializations) AS elem
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
