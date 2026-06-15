"""add user email

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-15 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("utilisateurs")}

    if "email" not in columns:
        op.add_column("utilisateurs", sa.Column("email", sa.String(length=255), nullable=True))
        op.execute("UPDATE utilisateurs SET email = lower(username || '@healthai.local') WHERE email IS NULL")
        op.alter_column("utilisateurs", "email", nullable=False)

    inspector = sa.inspect(bind)
    indexes = {index["name"] for index in inspector.get_indexes("utilisateurs")}
    unique_constraints = {constraint["name"] for constraint in inspector.get_unique_constraints("utilisateurs")}
    if "uq_utilisateurs_email" not in indexes and "uq_utilisateurs_email" not in unique_constraints:
        op.create_unique_constraint("uq_utilisateurs_email", "utilisateurs", ["email"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("utilisateurs")}
    unique_constraints = {constraint["name"] for constraint in inspector.get_unique_constraints("utilisateurs")}

    if "email" in columns:
        if "uq_utilisateurs_email" in unique_constraints:
            op.drop_constraint("uq_utilisateurs_email", "utilisateurs", type_="unique")
        op.drop_column("utilisateurs", "email")
