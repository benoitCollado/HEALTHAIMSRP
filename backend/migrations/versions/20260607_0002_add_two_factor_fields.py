"""add two factor fields

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-07 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("utilisateurs")}

    if "totp_secret" not in columns:
        op.add_column("utilisateurs", sa.Column("totp_secret", sa.String(length=64), nullable=True))

    if "totp_enabled" not in columns:
        op.add_column(
            "utilisateurs",
            sa.Column("totp_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        )
        op.alter_column("utilisateurs", "totp_enabled", server_default=None)


def downgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("utilisateurs")}

    if "totp_enabled" in columns:
        op.drop_column("utilisateurs", "totp_enabled")
    if "totp_secret" in columns:
        op.drop_column("utilisateurs", "totp_secret")
