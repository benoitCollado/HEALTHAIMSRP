"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-04-29 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "utilisateurs",
        sa.Column("id_utilisateur", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(50), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("sexe", sa.String(1), nullable=False),
        sa.Column("taille_cm", sa.Integer(), nullable=False),
        sa.Column("poids_kg", sa.Integer(), nullable=False),
        sa.Column("niveau_activite", sa.Integer(), nullable=False),
        sa.Column("type_abonnement", sa.Integer(), nullable=False),
        sa.Column("date_inscription", sa.Date(), nullable=False,
                  server_default=sa.text("CURRENT_DATE")),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )

    op.create_table(
        "aliment",
        sa.Column("id_aliment", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("nom_aliment", sa.String(50), nullable=False),
        sa.Column("calories", sa.Numeric(6, 2), nullable=False),
        sa.Column("proteines_g", sa.Numeric(6, 2), nullable=False),
        sa.Column("glucides_g", sa.Numeric(6, 2), nullable=False),
        sa.Column("lipides_g", sa.Numeric(6, 2), nullable=False),
        sa.Column("categorie", sa.String(50), nullable=False),
        sa.Column("sucres_g", sa.Numeric(6, 2), nullable=True),
        sa.Column("acides_gras_satures_g", sa.Numeric(6, 2), nullable=True),
    )

    op.create_table(
        "exercice",
        sa.Column("id_exercice", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("nom_exercice", sa.String(100), nullable=False),
        sa.Column("type_exercice", sa.String(50), nullable=False),
        sa.Column("niveau_difficulte", sa.String(20), nullable=False),
        sa.Column("equipement", sa.String(50), nullable=True),
        sa.Column("muscle_principal", sa.String(30), nullable=True),
    )

    op.create_table(
        "objectif",
        sa.Column("id_objectif", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("type_objectif", sa.String(20), nullable=False),
        sa.Column("description", sa.String(250), nullable=False),
        sa.Column("date_debut", sa.Date(), nullable=False),
        sa.Column("date_fin", sa.Date(), nullable=False),
        sa.Column("statut", sa.String(10), nullable=False),
        sa.Column("id_utilisateur", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["id_utilisateur"], ["utilisateurs.id_utilisateur"],
                                ondelete="CASCADE"),
    )

    op.create_table(
        "consommation",
        sa.Column("id_consommation", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("date_consommation", sa.Date(), nullable=False),
        sa.Column("quantite_g", sa.Numeric(6, 2), nullable=False),
        sa.Column("calories_calculees", sa.Numeric(6, 2), nullable=False),
        sa.Column("id_aliment", sa.Integer(), nullable=False),
        sa.Column("id_utilisateur", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["id_aliment"], ["aliment.id_aliment"]),
        sa.ForeignKeyConstraint(["id_utilisateur"], ["utilisateurs.id_utilisateur"],
                                ondelete="CASCADE"),
    )

    op.create_table(
        "activite",
        sa.Column("id_activite", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("date_activite", sa.Date(), nullable=False),
        sa.Column("duree_minutes", sa.Integer(), nullable=False),
        sa.Column("calories_depensees", sa.Numeric(6, 2), nullable=False),
        sa.Column("intensite", sa.String(20), nullable=True),
        sa.Column("id_exercice", sa.Integer(), nullable=False),
        sa.Column("id_utilisateur", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["id_exercice"], ["exercice.id_exercice"]),
        sa.ForeignKeyConstraint(["id_utilisateur"], ["utilisateurs.id_utilisateur"],
                                ondelete="CASCADE"),
    )

    op.create_table(
        "metrique_sante",
        sa.Column("id_metrique", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("date_mesure", sa.Date(), nullable=False),
        sa.Column("poids_kg", sa.Numeric(5, 2), nullable=True),
        sa.Column("frequence_cardiaque", sa.SmallInteger(), nullable=True),
        sa.Column("duree_sommeil_h", sa.Numeric(4, 2), nullable=True),
        sa.Column("calories_brulees", sa.Integer(), nullable=True),
        sa.Column("pas", sa.Integer(), nullable=True),
        sa.Column("id_utilisateur", sa.Integer(), nullable=False),
        sa.UniqueConstraint("id_utilisateur", "date_mesure", name="uq_metrique_jour"),
        sa.ForeignKeyConstraint(["id_utilisateur"], ["utilisateurs.id_utilisateur"],
                                ondelete="CASCADE"),
    )


def downgrade() -> None:
    op.drop_table("metrique_sante")
    op.drop_table("activite")
    op.drop_table("consommation")
    op.drop_table("objectif")
    op.drop_table("exercice")
    op.drop_table("aliment")
    op.drop_table("utilisateurs")
