"""Allow zero quantity on sold/expired/cancelled listings.

Revision ID: g2b3c4d5e6f7
Revises: a1b2c3d4e5f6
Create Date: 2026-09-03 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op

revision: str = "g2b3c4d5e6f7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("listings") as batch_op:
        batch_op.drop_constraint("ck_listing_quantity_positive", type_="check")
        batch_op.create_check_constraint(
            "ck_listing_quantity_positive",
            "quantity_kg > 0 OR status != 'active'",
        )


def downgrade() -> None:
    with op.batch_alter_table("listings") as batch_op:
        batch_op.drop_constraint("ck_listing_quantity_positive", type_="check")
        batch_op.create_check_constraint("ck_listing_quantity_positive", "quantity_kg > 0")
