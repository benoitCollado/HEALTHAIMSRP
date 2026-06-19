"""sync user goal flags to objectif rows

Revision ID: 0005
Revises: 0004
Create Date: 2026-06-19 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

GOAL_DEFINITIONS = (
    ("destresse", "Destresse", "Reduire mon stress"),
    ("sante", "Sante", "Ameliorer ma sante generale"),
    ("perte_de_poids", "Perte de poids", "Perdre du poids"),
    ("performance", "Performance", "Ameliorer mes performances sportives"),
    ("endurance", "Endurance", "Gagner en endurance"),
    ("force", "Force", "Developper ma force musculaire"),
)


def upgrade() -> None:
    for flag_name, type_objectif, description in GOAL_DEFINITIONS:
        op.execute(
            f"""
            INSERT INTO objectif (
                type_objectif,
                description,
                date_debut,
                date_fin,
                statut,
                id_utilisateur
            )
            SELECT
                '{type_objectif}',
                '{description}',
                u.date_inscription,
                u.date_inscription + 90,
                'en_cours',
                u.id_utilisateur
            FROM utilisateurs u
            WHERE u.{flag_name} = TRUE
              AND NOT EXISTS (
                SELECT 1
                FROM objectif o
                WHERE o.id_utilisateur = u.id_utilisateur
                  AND o.type_objectif = '{type_objectif}'
                  AND o.description = '{description}'
              )
            """
        )


def downgrade() -> None:
    for _flag_name, type_objectif, description in GOAL_DEFINITIONS:
        op.execute(
            f"""
            DELETE FROM objectif
            WHERE type_objectif = '{type_objectif}'
              AND description = '{description}'
            """
        )
