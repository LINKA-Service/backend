"""update casetype enum to lowercase

Revision ID: fb7ebb046dec
Revises: 615699808b75
Create Date: 2025-12-02 05:06:00.000000

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

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
        ALTER TABLE lawyers ADD COLUMN specializations_new casetype[]
    """)

    op.execute("""
        CREATE OR REPLACE FUNCTION migrate_specializations()
        RETURNS void AS $$
        DECLARE
            r RECORD;
            spec_array text[];
            spec_item text;
            new_array casetype[];
        BEGIN
            FOR r IN SELECT id, specializations FROM lawyers LOOP
                new_array := ARRAY[]::casetype[];

                FOR spec_item IN SELECT unnest(r.specializations::text[]) LOOP
                    new_array := array_append(new_array, LOWER(spec_item)::casetype);
                END LOOP;

                UPDATE lawyers SET specializations_new = new_array WHERE id = r.id;
            END LOOP;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("SELECT migrate_specializations()")
    op.execute("DROP FUNCTION migrate_specializations()")

    op.execute("ALTER TABLE lawyers DROP COLUMN specializations")
    op.execute(
        "ALTER TABLE lawyers RENAME COLUMN specializations_new TO specializations"
    )

    op.execute("""
        ALTER TABLE lawyer_reviews
        ALTER COLUMN case_type TYPE casetype
        USING LOWER(case_type::text)::casetype
    """)

    op.execute("DROP TYPE casetype_old CASCADE")


def downgrade():
    pass
