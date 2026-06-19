"""add user goal flags

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-19 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

USER_GOAL_FLAGS = (
    "destresse",
    "sante",
    "perte_de_poids",
    "performance",
    "endurance",
    "force",
)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("utilisateurs")}

    for column_name in USER_GOAL_FLAGS:
        if column_name not in columns:
            op.add_column(
                "utilisateurs",
                sa.Column(column_name, sa.Boolean(), nullable=False, server_default=sa.text("false")),
            )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("utilisateurs")}

    for column_name in reversed(USER_GOAL_FLAGS):
        if column_name in columns:
            op.drop_column("utilisateurs", column_name)
