"""Génère le dataset synthétique pour entraîner le Random Forest."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

N_USERS = 100
SESSIONS_PER_USER = 15
np.random.seed(42)

GOALS = ["perte_graisse", "renforcement_musculaire", "endurance", "sante_generale"]
LEVELS = ["debutant", "intermediaire", "avance"]
EQUIPMENTS = ["poids_du_corps", "domicile_equipé", "salle_de_sport"]
ACTIVITIES = ["musculation", "running", "hiit", "pilates"]
INJURIES = ["aucune", "genou", "epaule", "bas_dos"]

OUTPUT_DIR = Path(__file__).resolve().parent / "data"
OUTPUT_CSV = OUTPUT_DIR / "microservice_workout_training_data.csv"


def generate_dataset() -> pd.DataFrame:
    rows = []
    start_date = datetime(2026, 1, 1)

    for user_id in range(N_USERS):
        age = np.random.randint(18, 60)
        height = np.random.randint(155, 195)
        weight = np.random.randint(55, 110)
        fitness_level = np.random.choice(LEVELS, p=[0.5, 0.4, 0.1])
        health_goal = np.random.choice(GOALS)
        equipment = np.random.choice(EQUIPMENTS, p=[0.3, 0.4, 0.3])
        preferred_act = np.random.choice(ACTIVITIES)
        injury = np.random.choice(INJURIES, p=[0.75, 0.10, 0.10, 0.05])

        base_performance_modifier = (
            1.0 if fitness_level == "debutant" else (1.3 if fitness_level == "intermediaire" else 1.6)
        )

        for session_idx in range(SESSIONS_PER_USER):
            session_date = start_date + timedelta(days=session_idx * np.random.randint(2, 4))
            fatigue_rpe = np.random.randint(1, 11)
            duration_desired = np.random.choice([30, 45, 60, 90], p=[0.2, 0.4, 0.3, 0.1])

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

            rows.append(
                {
                    "user_id": f"USER_{user_id:03d}",
                    "session_date": session_date.strftime("%Y-%m-%d"),
                    "session_timestamp": int(session_date.timestamp()),
                    "age": age,
                    "height_cm": height,
                    "weight_kg": weight,
                    "fitness_level": fitness_level,
                    "health_goal": health_goal,
                    "equipment_available": equipment,
                    "preferred_activity": preferred_act,
                    "physical_limitation": injury,
                    "current_fatigue_rpe": fatigue_rpe,
                    "desired_duration_min": duration_desired,
                    "performance_history_score": performance_history_score,
                    "recommended_activity": recommended_activity,
                    "recommended_sets": recommended_sets,
                }
            )

    return pd.DataFrame(rows)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = generate_dataset()
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Dataset généré : {df.shape[0]} lignes → {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
