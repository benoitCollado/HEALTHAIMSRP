"""Entraîne les Random Forest avec CV, recherche d'hyperparamètres et rapport de métriques."""

from __future__ import annotations

import json
import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import GridSearchCV, GroupKFold, train_test_split

from ml.data_prep import TARGET_CLASS, prepare_matrices
from ml.evaluation import (
    build_metrics_summary,
    cross_validate_classifier,
    cross_validate_regressor,
    evaluate_classifier,
    evaluate_regressor,
    format_search_results,
)
from ml.generate_training_data import OUTPUT_CSV, OUTPUT_DIR, generate_dataset

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
BUNDLE_PATH = MODELS_DIR / "workout_rf_bundle.pkl"
REPORT_PATH = MODELS_DIR / "training_report.json"

CV_FOLDS = int(os.getenv("ML_CV_FOLDS", "5"))
RANDOM_STATE = 42


def _fast_mode() -> bool:
    return os.getenv("ML_FAST_TRAIN", "0") == "1"


def _classifier_param_grid() -> dict:
    if _fast_mode():
        return {
            "n_estimators": [80, 120],
            "max_depth": [10, 12],
            "min_samples_split": [2],
            "min_samples_leaf": [1, 2],
        }
    return {
        "n_estimators": [80, 120, 160],
        "max_depth": [8, 12, 16, None],
        "min_samples_split": [2, 5],
        "min_samples_leaf": [1, 2],
        "max_features": ["sqrt", "log2"],
    }


def _regressor_param_grid() -> dict:
    if _fast_mode():
        return {
            "n_estimators": [80, 120],
            "max_depth": [8, 10],
            "min_samples_split": [2],
            "min_samples_leaf": [1, 2],
        }
    return {
        "n_estimators": [80, 120, 160],
        "max_depth": [6, 10, 14, None],
        "min_samples_split": [2, 5],
        "min_samples_leaf": [1, 2],
        "max_features": ["sqrt", "log2"],
    }


def load_or_generate_csv() -> pd.DataFrame:
    if not OUTPUT_CSV.exists():
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        df = generate_dataset()
        df.to_csv(OUTPUT_CSV, index=False)
        return df
    return pd.read_csv(OUTPUT_CSV)


def search_best_classifier(x_train, y_train, groups_train) -> tuple[RandomForestClassifier, dict]:
    base = RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1)
    cv = GroupKFold(n_splits=CV_FOLDS)
    search = GridSearchCV(
        base,
        param_grid=_classifier_param_grid(),
        scoring="f1_weighted",
        cv=cv,
        n_jobs=-1,
        refit=True,
        verbose=0,
    )
    search.fit(x_train, y_train, groups=groups_train)
    return search.best_estimator_, format_search_results(search)


def search_best_regressor(x_train, y_train, groups_train) -> tuple[RandomForestRegressor, dict]:
    base = RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1)
    cv = GroupKFold(n_splits=CV_FOLDS)
    search = GridSearchCV(
        base,
        param_grid=_regressor_param_grid(),
        scoring="neg_mean_absolute_error",
        cv=cv,
        n_jobs=-1,
        refit=True,
        verbose=0,
    )
    search.fit(x_train, y_train, groups=groups_train)
    return search.best_estimator_, format_search_results(search)


def train() -> dict:
    df = load_or_generate_csv()
    x, y_class, y_reg, groups, meta = prepare_matrices(df)

    split = train_test_split(
        x,
        y_class,
        y_reg,
        groups,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y_class,
    )
    x_train, x_test, y_class_train, y_class_test, y_reg_train, y_reg_test, groups_train, _groups_test = split

    classifier, classifier_search = search_best_classifier(x_train, y_class_train, groups_train)
    regressor, regressor_search = search_best_regressor(x_train, y_reg_train, groups_train)

    class_pred = classifier.predict(x_test)
    reg_pred = regressor.predict(x_test)

    activity_labels = meta["encoders"][TARGET_CLASS].classes_.tolist()
    test_classifier_metrics = evaluate_classifier(y_class_test, class_pred, class_labels=activity_labels)
    test_regressor_metrics = evaluate_regressor(y_reg_test, reg_pred)

    cv_classifier_metrics = cross_validate_classifier(classifier, x_train, y_class_train, groups_train, CV_FOLDS)
    cv_regressor_metrics = cross_validate_regressor(regressor, x_train, y_reg_train, groups_train, CV_FOLDS)

    metrics_tables = build_metrics_summary(
        test_classifier_metrics,
        test_regressor_metrics,
        cv_classifier_metrics,
        cv_regressor_metrics,
    )

    metrics = {
        "accuracy_activity": test_classifier_metrics["accuracy"],
        "f1_weighted_activity": test_classifier_metrics["f1_weighted"],
        "mae_sets": test_regressor_metrics["mae"],
        "rmse_sets": test_regressor_metrics["rmse"],
        "r2_sets": test_regressor_metrics["r2"],
        "train_samples": len(x_train),
        "test_samples": len(x_test),
        "cv_folds": CV_FOLDS,
        "test": {
            "classifier": test_classifier_metrics,
            "regressor": test_regressor_metrics,
        },
        "cross_validation": {
            "classifier": cv_classifier_metrics,
            "regressor": cv_regressor_metrics,
        },
        "tables": metrics_tables,
    }

    output_classes = {
        "classification": {
            "target": TARGET_CLASS,
            "classes": activity_labels,
            "type": "multiclass",
        },
        "regression": {
            "target": "recommended_sets",
            "type": "integer",
            "plage": [2, 6],
        },
    }

    hyperparameter_search = {
        "classifier": classifier_search,
        "regressor": regressor_search,
        "scoring_classifier": "f1_weighted",
        "scoring_regressor": "neg_mean_absolute_error",
        "cv_strategy": f"GroupKFold(n_splits={CV_FOLDS}) by user_id",
    }

    return {
        "version": "2.0",
        "classifier": classifier,
        "regressor": regressor,
        "encoders": meta["encoders"],
        "feature_columns": meta["feature_columns"],
        "output_classes": output_classes,
        "best_params": {
            "classifier": classifier_search["best_params"],
            "regressor": regressor_search["best_params"],
        },
        "metrics": metrics,
        "hyperparameter_search": hyperparameter_search,
    }


def save_report(bundle: dict) -> None:
    report = {
        "version": bundle["version"],
        "output_classes": bundle["output_classes"],
        "best_params": bundle["best_params"],
        "metrics": bundle["metrics"],
        "hyperparameter_search": {
            "classifier": {
                "best_params": bundle["hyperparameter_search"]["classifier"]["best_params"],
                "best_score": bundle["hyperparameter_search"]["classifier"]["best_score"],
            },
            "regressor": {
                "best_params": bundle["hyperparameter_search"]["regressor"]["best_params"],
                "best_score": bundle["hyperparameter_search"]["regressor"]["best_score"],
            },
            "cv_strategy": bundle["hyperparameter_search"]["cv_strategy"],
        },
        "feature_columns": bundle["feature_columns"],
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    bundle = train()
    joblib.dump(bundle, BUNDLE_PATH)
    save_report(bundle)

    print(f"Modèle exporté → {BUNDLE_PATH}")
    print(f"Rapport      → {REPORT_PATH}")
    print("\n=== Meilleurs hyperparamètres ===")
    print(json.dumps(bundle["best_params"], indent=2, ensure_ascii=False))
    print("\n=== Métriques test ===")
    print(f"  Activité  — accuracy: {bundle['metrics']['accuracy_activity']}, f1_weighted: {bundle['metrics']['f1_weighted_activity']}")
    print(f"  Séries    — MAE: {bundle['metrics']['mae_sets']}, RMSE: {bundle['metrics']['rmse_sets']}, R²: {bundle['metrics']['r2_sets']}")
    print("\n=== Cross-validation (moyenne test) ===")
    cv = bundle["metrics"]["cross_validation"]
    print(f"  Activité  — accuracy: {cv['classifier']['accuracy']['test_mean']} ± {cv['classifier']['accuracy']['test_std']}")
    print(f"  Activité  — f1_weighted: {cv['classifier']['f1_weighted']['test_mean']} ± {cv['classifier']['f1_weighted']['test_std']}")
    print(f"  Séries    — MAE: {cv['regressor']['mae']['test_mean']} ± {cv['regressor']['mae']['test_std']}")
    print(f"  Séries    — R²: {cv['regressor']['r2']['test_mean']} ± {cv['regressor']['r2']['test_std']}")


if __name__ == "__main__":
    main()
