"""Message model inference: probability, top contributing n-grams, scam type."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np

DEFAULT_PATH = Path(__file__).resolve().parents[2] / "ml" / "artifacts" / "message_model.joblib"


@dataclass(frozen=True)
class NgramWeight:
    ngram: str
    weight: float


class MessageModel:
    def __init__(self, path: Path = DEFAULT_PATH) -> None:
        bundle: dict[str, Any] = joblib.load(path)
        pipe = bundle["pipeline"]
        self.features = pipe.named_steps["features"]
        self.clf = pipe.named_steps["clf"]
        self.type_clf = bundle["type_clf"]
        self.threshold: float = float(bundle["threshold"])
        self.meta = {k: v for k, v in bundle.items() if k not in ("pipeline", "type_clf")}
        self._names = np.array([n.split("__", 1)[1] for n in self.features.get_feature_names_out()])
        self._kinds = np.array([n.split("__", 1)[0] for n in self.features.get_feature_names_out()])
        self._coef = self.clf.coef_[0]

    def predict(self, text: str, top_k: int = 5) -> dict[str, Any]:
        """{prob, top_ngrams: [{ngram, weight}]}: top_k features by coef x tfidf."""
        x = self.features.transform([text])
        prob = float(self.clf.predict_proba(x)[0, 1])
        row = x.tocsr()
        contrib = row.data * self._coef[row.indices]
        order = np.argsort(-contrib)
        top: list[NgramWeight] = []
        for i in order:
            if contrib[i] <= 0 or len(top) == top_k:
                break
            idx = row.indices[i]
            gram = self._names[idx].strip()
            if self._kinds[idx] == "char" and len(gram) < 3:
                continue
            top.append(NgramWeight(gram, round(float(contrib[i]), 4)))
        return {"prob": prob, "top_ngrams": [t.__dict__ for t in top]}

    def predict_proba(self, texts: list[str]) -> np.ndarray:
        return self.clf.predict_proba(self.features.transform(texts))[:, 1]

    def scam_type(self, text: str) -> tuple[str, float]:
        probs = self.type_clf.predict_proba(self.features.transform([text]))[0]
        i = int(np.argmax(probs))
        return str(self.type_clf.classes_[i]), float(probs[i])


def load(path: Path = DEFAULT_PATH) -> MessageModel | None:
    return MessageModel(path) if path.exists() else None
