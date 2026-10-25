"""Transaction model inference with per-feature SHAP contributions.

SHAP TreeExplainer runs on the HistGradientBoosting model (log-odds units).
If SHAP is unavailable, contributions fall back to an occlusion estimate
against a background sample, and `explainer` says so.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from ml.transaction.features import FEATURES, TxnContext, feature_vector

DEFAULT_PATH = Path(__file__).resolve().parents[2] / "ml" / "artifacts" / "txn_model.joblib"
# One-hot columns are reported as one plain-language reason.
GROUPS = {"type_PAY": "type", "type_COLLECT_REQUEST": "type", "type_RECEIVE": "type",
          "channel_QR": "channel", "channel_VPA": "channel", "channel_PHONE": "channel"}


class TxnModel:
    def __init__(self, path: Path = DEFAULT_PATH) -> None:
        bundle: dict[str, Any] = joblib.load(path)
        self.model = bundle["model"]
        self.iforest = bundle.get("iforest")
        self.background: np.ndarray = bundle["background"]
        self.threshold: float = float(bundle["threshold"])
        self.floor_min: float = float(bundle.get("floor_min", 0.35))
        self.explainer_name = "shap.TreeExplainer"
        try:
            import shap

            self._shap = shap.TreeExplainer(self.model)
        except Exception:  # noqa: BLE001 - any SHAP failure falls back to occlusion
            self._shap = None
            self.explainer_name = "occlusion (SHAP unavailable)"

    def _contributions(self, x: np.ndarray) -> np.ndarray:
        if self._shap is not None:
            values = self._shap.shap_values(x)
            values = values[1] if isinstance(values, list) else values
            return np.asarray(values)[0]
        base = self._logit(x)[0]
        out = np.zeros(x.shape[1])
        for j in range(x.shape[1]):
            probe = np.repeat(x, len(self.background), axis=0)
            probe[:, j] = self.background[:, j]
            out[j] = base - float(np.mean(self._logit(probe)))
        return out

    def _logit(self, x: np.ndarray) -> np.ndarray:
        p = np.clip(self.model.predict_proba(x)[:, 1], 1e-6, 1 - 1e-6)
        return np.log(p / (1 - p))

    def predict(self, txn: Mapping[str, Any], ctx: TxnContext, top_k: int = 5) -> tuple[float, list[tuple[str, float]]]:
        """(probability, [(feature group, contribution)]) sorted by |contribution|."""
        x = np.array([feature_vector(txn, ctx)])
        prob = float(self.model.predict_proba(x)[0, 1])
        grouped: dict[str, float] = {}
        for name, value in zip(FEATURES, self._contributions(x)):
            key = GROUPS.get(name, name)
            grouped[key] = grouped.get(key, 0.0) + float(value)
        ranked = sorted(grouped.items(), key=lambda kv: abs(kv[1]), reverse=True)[:top_k]
        return prob, [(k, round(v, 4)) for k, v in ranked]


def load(path: Path = DEFAULT_PATH) -> TxnModel | None:
    return TxnModel(path) if path.exists() else None
