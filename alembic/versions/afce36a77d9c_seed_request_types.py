"""seed request_types

Revision ID: afce36a77d9c
Revises: a4bbd3391e7a
Create Date: 2026-11-12 10:07:51.137558

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import uuid
from decimal import Decimal

# revision identifiers, used by Alembic.
revision: str = 'afce36a77d9c'
down_revision: Union[str, Sequence[str], None] = 'a4bbd3391e7a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

request_types = sa.table(
    "request_types",
    sa.column("id", sa.Uuid),
    sa.column("code", sa.String),
    sa.column("name", sa.String),
    sa.column("requires_amount", sa.Boolean),
    sa.column("approval_threshold", sa.Numeric),
)

SEED_CODES = ["expense", "equipment", "access"]

def upgrade() -> None:
     op.bulk_insert(
        request_types,
        [
            {
                "id": uuid.uuid4(),
                "code": "expense",
                "name": "Trošak",
                "requires_amount": True,
                "approval_threshold": Decimal("50000.00"),
            },
            {
                "id": uuid.uuid4(),
                "code": "equipment",
                "name": "Oprema",
                "requires_amount": True,
                "approval_threshold": Decimal("100000.00"),
            },
            {
                "id": uuid.uuid4(),
                "code": "access",
                "name": "Pristup sistemu",
                "requires_amount": False,
                "approval_threshold": None,
            },
        ],
    )


def downgrade() -> None:
    op.execute(request_types.delete().where(request_types.c.code.in_(SEED_CODES)))
