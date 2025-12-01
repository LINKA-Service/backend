"""iluvshibuki

Revision ID: f6a181086d6f
Revises: 142db7ec9e62
Create Date: 2025-12-02 00:16:54.987438

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "f6a181086d6f"
down_revision: Union[str, None] = "142db7ec9e62"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # lawyer_id 컬럼 추가 (존재하지 않을 때만)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='lawyer_reviews' AND column_name='lawyer_id'
            ) THEN
                ALTER TABLE lawyer_reviews ADD COLUMN lawyer_id INTEGER;
            END IF;
        END $$;
    """)

    # author_id 컬럼 추가 (존재하지 않을 때만)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='lawyer_reviews' AND column_name='author_id'
            ) THEN
                ALTER TABLE lawyer_reviews ADD COLUMN author_id INTEGER;
            END IF;
        END $$;
    """)

    # 인덱스 삭제 (존재할 때만)
    op.execute("""
        DROP INDEX IF EXISTS ix_lawyer_reviews_lawyername;
    """)

    # 컬럼 삭제 (존재할 때만)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='lawyer_reviews' AND column_name='lawyername'
            ) THEN
                ALTER TABLE lawyer_reviews DROP COLUMN lawyername;
            END IF;
        END $$;
    """)

    # 기존 NULL 데이터 삭제
    op.execute(
        "DELETE FROM lawyer_reviews WHERE lawyer_id IS NULL OR author_id IS NULL"
    )

    # NOT NULL 제약조건 추가
    op.execute("""
        ALTER TABLE lawyer_reviews
        ALTER COLUMN lawyer_id SET NOT NULL,
        ALTER COLUMN author_id SET NOT NULL;
    """)


def downgrade() -> None:
    op.add_column(
        "lawyer_reviews",
        sa.Column("lawyername", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.create_index(
        "ix_lawyer_reviews_lawyername", "lawyer_reviews", ["lawyername"], unique=False
    )
    op.drop_column("lawyer_reviews", "author_id")
    op.drop_column("lawyer_reviews", "lawyer_id")
