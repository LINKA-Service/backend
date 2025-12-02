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
        CREATE TEMP TABLE lawyer_specs_temp AS
        SELECT
            id,
            array_agg(LOWER(elem::text)::casetype) as new_specs
        FROM lawyers
        CROSS JOIN LATERAL unnest(specializations::text[]) AS elem
        GROUP BY id
    """)

    op.execute("""
        ALTER TABLE lawyers DROP COLUMN specializations
    """)

    op.execute("""
        ALTER TABLE lawyers ADD COLUMN specializations casetype[]
    """)

    op.execute("""
        UPDATE lawyers
        SET specializations = lawyer_specs_temp.new_specs
        FROM lawyer_specs_temp
        WHERE lawyers.id = lawyer_specs_temp.id
    """)

    op.execute("""
        ALTER TABLE lawyer_reviews
        ALTER COLUMN case_type TYPE casetype
        USING LOWER(case_type::text)::casetype
    """)

    op.execute("DROP TYPE casetype_old CASCADE")


def downgrade():
    pass
