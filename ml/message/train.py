"""Train the message scam model and the scam-type classifier.

Binary model: FeatureUnion(char 2-5, word 1-2 TF-IDF) -> LogisticRegression
(class_weight=balanced). C tuned on the val split by PR-AUC; the decision
threshold is the highest-F1 point on val with recall >= 0.90.
Run: python -m ml.message.train
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, precision_recall_curve
from sklearn.pipeline import Pipeline

from ml.message.features import build_features

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "processed" / "messages.csv"
ARTIFACTS = ROOT / "ml" / "artifacts"
C_GRID = (0.3, 1.0, 3.0, 10.0)
MIN_RECALL = 0.90


def pick_threshold(y: np.ndarray, prob: np.ndarray, min_recall: float) -> float:
    """Highest-F1 threshold subject to recall >= min_recall (falls back to best F1)."""
    precision, recall, thresholds = precision_recall_curve(y, prob)
    f1 = 2 * precision * recall / np.clip(precision + recall, 1e-9, None)
    f1, recall = f1[:-1], recall[:-1]
    ok = recall >= min_recall
    idx = int(np.argmax(np.where(ok, f1, -1))) if ok.any() else int(np.argmax(f1))
    return float(thresholds[idx])


def fit_binary(train: pd.DataFrame, val: pd.DataFrame) -> tuple[Pipeline, float, float]:
    best: tuple[float, float, Pipeline] | None = None
    for c in C_GRID:
        pipe = Pipeline([("features", build_features()),
                         ("clf", LogisticRegression(C=c, class_weight="balanced", max_iter=3000))])
        pipe.fit(train.text, train.label)
        ap = average_precision_score(val.label, pipe.predict_proba(val.text)[:, 1])
        print(f"  C={c:<5} val PR-AUC={ap:.4f}")
        if best is None or ap > best[0]:
            best = (ap, c, pipe)
    assert best is not None
    _, c, pipe = best
    threshold = pick_threshold(val.label.to_numpy(), pipe.predict_proba(val.text)[:, 1], MIN_RECALL)
    return pipe, c, threshold


def fit_type_classifier(pipe: Pipeline, train: pd.DataFrame) -> LogisticRegression:
    scams = train[train.label == 1]
    x = pipe.named_steps["features"].transform(scams.text)
    clf = LogisticRegression(C=3.0, max_iter=3000)
    clf.fit(x, scams.scam_type)
    return clf


def main() -> None:
    df = pd.read_csv(DATA, keep_default_na=False)
    train, val = df[df.split == "train"], df[df.split == "val"]
    print(f"train {len(train)} / val {len(val)}")
    pipe, c, threshold = fit_binary(train, val)
    type_clf = fit_type_classifier(pipe, train)
    data_hash = hashlib.sha256(DATA.read_bytes()).hexdigest()[:12]
    meta = {"threshold": round(threshold, 4), "C": c, "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "data_hash": data_hash, "min_recall": MIN_RECALL, "train_rows": len(train)}
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": pipe, "type_clf": type_clf, **meta}, ARTIFACTS / "message_model.joblib", compress=3)
    (ARTIFACTS / "message_meta.json").write_text(json.dumps(meta, indent=2))
    print(f"saved message_model.joblib (C={c}, threshold={threshold:.3f})")


if __name__ == "__main__":
    main()
