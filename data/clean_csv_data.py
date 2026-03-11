import glob
import os
from pathlib import Path

import pandas as pd


def get_data_dir() -> Path:
    return Path(__file__).parent


def load_csv_files(data_dir: Path) -> dict:
    df_food = pd.read_csv(
        data_dir / "daily_food_nutrition_dataset.csv",
        on_bad_lines="skip"
    )
    df_diet = pd.read_csv(
        data_dir / "diet_recommendations_dataset.csv",
        on_bad_lines="skip"
    )
    df_members = pd.read_csv(
        data_dir / "gym_meber.csv",
        on_bad_lines="skip"
    )
    df_exercises = pd.read_csv(
        data_dir / "exercices.csv",
        on_bad_lines="skip"
    )
    return {
        "food": df_food,
        "diet": df_diet,
        "members": df_members,
        "exercises": df_exercises,
    }


def clean_string_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.columns:
        if df[col].dtype in ("object", "string"):
            df[col] = (
                df[col]
                .str.replace("\t", "", regex=False)
                .str.replace("\n", "", regex=False)
                .str.strip()
            )
    return df


def clean_food_data(df: pd.DataFrame) -> pd.DataFrame:
    return clean_string_columns(df)


def clean_diet_data(df: pd.DataFrame) -> pd.DataFrame:
    df = clean_string_columns(df)
    # Remplit les valeurs manquantes (NaN et chaînes vides)
    if "Gender" in df.columns:
        df["Gender"] = df["Gender"].replace("", pd.NA).fillna("Other")
    if "Disease_Type" in df.columns:
        df["Disease_Type"] = df["Disease_Type"].replace("", pd.NA).fillna("no_disease")
    if "Dietary_Restrictions" in df.columns:
        df["Dietary_Restrictions"] = df["Dietary_Restrictions"].replace("", pd.NA).fillna("no_dietary_restriction")
    if "Allergies" in df.columns:
        df["Allergies"] = df["Allergies"].replace("", pd.NA).fillna("no_allergies")
    return df


def clean_exercise_data(df_members: pd.DataFrame, df_exercises: pd.DataFrame) -> pd.DataFrame:
    df_merged = pd.concat([df_members, df_exercises], axis=0, ignore_index=True)
    df_merged = clean_string_columns(df_merged)
    # Remplit les valeurs manquantes de Gender par "Other"
    if "Gender" in df_merged.columns:
        df_merged["Gender"] = df_merged["Gender"].fillna("Other")
    # Supprime les lignes avec des valeurs manquantes (comme dans le notebook)
    df_merged = df_merged.dropna()
    return df_merged


def save_clean_data(dataframes: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    file_mapping = {
        "food": "daily_food_nutrition_clean.csv",
        "diet": "diet_recommendations_clean.csv",
        "exercise": "exercise_tracker_clean.csv",
    }

    for key, filename in file_mapping.items():
        if key in dataframes:
            filepath = output_dir / filename
            dataframes[key].to_csv(filepath, index=False, encoding="utf-8")
            print(f"  ✓ {filename} ({len(dataframes[key])} lignes)")


def main():
    data_dir = get_data_dir()
    output_dir = data_dir / "clean"

    print("Chargement des fichiers CSV...")
    raw_data = load_csv_files(data_dir)

    print("Nettoyage des données...")
    df_food_clean = clean_food_data(raw_data["food"])
    df_diet_clean = clean_diet_data(raw_data["diet"])
    df_exercise_clean = clean_exercise_data(
        raw_data["members"],
        raw_data["exercises"]
    )

    clean_data = {
        "food": df_food_clean,
        "diet": df_diet_clean,
        "exercise": df_exercise_clean,
    }

    print(f"Sauvegarde dans {output_dir}...")
    save_clean_data(clean_data, output_dir)

    print("\nRésumé :")
    print(f"  - Food: {len(df_food_clean)} lignes")
    print(f"  - Diet: {len(df_diet_clean)} lignes")
    print(f"  - Exercise (fusion gym + exercices): {len(df_exercise_clean)} lignes")
    print("\nTerminé.")


if __name__ == "__main__":
    main()
