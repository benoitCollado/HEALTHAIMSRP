#!/usr/bin/env python3
"""
Script d'import des données CSV vers la base de données.
Charge les fichiers du dossier clean/, crée utilisateurs, aliments, exercices
et activités, puis relie les données aux utilisateurs.

Usage (depuis l'hôte, avec pandas/sqlalchemy/passlib installés):
    cd HEALTHAIMSRP && PYTHONPATH=backend DATABASE_URL=postgresql://user:pass@localhost:5433/healthdb python data/seed_db.py
    # Port 5433 par défaut (configurable via POSTGRES_PORT dans .env)

Usage (Docker, avec postgres sur le réseau health_net):
    docker compose up -d postgres   # démarrer postgres
    docker compose --profile seed run --rm seed
"""

import os
import random
import sys
from datetime import date, timedelta
from pathlib import Path

# Ajouter le backend au path pour importer app
_script_dir = Path(__file__).resolve().parent
if os.getenv("DATA_DIR"):
    # Exécution depuis le conteneur Docker
    sys.path.insert(0, str(Path("/app")))
    DATA_BASE = Path(os.getenv("DATA_DIR"))
else:
    PROJECT_ROOT = _script_dir.parent
    sys.path.insert(0, str(PROJECT_ROOT / "backend"))
    DATA_BASE = _script_dir

import pandas as pd
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models.aliment import Aliment
from app.models.exercice import Exercice
from app.models.utilisateur import Utilisateur
from app.models.activite import Activite
from app.models.consommation import Consommation

# Configuration du hash de mot de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
DEFAULT_PASSWORD = "HealthAim2025!"

# Mapping niveau d'activité (diet)
ACTIVITY_LEVEL_MAP = {"Sedentary": 1, "Moderate": 2, "Active": 3}

# Mapping intensité (exercise Experience_Level 1/2/3)
INTENSITY_MAP = {1.0: "faible", 2.0: "moyenne", 3.0: "elevee"}

# Types d'exercice uniques (normalisation des variations CSV)
WORKOUT_TYPES = ["Yoga", "HIIT", "Cardio", "Strength"]
WORKOUT_NORMALIZE = {
    "yoga": "Yoga", "hiit": "HIIT", "cardio": "Cardio", "strength": "Strength",
}


def get_data_dir() -> Path:
    """Répertoire des données (dossier data/ ou DATA_DIR)."""
    return DATA_BASE


def load_csv_files() -> dict:
    """Charge les fichiers CSV du dossier clean/."""
    data_dir = get_data_dir() / "clean"
    return {
        "diet": pd.read_csv(data_dir / "diet_recommendations_clean.csv", on_bad_lines="skip"),
        "exercise": pd.read_csv(data_dir / "exercise_tracker_clean.csv", on_bad_lines="skip"),
        "food": pd.read_csv(data_dir / "daily_food_nutrition_clean.csv", on_bad_lines="skip"),
    }


def seed_aliments(session: Session, df_food: pd.DataFrame) -> dict:
    """
    Importe les aliments. Retourne un mapping nom_aliment -> id_aliment
    pour les doublons (on garde le premier).
    """
    seen = set()
    mapping = {}
    for _, row in df_food.iterrows():
        nom = str(row["Food_Item"])[:50]  # Tronquer à 50 car.
        if nom in seen:
            continue
        seen.add(nom)
        aliment = Aliment(
            nom_aliment=nom,
            calories=float(row["Calories (kcal)"]),
            proteines_g=float(row["Protein (g)"]),
            glucides_g=float(row["Carbohydrates (g)"]),
            lipides_g=float(row["Fat (g)"]),
            categorie=str(row["Category"])[:50],
        )
        session.add(aliment)
        session.flush()
        mapping[nom] = aliment.id_aliment
    return mapping


def seed_exercices(session: Session) -> dict:
    """
    Crée les 4 types d'exercice uniques.
    Retourne mapping type -> id_exercice.
    """
    mapping = {}
    for workout_type in WORKOUT_TYPES:
        exercice = Exercice(
            nom_exercice=workout_type,
            type_exercice=workout_type,
            niveau_difficulte="intermediaire",
            equipement=None,
            muscle_principal=None,
        )
        session.add(exercice)
        session.flush()
        mapping[workout_type] = exercice.id_exercice
    return mapping


def seed_utilisateurs(session: Session, df_diet: pd.DataFrame) -> list[int]:
    """Importe les utilisateurs depuis diet_recommendations. Retourne la liste des id."""
    password_hash = pwd_context.hash(DEFAULT_PASSWORD)
    user_ids = []
    for _, row in df_diet.iterrows():
        username = str(row["Patient_ID"])
        sexe = "H" if str(row["Gender"]).strip().lower() == "male" else "F"
        niveau = str(row["Physical_Activity_Level"]).strip()
        niveau_activite = ACTIVITY_LEVEL_MAP.get(niveau, 2)
        utilisateur = Utilisateur(
            username=username,
            password_hash=password_hash,
            age=int(row["Age"]),
            sexe=sexe,
            taille_cm=int(round(float(row["Height_cm"]))),
            poids_kg=int(round(float(row["Weight_kg"]))),
            niveau_activite=niveau_activite,
            type_abonnement=0,
            date_inscription=date.today(),
            is_admin=False,
        )
        try:
            existing = session.query(Utilisateur).filter(Utilisateur.username == username).first()
            if existing:
                user_ids.append(existing.id_utilisateur)
                continue
            session.add(utilisateur)
            session.flush()
            user_ids.append(utilisateur.id_utilisateur)
        except Exception as e:
            print(e + " - " + username)
        
    return user_ids


def seed_activites(
    session: Session,
    df_exercise: pd.DataFrame,
    user_ids: list[int],
    exercice_map: dict,
) -> int:
    """
    Importe les activités. Chaque session est assignée aléatoirement à un utilisateur.
    date_activite : dates réparties sur 2024.
    """
    count = 0
    start_date = date(2024, 1, 1)
    for i, row in df_exercise.iterrows():
        raw = row.get("Workout_Type")
        if pd.isna(raw) or str(raw).strip() == "":
            continue
        workout_type = WORKOUT_NORMALIZE.get(str(raw).strip().lower(), str(raw).strip())
        if workout_type not in exercice_map:
            workout_type = str(raw).strip()
        if workout_type not in exercice_map:
            continue
        id_exercice = exercice_map[workout_type]
        id_utilisateur = random.choice(user_ids)
        duree_h = float(row["Session_Duration (hours)"])
        duree_minutes = int(round(duree_h * 60))
        calories = float(row["Calories_Burned"])
        exp_level = row.get("Experience_Level")
        intensite = INTENSITY_MAP.get(exp_level, "moyenne") if pd.notna(exp_level) else "moyenne"
        # Date répartie sur 2024
        date_activite = start_date + timedelta(days=i % 365)
        activite = Activite(
            date_activite=date_activite,
            duree_minutes=duree_minutes,
            calories_depensees=calories,
            intensite=intensite,
            id_exercice=id_exercice,
            id_utilisateur=id_utilisateur,
        )
        session.add(activite)
        count += 1
    return count


def seed_consommations_synthetiques(
    session: Session,
    aliment_ids: list[int],
    user_ids: list[int],
    n: int = 500,
) -> int:
    """
    Génère N consommations synthétiques (optionnel).
    date aléatoire, aliment aléatoire, user aléatoire, quantite 100g.
    """
    if not aliment_ids or not user_ids:
        return 0
    start = date(2024, 1, 1)
    count = 0
    for _ in range(n):
        id_aliment = random.choice(aliment_ids)
        id_utilisateur = random.choice(user_ids)
        day_offset = random.randint(0, 364)
        date_consommation = start + timedelta(days=day_offset)
        quantite_g = 100.0
        # Récupérer les calories de l'aliment (requête ou cache)
        aliment = session.get(Aliment, id_aliment)
        if aliment:
            calories_calculees = round(float(aliment.calories) * (quantite_g / 100), 2)
            c = Consommation(
                date_consommation=date_consommation,
                quantite_g=quantite_g,
                calories_calculees=calories_calculees,
                id_aliment=id_aliment,
                id_utilisateur=id_utilisateur,
            )
            session.add(c)
            count += 1
    return count


def wait_for_db(max_attempts: int = 30) -> bool:
    """Attend que la base de données soit accessible."""
    import time
    from sqlalchemy import text
    for i in range(max_attempts):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                return True
        except Exception:
            if i < max_attempts - 1:
                time.sleep(2)
                print(f"  Attente de la base de données... ({i + 1}/{max_attempts})")
    return False


def main():
    """Point d'entrée principal."""
    if not os.getenv("DATABASE_URL"):
        print("Erreur: DATABASE_URL doit être défini.")
        sys.exit(1)

    print("Connexion à la base de données...")
    if not wait_for_db():
        print("Erreur: Impossible de se connecter à la base de données.")
        sys.exit(1)

    print("Chargement des CSV...")
    data = load_csv_files()
    print(f"  - diet: {len(data['diet'])} lignes")
    print(f"  - exercise: {len(data['exercise'])} lignes")
    print(f"  - food: {len(data['food'])} lignes")

    session = SessionLocal()
    try:
        print("\n1. Import des aliments...")
        aliment_map = seed_aliments(session, data["food"])
        print(f"   {len(aliment_map)} aliments importés")

        print("\n2. Import des exercices...")
        exercice_map = seed_exercices(session)
        print(f"   {len(exercice_map)} exercices importés")

        print("\n3. Import des utilisateurs...")
        user_ids = seed_utilisateurs(session, data["diet"])
        print(f"   {len(user_ids)} utilisateurs importés")

        print("\n4. Import des activités...")
        n_activites = seed_activites(session, data["exercise"], user_ids, exercice_map)
        print(f"   {n_activites} activités importées")

        print("\n5. Consommations synthétiques (optionnel)...")
        aliment_ids = list(aliment_map.values())
        n_consommations = seed_consommations_synthetiques(
            session, aliment_ids, user_ids, n=500
        )
        print(f"   {n_consommations} consommations créées")

        session.commit()
        print("\nImport terminé avec succès.")
        print(f"Mot de passe par défaut pour tous les utilisateurs: {DEFAULT_PASSWORD}")
    except Exception as e:
        session.rollback()
        print(f"\nErreur: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
