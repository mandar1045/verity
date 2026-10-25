"""Score fusion: model probability + rule score -> calibrated 0..100 risk score.

fused = w * model_prob + (1 - w) * rule_score, with w and the decision
threshold t tuned on the validation split (ml/reports/fusion.json). The raw
fused value is mapped piecewise-linearly so that t lands exactly on 35, the
contract's SUSPICIOUS cut-off. Then two floors: strong rule evidence (rule
score >= rule_floor_min, also tuned on val) sets the score to at least
100 x rule score, and a DANGEROUS link or PIN-to-receive forces >= 75.
Evidence gate: when no rule fired at all, the model alone can reach
SUSPICIOUS but never HIGH_RISK, so every HIGH_RISK verdict has a reason the
user can read. (This never changes flagged vs not flagged: that cut is 35.)
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from contracts.schemas import THRESHOLD_SUSPICIOUS, LinkFinding, Signal

FLOOR_SCORE = 75
MODEL_ONLY_CAP = 69  # HIGH_RISK needs at least one explainable rule signal
DEFAULT_WEIGHT = 0.55
DEFAULT_THRESHOLD = 0.5
RULES_ONLY_THRESHOLD = 0.35
NO_RULE_FLOOR = 1.01


@dataclass(frozen=True)
class FusionConfig:
    weight: float = DEFAULT_WEIGHT
    threshold: float = DEFAULT_THRESHOLD
    rules_threshold: float = RULES_ONLY_THRESHOLD
    rule_floor_min: float = NO_RULE_FLOOR  # strong rule evidence alone can set the score


def load_fusion(path: Path) -> FusionConfig:
    if not path.exists():
        return FusionConfig()
    data = json.loads(path.read_text())
    return FusionConfig(
        weight=float(data.get("weight", DEFAULT_WEIGHT)),
        threshold=float(data.get("threshold", DEFAULT_THRESHOLD)),
        rules_threshold=float(data.get("rules_threshold", RULES_ONLY_THRESHOLD)),
        rule_floor_min=float(data.get("rule_floor_min", NO_RULE_FLOOR)),
    )


def calibrate(raw: float, threshold: float) -> int:
    """Map raw [0,1] to [0,100] so that `threshold` maps to 35."""
    raw = min(1.0, max(0.0, raw))
    t = min(0.95, max(0.05, threshold))
    if raw < t:
        score = THRESHOLD_SUSPICIOUS * raw / t
    else:
        score = THRESHOLD_SUSPICIOUS + (100 - THRESHOLD_SUSPICIOUS) * (raw - t) / (1 - t)
    return int(round(min(100.0, max(0.0, score))))


def has_floor(signals: list[Signal], links: list[LinkFinding]) -> bool:
    """A DANGEROUS link or a PIN-to-receive request is always high risk."""
    return any(s.code == "PIN_TO_RECEIVE" for s in signals) or any(lk.verdict == "DANGEROUS" for lk in links)


def fuse(model_prob: float | None, rule_score: float, cfg: FusionConfig) -> tuple[float, float]:
    """Return (raw fused value, threshold used). Rules-only when there is no model."""
    if model_prob is None:
        return rule_score, cfg.rules_threshold
    return cfg.weight * model_prob + (1 - cfg.weight) * rule_score, cfg.threshold


def score_message(
    model_prob: float | None,
    rule_score: float,
    signals: list[Signal],
    links: list[LinkFinding],
    cfg: FusionConfig,
) -> int:
    raw, threshold = fuse(model_prob, rule_score, cfg)
    score = calibrate(raw, threshold)
    if model_prob is not None and rule_score >= cfg.rule_floor_min:
        score = max(score, int(round(100 * rule_score)))
    floor = has_floor(signals, links)
    if rule_score == 0 and not floor:
        score = min(score, MODEL_ONLY_CAP)
    if floor:
        score = max(score, FLOOR_SCORE)
    return score
