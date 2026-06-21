"""Métriques et validation croisée pour les modèles activité / séries."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    precision_score,
    r2_score,
    recall_score,
    root_mean_squared_error,
)
from sklearn.model_selection import GroupKFold, cross_validate


def _round(value: float, digits: int = 4) -> float:
    return round(float(value), digits)


def evaluate_classifier(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_labels: list[str] | None = None,
) -> dict[str, Any]:
    labels = class_labels or [str(i) for i in sorted(set(y_true) | set(y_pred))]
    report_kwargs: dict[str, Any] = {"output_dict": True, "zero_division": 0}
    if class_labels:
        report_kwargs["labels"] = list(range(len(class_labels)))
        report_kwargs["target_names"] = class_labels
    report = classification_report(y_true, y_pred, **report_kwargs)
    matrix = confusion_matrix(y_true, y_pred)

    per_class_metrics = []
    for label in labels:
        if label not in report:
            continue
        row = report[label]
        per_class_metrics.append(
            {
                "class": label,
                "precision": _round(row["precision"]),
                "recall": _round(row["recall"]),
                "f1_score": _round(row["f1-score"]),
                "support": int(row["support"]),
            }
        )

    global_metrics = {
        "accuracy": _round(accuracy_score(y_true, y_pred)),
        "precision_weighted": _round(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
        "recall_weighted": _round(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
        "f1_weighted": _round(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        "f1_macro": _round(f1_score(y_true, y_pred, average="macro", zero_division=0)),
    }

    return {
        **global_metrics,
        "classes": labels,
        "per_class_metrics": per_class_metrics,
        "classification_report": report,
        "confusion_matrix": matrix.tolist(),
        "confusion_matrix_table": {
            "row_axis": "classe_reelle",
            "column_axis": "classe_predite",
            "labels": labels,
            "matrix": matrix.tolist(),
        },
        "activity_labels": labels,
    }


def evaluate_regressor(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    return {
        "mae": _round(mean_absolute_error(y_true, y_pred)),
        "rmse": _round(root_mean_squared_error(y_true, y_pred)),
        "r2": _round(r2_score(y_true, y_pred)),
        "mape": _round(float(np.mean(np.abs((y_true - y_pred) / np.clip(y_true, 1e-6, None))) * 100)),
    }


def cross_validate_classifier(
    estimator: RandomForestClassifier,
    x: pd.DataFrame,
    y: np.ndarray,
    groups: np.ndarray,
    cv_folds: int = 5,
) -> dict[str, Any]:
    splitter = GroupKFold(n_splits=cv_folds)
    scoring = {
        "accuracy": "accuracy",
        "f1_weighted": "f1_weighted",
        "precision_weighted": "precision_weighted",
        "recall_weighted": "recall_weighted",
    }
    results = cross_validate(
        estimator,
        x,
        y,
        cv=splitter,
        groups=groups,
        scoring=scoring,
        n_jobs=-1,
        return_train_score=True,
    )
    return _summarize_cv_results(results, scoring.keys())


def cross_validate_regressor(
    estimator: RandomForestRegressor,
    x: pd.DataFrame,
    y: np.ndarray,
    groups: np.ndarray,
    cv_folds: int = 5,
) -> dict[str, Any]:
    splitter = GroupKFold(n_splits=cv_folds)
    scoring = {
        "mae": "neg_mean_absolute_error",
        "rmse": "neg_root_mean_squared_error",
        "r2": "r2",
    }
    results = cross_validate(
        estimator,
        x,
        y,
        cv=splitter,
        groups=groups,
        scoring=scoring,
        n_jobs=-1,
        return_train_score=True,
    )
    summary = _summarize_cv_results(results, scoring.keys(), negate={"mae", "rmse"})
    return summary


def _summarize_cv_results(
    results: dict[str, np.ndarray],
    metric_names,
    negate: set[str] | None = None,
) -> dict[str, Any]:
    negate = negate or set()
    summary: dict[str, Any] = {}
    for name in metric_names:
        test_key = f"test_{name}"
        train_key = f"train_{name}"
        test_values = results[test_key]
        train_values = results[train_key]
        if name in negate:
            test_values = -test_values
            train_values = -train_values
        summary[name] = {
            "test_mean": _round(float(np.mean(test_values))),
            "test_std": _round(float(np.std(test_values))),
            "train_mean": _round(float(np.mean(train_values))),
            "fold_test_scores": [_round(v) for v in test_values.tolist()],
        }
    return summary


def build_metrics_summary(
    test_classifier: dict[str, Any],
    test_regressor: dict[str, float],
    cv_classifier: dict[str, Any],
    cv_regressor: dict[str, Any],
) -> dict[str, Any]:
    """Tableaux synthétiques pour le rapport JSON / documentation."""
    return {
        "test_holdout": {
            "classification_global": [
                {"metrique": "accuracy", "valeur": test_classifier["accuracy"]},
                {"metrique": "precision_weighted", "valeur": test_classifier["precision_weighted"]},
                {"metrique": "recall_weighted", "valeur": test_classifier["recall_weighted"]},
                {"metrique": "f1_weighted", "valeur": test_classifier["f1_weighted"]},
                {"metrique": "f1_macro", "valeur": test_classifier["f1_macro"]},
            ],
            "classification_par_classe": test_classifier["per_class_metrics"],
            "confusion_matrix": test_classifier["confusion_matrix_table"],
            "regression": [
                {"metrique": "mae", "valeur": test_regressor["mae"]},
                {"metrique": "rmse", "valeur": test_regressor["rmse"]},
                {"metrique": "r2", "valeur": test_regressor["r2"]},
                {"metrique": "mape", "valeur": test_regressor["mape"]},
            ],
        },
        "cross_validation": {
            "classification": [
                {
                    "metrique": name,
                    "test_mean": values["test_mean"],
                    "test_std": values["test_std"],
                    "train_mean": values["train_mean"],
                    "fold_test_scores": values["fold_test_scores"],
                }
                for name, values in cv_classifier.items()
            ],
            "regression": [
                {
                    "metrique": name,
                    "test_mean": values["test_mean"],
                    "test_std": values["test_std"],
                    "train_mean": values["train_mean"],
                    "fold_test_scores": values["fold_test_scores"],
                }
                for name, values in cv_regressor.items()
            ],
        },
    }


def format_search_results(search) -> dict[str, Any]:
    return {
        "best_params": search.best_params_,
        "best_score": _round(float(search.best_score_)),
        "cv_results": {
            "mean_test_score": [_round(v) for v in search.cv_results_["mean_test_score"].tolist()],
            "std_test_score": [_round(v) for v in search.cv_results_["std_test_score"].tolist()],
            "params": search.cv_results_["params"],
        },
    }
