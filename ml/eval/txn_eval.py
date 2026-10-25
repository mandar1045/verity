"""Transaction evaluation on the chronological test window (days 46-60)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from backend.app.services.registry import load_registry
from backend.app.services.txn_analyzer import DemoFeed
from backend.app.services.txn_rules import inr
from ml.eval.plots import save_confusion
from ml.transaction.train import combined_risk, frame_features, load_frame, rule_scores

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "ml" / "artifacts"
REPORTS = ROOT / "ml" / "reports"
DEMO_FEED = ROOT / "data" / "processed" / "demo_feed.json"




def _metrics(y: np.ndarray, pred: np.ndarray, score: np.ndarray, n: int) -> dict[str, Any]:
    from ml.eval.evaluate import binary_metrics

    m = binary_metrics(y, pred.astype(int), score)
    fp = m["confusion"][0][1]
    return m | {"false_alarms_per_1000": round(fp / n * 1000, 2)}


def _recall_by_pattern(test: pd.DataFrame, pred: np.ndarray) -> list[dict[str, Any]]:
    rows = []
    frauds = test[test.is_fraud == 1]
    for pattern, idx in frauds.groupby("fraud_pattern").groups.items():
        pos = test.index.get_indexer(idx)
        rows.append({"group": str(pattern), "n": int(len(pos)), "value": round(float(pred[pos].mean()), 4)})
    return sorted(rows, key=lambda r: r["value"])


def demo_check() -> str:
    """Every fraud in the demo feed must be flagged (SUSPICIOUS or HIGH_RISK)."""
    raw = json.loads(DEMO_FEED.read_text(encoding="utf-8"))
    truth = {t["txn_id"]: t["is_fraud"] for t in raw["transactions"]}
    reg, feed = load_registry(), DemoFeed()
    flagged = total = 0
    missed = []
    for u in raw["users"]:
        for item in feed.feed(u["user_id"], "en", reg, 500):
            if truth[item.transaction.txn_id]:
                total += 1
                ok = item.analysis.label != "SAFE"
                flagged += ok
                if not ok:
                    missed.append(item.transaction.txn_id)
    summary = f"{flagged}/{total}"
    if missed:
        print(f"WARNING demo frauds not flagged: {missed}")
    return summary


def _describe(row: Any) -> str:
    new = "new payee" if row.payee_is_new else "known payee"
    return (f"{row.type} ₹{inr(row.amount_inr)} to {row.payee_name} ({new}, account {row.payee_account_age_days} days old, "
            f"{row.amount_vs_median:.1f}× usual) at {str(row.timestamp)[11:16]}")


def txn_failures(test: pd.DataFrame, risk: np.ndarray, codes: list[list[str]]) -> list[dict[str, Any]]:
    y = test.is_fraud.to_numpy()
    pred = (risk >= 35).astype(int)
    wrong = np.where(pred != y)[0]
    order = wrong[np.argsort(-np.abs(risk[wrong] / 100 - y[wrong]))][:6]
    out = []
    for i in order:
        row = test.iloc[i]
        if y[i]:
            why = f"Missed '{row.fraud_pattern}': it looked like normal spending for this account."
        else:
            why = f"Genuine payment with risky features ({', '.join(codes[i]) or 'model only'})."
        out.append({"kind": "transaction", "text": _describe(row), "true_label": int(y[i]), "predicted": int(pred[i]),
                    "score": int(risk[i]), "group": row.fraud_pattern or "legit", "why": why})
    return out


def evaluate_transactions() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    bundle = joblib.load(ARTIFACTS / "txn_model.joblib")
    df = load_frame()
    test = df[df.split == "test"].reset_index(drop=True)
    x, y, n = frame_features(test), test.is_fraud.to_numpy(), len(test)
    prob = bundle["model"].predict_proba(x)[:, 1]
    thr = float(bundle["threshold"])
    rules, codes = rule_scores(test)
    iso_score = -bundle["iforest"].score_samples(x)
    risk = combined_risk(prob, rules, thr, float(bundle["floor_min"]))
    models = [
        {"key": "rules", "name": "Rules only", **_metrics(y, rules * 100 >= 35, rules, n)},
        {"key": "iforest", "name": "Isolation Forest (unsupervised)", **_metrics(y, bundle["iforest"].predict(x) == -1, iso_score, n)},
        {"key": "gbm", "name": "Gradient boosting (GBM)", **_metrics(y, prob >= thr, prob, n)},
        {"key": "gbm_floors", "name": "Verity (GBM + rule floors)", **_metrics(y, risk >= 35, risk / 100, n)},
    ]
    for m in models:
        save_confusion(np.array(m["confusion"]), m["name"], REPORTS / f"confusion_txn_{m['key']}.png")
    report = {
        "test_size": n, "train_size": int((df.split == "train").sum()), "fraud_rate_test": round(float(y.mean()), 4),
        "threshold": round(thr, 4), "floor_min": float(bundle["floor_min"]), "explainer": "shap.TreeExplainer on HistGradientBoostingClassifier",
        "models": models, "recall_by_pattern": _recall_by_pattern(test, (risk >= 35).astype(int)),
        "demo_frauds_flagged": demo_check(),
    }
    return report, txn_failures(test, risk, codes)
