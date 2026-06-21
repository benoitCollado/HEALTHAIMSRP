import json
import os

import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestClassifier

from ml.data_prep import prepare_matrices
from ml.evaluation import cross_validate_classifier, evaluate_classifier, evaluate_regressor
from ml.generate_training_data import generate_dataset


@pytest.fixture
def sample_frame() -> pd.DataFrame:
    return generate_dataset().head(300)


def test_prepare_matrices_shape(sample_frame):
    x, y_class, y_reg, groups, meta = prepare_matrices(sample_frame)
    assert len(x) == len(sample_frame)
    assert len(y_class) == len(sample_frame)
    assert len(groups) == len(sample_frame)
    assert len(meta["feature_columns"]) == 12


def test_evaluate_classifier_returns_core_metrics():
    y_true = np.array([0, 0, 1, 1, 2, 2])
    y_pred = np.array([0, 1, 1, 1, 2, 0])
    labels = ["a", "b", "c"]
    metrics = evaluate_classifier(y_true, y_pred, class_labels=labels)
    assert "accuracy" in metrics
    assert "f1_weighted" in metrics
    assert "confusion_matrix" in metrics
    assert "confusion_matrix_table" in metrics
    assert len(metrics["per_class_metrics"]) == 3
    assert metrics["classes"] == labels
    assert 0 <= metrics["accuracy"] <= 1


def test_evaluate_regressor_returns_core_metrics():
    y_true = np.array([3.0, 4.0, 5.0, 4.0])
    y_pred = np.array([3.0, 4.5, 4.8, 4.0])
    metrics = evaluate_regressor(y_true, y_pred)
    assert metrics["mae"] >= 0
    assert metrics["rmse"] >= metrics["mae"]
    assert "r2" in metrics


def test_cross_validate_classifier_runs(sample_frame):
    x, y_class, _, groups, _ = prepare_matrices(sample_frame)
    model = RandomForestClassifier(n_estimators=20, max_depth=6, random_state=42, n_jobs=1)
    cv = cross_validate_classifier(model, x, y_class, groups, cv_folds=3)
    assert "accuracy" in cv
    assert len(cv["accuracy"]["fold_test_scores"]) == 3


def test_train_exports_report(tmp_path, monkeypatch):
    monkeypatch.setenv("ML_FAST_TRAIN", "1")
    monkeypatch.setenv("ML_CV_FOLDS", "3")
    from ml import train_random_forest as train_module

    monkeypatch.setattr(train_module, "MODELS_DIR", tmp_path)
    monkeypatch.setattr(train_module, "BUNDLE_PATH", tmp_path / "workout_rf_bundle.pkl")
    monkeypatch.setattr(train_module, "REPORT_PATH", tmp_path / "training_report.json")

    bundle = train_module.train()
    train_module.save_report(bundle)

    report = json.loads((tmp_path / "training_report.json").read_text(encoding="utf-8"))
    assert "best_params" in report
    assert "output_classes" in report
    assert "tables" in report["metrics"]
    assert "confusion_matrix" in report["metrics"]["tables"]["test_holdout"]
    assert "classifier" in report["best_params"]
    assert "regressor" in report["best_params"]
    assert report["metrics"]["cross_validation"]["classifier"]["f1_weighted"]["test_mean"] > 0
