"""Evaluate everything on held-out data and write ml/reports/.

Messages (test split = template families never seen in training):
  keyword baseline vs rules-only vs model-only vs Verity fused (w tuned on val)
Transactions (days 46-60):
  rules-only vs Isolation Forest vs GBM vs GBM + rule floors
Outputs: metrics.json (validated against schema.json), fusion.json,
confusion_*.png, failures.csv. Run: python -m ml.eval.evaluate
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, confusion_matrix, f1_score, precision_score, recall_score

from backend.app.services.links import inspect_links
from backend.app.services.rules import RULE_CODES, RuleContext, rule_score, run_rules
from backend.app.services.scoring import FLOOR_SCORE, MODEL_ONLY_CAP, calibrate, has_floor
from ml.eval.plots import save_confusion
from ml.eval.txn_eval import evaluate_transactions
from ml.message.predict import MessageModel

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"
REPORTS = ROOT / "ml" / "reports"
ARTIFACTS = ROOT / "ml" / "artifacts"
MIN_RECALL = 0.90
KEYWORDS = ("otp", "kyc", "blocked", "suspended", "lottery", "prize", "won", "refund", "urgent", "verify",
            "anydesk", "pin", "winner", "cashback", "click", "link", "reward", "fee", "customer care", "lucky")
UCI_NOTE = ("Out-of-domain check only: UCI is 2010-era UK promotional spam, not UPI fraud. "
            "Verity is specialised for UPI scams, so lower recall here is expected.")


def binary_metrics(y: np.ndarray, pred: np.ndarray, score: np.ndarray | None = None) -> dict[str, Any]:
    cm = confusion_matrix(y, pred, labels=[0, 1])
    return {
        "precision": round(float(precision_score(y, pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y, pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y, pred, zero_division=0)), 4),
        "pr_auc": round(float(average_precision_score(y, score)), 4) if score is not None else None,
        "confusion": cm.astype(int).tolist(),
    }


def rule_features(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, list[list[str]]]:
    """Rule score, hard-floor flag and fired codes for every message."""
    scores, floors, codes = [], [], []
    for text, channel, sender in zip(df.text, df.channel, df.sender):
        links = inspect_links(text)
        signals = run_rules(RuleContext(text, channel or "sms", sender or None, links))
        scores.append(rule_score(signals))
        floors.append(has_floor(signals, [lk.finding for lk in links]))
        codes.append([s.code for s in signals if s.code in RULE_CODES])
    return np.array(scores), np.array(floors), codes


RULE_FLOOR_GRID = (0.6, 0.65, 0.7, 0.75, 0.8, 0.9, 1.01)


def verity_scores(p: np.ndarray, r: np.ndarray, floor: np.ndarray, w: float, t: float, m: float = 1.01) -> np.ndarray:
    """Same arithmetic as backend scoring.score_message, vectorised."""
    raw = w * p + (1 - w) * r
    scores = np.array([calibrate(x, t) for x in raw])
    scores = np.where(r >= m, np.maximum(scores, np.round(r * 100)), scores)
    scores = np.where((r == 0) & ~floor, np.minimum(scores, MODEL_ONLY_CAP), scores)
    return np.where(floor, np.maximum(scores, FLOOR_SCORE), scores)


def tune_rule_floor(p: np.ndarray, r: np.ndarray, floor: np.ndarray, y: np.ndarray, w: float, t: float) -> float:
    """Weakest rule score that may override the fused score: best val F1, ties -> stricter."""
    scored = [(f1_score(y, verity_scores(p, r, floor, w, t, m) >= 35), m) for m in RULE_FLOOR_GRID]
    best = max(f for f, _ in scored)
    return max(m for f, m in scored if f >= best - 1e-9)


def tune_fusion(p: np.ndarray, r: np.ndarray, floor: np.ndarray, y: np.ndarray, weights: np.ndarray) -> tuple[float, float, float]:
    """Pick (w, t) on val: best F1 with recall >= 0.90 (else best F1)."""
    best: tuple[bool, float, float, float] = (False, -1.0, 0.0, 0.5)
    for w in weights:
        raw = w * p + (1 - w) * r
        for t in np.linspace(0.05, 0.95, 91):
            pred = (raw >= t) | floor
            rec = recall_score(y, pred, zero_division=0)
            f1 = f1_score(y, pred, zero_division=0)
            cand = (rec >= MIN_RECALL, f1, float(w), float(t))
            if cand[:2] > best[:2]:
                best = cand
    return best[2], best[3], best[1]


def breakdown(df: pd.DataFrame, pred: np.ndarray, by: str, kind: str) -> list[dict[str, Any]]:
    rows = []
    for group, idx in df.groupby(by).groups.items():
        if not group:
            continue
        pos = df.index.get_indexer(idx)
        y, yhat = df.label.to_numpy()[pos], pred[pos]
        value = recall_score(y, yhat, zero_division=0) if kind == "recall" else (
            f1_score(y, yhat, zero_division=0) if kind == "f1" else float(yhat.mean()))
        rows.append({"group": str(group), "n": int(len(pos)), "value": round(float(value), 4)})
    return sorted(rows, key=lambda r: r["value"])


def why_failed(true: int, codes: list[str], top: str | None) -> str:
    if true == 1 and not codes:
        return "No rule fired and the wording comes from a template family the model never saw."
    if true == 1:
        return f"Rules saw {', '.join(codes)} but the combined score stayed under the SUSPICIOUS cut-off."
    if codes:
        return f"A genuine message that uses scam-like wording ({', '.join(codes)})."
    return f"The model over-weighted wording shared with scams{f' (“{top}”)' if top else ''}."


def message_failures(test: pd.DataFrame, scores: np.ndarray, codes: list[list[str]], model: MessageModel) -> list[dict[str, Any]]:
    y = test.label.to_numpy()
    pred = (scores >= 35).astype(int)
    wrong = np.where(pred != y)[0]
    order = wrong[np.argsort(-np.abs(scores[wrong] / 100 - y[wrong]))][:15]
    out = []
    for i in order:
        text = test.text.iloc[i]
        top = model.predict(text)["top_ngrams"]
        out.append({"kind": "message", "text": text, "true_label": int(y[i]), "predicted": int(pred[i]),
                    "score": int(scores[i]), "group": test.scam_type.iloc[i] or test.legit_class.iloc[i],
                    "why": why_failed(int(y[i]), codes[i], top[0]["ngram"] if top else None)})
    return out


def evaluate_messages(model: MessageModel) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, float]]:
    df = pd.read_csv(PROCESSED / "messages.csv", keep_default_na=False)
    val, test = df[df.split == "val"].reset_index(drop=True), df[df.split == "test"].reset_index(drop=True)
    p_val, p_test = model.predict_proba(list(val.text)), model.predict_proba(list(test.text))
    r_val, f_val, _ = rule_features(val)
    r_test, f_test, codes = rule_features(test)
    w, t, _ = tune_fusion(p_val, r_val, f_val, val.label.to_numpy(), np.linspace(0, 1, 21))
    _, t_rules, _ = tune_fusion(p_val, r_val, f_val, val.label.to_numpy(), np.array([0.0]))
    m = tune_rule_floor(p_val, r_val, f_val, val.label.to_numpy(), w, t)
    fusion = {"weight": round(w, 3), "threshold": round(t, 3), "rules_threshold": round(t_rules, 3), "rule_floor_min": m}
    y = test.label.to_numpy()
    s_fused = verity_scores(p_test, r_test, f_test, w, t, m)
    s_rules = verity_scores(np.zeros_like(r_test), r_test, f_test, 0.0, t_rules)
    kw = np.array([sum(k in x.lower() for k in KEYWORDS) for x in test.text])
    models = [
        {"key": "keyword", "name": "Keyword baseline (20 words)", **binary_metrics(y, (kw > 0).astype(int), kw)},
        {"key": "rules", "name": "Rules only", **binary_metrics(y, (s_rules >= 35).astype(int), s_rules / 100)},
        {"key": "model", "name": "TF-IDF + LR model only", **binary_metrics(y, (p_test >= model.threshold).astype(int), p_test)},
        {"key": "fused", "name": "Verity (model + rules + floors)", **binary_metrics(y, (s_fused >= 35).astype(int), s_fused / 100)},
    ]
    pred = (s_fused >= 35).astype(int)
    legit = test[test.label == 0]
    type_acc = _type_accuracy(model, test[test.label == 1])
    report = {
        "test_size": int(len(test)), "train_size": int((df.split == "train").sum()),
        "n_templates_test": int(test.template_group.nunique()), "threshold": round(model.threshold, 4),
        "fusion_weight": fusion["weight"], "rule_floor_min": m, "models": models,
        "recall_by_scam_type": breakdown(test, pred, "scam_type", "recall"),
        "f1_by_language": breakdown(test, pred, "language", "f1"),
        "fpr_by_legit_class": breakdown(legit.reset_index(drop=True), pred[legit.index], "legit_class", "rate"),
        "hard_negative_fpr": round(float(pred[legit.index].mean()), 4),
        "scam_type_accuracy": type_acc,
        "external_uci": _uci(model, w, t, m),
    }
    for row in models:
        save_confusion(np.array(row["confusion"]), row["name"], REPORTS / f"confusion_message_{row['key']}.png")
    return report, message_failures(test, s_fused, codes, model), fusion


def _type_accuracy(model: MessageModel, scams: pd.DataFrame) -> float:
    hits = sum(model.scam_type(x)[0] == y for x, y in zip(scams.text, scams.scam_type))
    return round(hits / max(1, len(scams)), 4)


def _uci(model: MessageModel, w: float, t: float, m: float) -> dict[str, Any]:
    uci = pd.read_csv(PROCESSED / "uci_external.csv", keep_default_na=False)
    p = model.predict_proba(list(uci.text))
    r, f, _ = rule_features(uci)
    s = verity_scores(p, r, f, w, t, m)
    res = binary_metrics(uci.label.to_numpy(), (s >= 35).astype(int), s / 100)
    return {k: res[k] for k in ("precision", "recall", "f1", "pr_auc")} | {"n": int(len(uci)), "note": UCI_NOTE}


def write_failures(rows: list[dict[str, Any]]) -> None:
    with (REPORTS / "failures.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["kind", "text", "true_label", "predicted", "score", "group", "why"])
        w.writeheader()
        w.writerows(rows)


def validate(metrics: dict[str, Any]) -> None:
    import jsonschema

    schema = json.loads((REPORTS / "schema.json").read_text())
    jsonschema.validate(metrics, schema)


def print_table(metrics: dict[str, Any]) -> None:
    print("\n| Messages (unseen templates) | Precision | Recall | F1 | PR-AUC |\n|---|---|---|---|---|")
    for m in metrics["message"]["models"]:
        print(f"| {m['name']} | {m['precision']:.3f} | {m['recall']:.3f} | {m['f1']:.3f} | {m['pr_auc']:.3f} |")
    if metrics["transaction"]:
        print("\n| Transactions (days 46-60) | Precision | Recall | F1 | PR-AUC | False alarms /1k |\n|---|---|---|---|---|---|")
        for m in metrics["transaction"]["models"]:
            print(f"| {m['name']} | {m['precision']:.3f} | {m['recall']:.3f} | {m['f1']:.3f} | {m['pr_auc']:.3f} | {m['false_alarms_per_1000']:.1f} |")


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    model = MessageModel(ARTIFACTS / "message_model.joblib")
    msg, failures, fusion = evaluate_messages(model)
    (REPORTS / "fusion.json").write_text(json.dumps(fusion, indent=2))
    txn, txn_failures = evaluate_transactions() if (ARTIFACTS / "txn_model.joblib").exists() else (None, [])
    metrics = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "data_hash": hashlib.sha256((PROCESSED / "messages.csv").read_bytes()).hexdigest()[:12],
        "message": msg, "transaction": txn, "failures": failures + txn_failures,
    }
    validate(metrics)
    (REPORTS / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False))
    write_failures(metrics["failures"])
    print(f"fusion: {fusion}")
    print_table(metrics)
    if txn:
        print(f"\ndemo frauds flagged: {txn['demo_frauds_flagged']}")


if __name__ == "__main__":
    main()
