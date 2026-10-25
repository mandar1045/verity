"""Train the transaction fraud model (HistGradientBoosting) on days 1-45.

max_depth / learning_rate tuned on the last 7 training days (39-45) used as
validation; threshold = highest F1 with recall >= 0.85 on that window.
Run: python -m ml.transaction.train
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, IsolationForest
from sklearn.metrics import average_precision_score

from backend.app.services.scoring import calibrate
from backend.app.services.txn_rules import run_txn_rules, txn_rule_score
from contracts.schemas import Transaction
from ml.message.train import pick_threshold
from ml.transaction.features import FEATURES, TxnContext

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "processed" / "transactions.csv"
ARTIFACTS = ROOT / "ml" / "artifacts"
VAL_FROM_DAY = 39
MIN_RECALL = 0.85
GRID = [(d, lr) for d in (3, 5, 8) for lr in (0.05, 0.1, 0.2)]
FLOOR_GRID = (0.35, 0.45, 0.55, 0.6, 0.65, 0.7, 0.8, 0.9, 1.01)


def frame_features(df: pd.DataFrame) -> np.ndarray:
    """Vectorised equivalent of features.feature_vector over the generated CSV."""
    cols = {
        "amount_log": np.log1p(df.amount_inr),
        "amount_vs_median": df.amount_vs_median,
        "hour": df.hour,
        "is_night": df.is_night.astype(float),
        **{f"type_{t}": (df.type == t).astype(float) for t in ("PAY", "COLLECT_REQUEST", "RECEIVE")},
        **{f"channel_{c}": (df.channel == c).astype(float) for c in ("QR", "VPA", "PHONE")},
        "payee_is_new": df.payee_is_new.astype(float),
        "payee_account_age_days": df.payee_account_age_days,
        "payee_report_count": df.payee_report_count,
        "device_changed": df.device_changed.astype(float),
        "txns_last_10m": df.txns_last_10m,
        "inbound_count_24h": df.inbound_count_24h,
        "received_then_sent_ratio_24h": df.received_then_sent_ratio_24h,
    }
    return np.column_stack([np.asarray(cols[f], dtype=float) for f in FEATURES])


def load_frame() -> pd.DataFrame:
    df = pd.read_csv(DATA, keep_default_na=False)
    for col in ("is_night", "payee_is_new", "device_changed"):
        df[col] = df[col].astype(str).str.lower().eq("true")
    return df


def row_context(row: object) -> TxnContext:
    return TxnContext(
        amount_vs_median=float(row.amount_vs_median), txns_last_10m=int(row.txns_last_10m), hour=int(row.hour),
        is_night=bool(row.is_night), inbound_count_24h=int(row.inbound_count_24h),
        received_then_sent_ratio_24h=float(row.received_then_sent_ratio_24h),
    )


def rule_scores(df: pd.DataFrame) -> tuple[np.ndarray, list[list[str]]]:
    """Backend rule score and fired codes for every generated transaction."""
    scores, codes = [], []
    for row in df.itertuples(index=False):
        hits = run_txn_rules(Transaction.model_validate(row._asdict()), row_context(row))
        scores.append(txn_rule_score(hits))
        codes.append([h.signal.code for h in hits])
    return np.array(scores), codes


def combined_risk(prob: np.ndarray, rules: np.ndarray, threshold: float, floor_min: float) -> np.ndarray:
    """risk = max(calibrated model score, rule score when the rules are strong enough to act as a floor)."""
    model = np.array([calibrate(p, threshold) for p in prob])
    floor = np.where(rules >= floor_min, np.round(rules * 100), 0)
    return np.maximum(model, floor)


def tune_floor(prob: np.ndarray, rules: np.ndarray, y: np.ndarray, threshold: float) -> float:
    """Weakest rule score allowed to override the model: best F1 on the validation window."""
    from sklearn.metrics import f1_score

    scored = [(f1_score(y, combined_risk(prob, rules, threshold, m) >= 35), -m) for m in FLOOR_GRID]
    best_f1, neg_m = max(scored)
    print(f"  rule floor applies from rule score >= {-neg_m} (val F1 {best_f1:.4f})")
    return -neg_m


def tune(x_fit: np.ndarray, y_fit: np.ndarray, x_val: np.ndarray, y_val: np.ndarray) -> tuple[int, float]:
    best = (-1.0, 3, 0.1)
    for depth, lr in GRID:
        m = HistGradientBoostingClassifier(max_depth=depth, learning_rate=lr, max_iter=300, random_state=0)
        m.fit(x_fit, y_fit)
        ap = average_precision_score(y_val, m.predict_proba(x_val)[:, 1])
        if ap > best[0]:
            best = (ap, depth, lr)
    print(f"  best max_depth={best[1]} learning_rate={best[2]} val PR-AUC={best[0]:.4f}")
    return best[1], best[2]


def main() -> None:
    df = load_frame()
    train = df[df.split == "train"]
    fit, val = train[train.day < VAL_FROM_DAY], train[train.day >= VAL_FROM_DAY]
    x_fit, x_val = frame_features(fit), frame_features(val)
    depth, lr = tune(x_fit, fit.is_fraud.to_numpy(), x_val, val.is_fraud.to_numpy())
    probe = HistGradientBoostingClassifier(max_depth=depth, learning_rate=lr, max_iter=300, random_state=0)
    probe.fit(x_fit, fit.is_fraud)
    val_prob = probe.predict_proba(x_val)[:, 1]
    threshold = pick_threshold(val.is_fraud.to_numpy(), val_prob, MIN_RECALL)
    floor_min = tune_floor(val_prob, rule_scores(val)[0], val.is_fraud.to_numpy(), threshold)
    model = HistGradientBoostingClassifier(max_depth=depth, learning_rate=lr, max_iter=300, random_state=0)
    x_train = frame_features(train)
    model.fit(x_train, train.is_fraud)
    iforest = IsolationForest(contamination=0.03, random_state=0).fit(x_train)
    background = x_train[np.random.default_rng(0).choice(len(x_train), size=200, replace=False)]
    meta = {"threshold": round(threshold, 4), "floor_min": floor_min, "max_depth": depth, "learning_rate": lr, "features": list(FEATURES),
            "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "train_rows": len(train)}
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "iforest": iforest, "background": background, **meta}, ARTIFACTS / "txn_model.joblib", compress=3)
    (ARTIFACTS / "txn_meta.json").write_text(json.dumps(meta, indent=2))
    print(f"saved txn_model.joblib (threshold={threshold:.3f})")


if __name__ == "__main__":
    main()
