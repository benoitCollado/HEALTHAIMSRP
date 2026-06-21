"""Génère le dataset d'entraînement à partir d'un CSV de profils de base."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

SESSIONS_PER_USER = 15
np.random.seed(42)

GOALS = ["perte_graisse", "renforcement_musculaire", "endurance", "sante_generale"]
LEVELS = ["debutant", "intermediaire", "avance"]
EQUIPMENTS = ["poids_du_corps", "domicile_equipé", "salle_de_sport"]
ACTIVITIES = ["musculation", "running", "hiit", "pilates"]
INJURIES = ["aucune", "genou", "epaule", "bas_dos"]

ML_DIR = Path(__file__).resolve().parent
INPUT_DIR = ML_DIR / "input"
OUTPUT_DIR = ML_DIR / "data"
INPUT_BASE_CSV = INPUT_DIR / "base_profiles.csv"
OUTPUT_CSV = OUTPUT_DIR / "microservice_workout_training_data.csv"

BASE_PROFILE_COLUMNS = [
    "user_id",
    "age",
    "height_cm",
    "weight_kg",
    "fitness_level",
    "health_goal",
    "equipment_available",
    "preferred_activity",
    "physical_limitation",
]


def generate_base_profiles(n_users: int = 100) -> pd.DataFrame:
    """Crée le CSV d'entrée : un profil utilisateur par ligne."""
    rows = []
    for user_idx in range(n_users):
        rows.append(
            {
                "user_id": f"USER_{user_idx:03d}",
                "age": int(np.random.randint(18, 60)),
                "height_cm": int(np.random.randint(155, 195)),
                "weight_kg": int(np.random.randint(55, 110)),
                "fitness_level": np.random.choice(LEVELS, p=[0.5, 0.4, 0.1]),
                "health_goal": np.random.choice(GOALS),
                "equipment_available": np.random.choice(EQUIPMENTS, p=[0.3, 0.4, 0.3]),
                "preferred_activity": np.random.choice(ACTIVITIES),
                "physical_limitation": np.random.choice(INJURIES, p=[0.75, 0.10, 0.10, 0.05]),
            }
        )
    return pd.DataFrame(rows, columns=BASE_PROFILE_COLUMNS)


def write_base_profiles(path: Path = INPUT_BASE_CSV, n_users: int = 100) -> pd.DataFrame:
    path.parent.mkdir(parents=True, exist_ok=True)
    df = generate_base_profiles(n_users=n_users)
    df.to_csv(path, index=False)
    return df


def load_base_profiles(path: Path = INPUT_BASE_CSV) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"CSV d'entrée introuvable : {path}. "
            f"Lancez : python -m ml.generate_training_data --generate-base"
        )
    df = pd.read_csv(path)
    missing = [col for col in BASE_PROFILE_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes dans {path} : {missing}")
    return df[BASE_PROFILE_COLUMNS].copy()


def expand_profiles_to_sessions(base_df: pd.DataFrame, sessions_per_user: int = SESSIONS_PER_USER) -> pd.DataFrame:
    """Étape A : enrichit chaque profil avec le contexte de séance simulé."""
    rows = []
    start_date = datetime(2026, 1, 1)

    for _, profile in base_df.iterrows():
        for session_idx in range(sessions_per_user):
            session_date = start_date + timedelta(days=session_idx * np.random.randint(2, 4))
            rows.append(
                {
                    "user_id": profile["user_id"],
                    "session_date": session_date.strftime("%Y-%m-%d"),
                    "session_timestamp": int(session_date.timestamp()),
                    "age": int(profile["age"]),
                    "height_cm": int(profile["height_cm"]),
                    "weight_kg": int(profile["weight_kg"]),
                    "fitness_level": profile["fitness_level"],
                    "health_goal": profile["health_goal"],
                    "equipment_available": profile["equipment_available"],
                    "preferred_activity": profile["preferred_activity"],
                    "physical_limitation": profile["physical_limitation"],
                    "current_fatigue_rpe": int(np.random.randint(1, 11)),
                    "desired_duration_min": int(
                        np.random.choice([30, 45, 60, 90], p=[0.2, 0.4, 0.3, 0.1])
                    ),
                    "_session_idx": session_idx,
                }
            )

    return pd.DataFrame(rows)


def apply_label_rules(row: pd.Series) -> tuple[float, str, int]:
    """Étape B : calcule score, activité recommandée et nombre de séries."""
    fitness_level = row["fitness_level"]
    health_goal = row["health_goal"]
    injury = row["physical_limitation"]
    preferred_act = row["preferred_activity"]
    fatigue_rpe = row["current_fatigue_rpe"]
    session_idx = row["_session_idx"]

    base_performance_modifier = (
        1.0 if fitness_level == "debutant" else (1.3 if fitness_level == "intermediaire" else 1.6)
    )
    performance_history_score = (base_performance_modifier * 10) + (session_idx * 0.3) - (fatigue_rpe * 0.2)
    performance_history_score = round(max(5.0, performance_history_score), 2)

    if injury == "genou":
        recommended_activity = "pilates" if health_goal == "sante_generale" else "musculation"
    elif injury == "epaule" and health_goal == "renforcement_musculaire":
        recommended_activity = "musculation"
    elif health_goal == "perte_graisse":
        recommended_activity = np.random.choice(["hiit", "running"], p=[0.6, 0.4])
    elif health_goal == "endurance":
        recommended_activity = "running"
    else:
        recommended_activity = preferred_act

    base_sets = 3 if fitness_level == "debutant" else (4 if fitness_level == "intermediaire" else 5)
    if session_idx > 10:
        base_sets += 1
    if fatigue_rpe >= 8:
        base_sets -= 2
    elif fatigue_rpe >= 5:
        base_sets -= 1
    recommended_sets = int(np.clip(base_sets, 2, 6))

    return performance_history_score, recommended_activity, recommended_sets


def enrich_with_labels(sessions_df: pd.DataFrame) -> pd.DataFrame:
    """Étape B : ajoute labels et feature dérivée au dataset session-level."""
    labels = sessions_df.apply(apply_label_rules, axis=1, result_type="expand")
    labels.columns = ["performance_history_score", "recommended_activity", "recommended_sets"]
    return pd.concat([sessions_df.drop(columns=["_session_idx"]), labels], axis=1)


def generate_dataset(input_path: Path | None = None) -> pd.DataFrame:
    base_df = load_base_profiles(input_path or INPUT_BASE_CSV)
    sessions_df = expand_profiles_to_sessions(base_df)
    return enrich_with_labels(sessions_df)


def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline CSV base → dataset d'entraînement")
    parser.add_argument(
        "--generate-base",
        action="store_true",
        help="Génère ml/input/base_profiles.csv (100 profils) puis le dataset",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=INPUT_BASE_CSV,
        help="Chemin du CSV de profils de base",
    )
    args = parser.parse_args()

    if args.generate_base or not args.input.exists():
        np.random.seed(42)
        write_base_profiles(args.input)
        print(f"CSV de base généré : {args.input}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = generate_dataset(args.input)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Dataset généré : {df.shape[0]} lignes → {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
