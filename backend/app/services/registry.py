"""Loads models once at startup. Missing files mean rules-only fallback."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

from backend.app.services.scoring import FusionConfig, load_fusion
from ml.message.predict import MessageModel
from ml.transaction.predict import TxnModel

log = logging.getLogger(__name__)
ROOT = Path(os.environ.get("VERITY_ROOT", Path(__file__).resolve().parents[3]))
ARTIFACTS = ROOT / "ml" / "artifacts"
REPORTS = ROOT / "ml" / "reports"
DEMO_FEED = ROOT / "data" / "processed" / "demo_feed.json"


@dataclass
class Registry:
    message_model: MessageModel | None
    txn_model: TxnModel | None
    fusion: FusionConfig

    @property
    def models_loaded(self) -> bool:
        return self.message_model is not None and self.txn_model is not None


def _try_load(cls: type, path: Path) -> object | None:
    if not path.exists():
        log.warning("model file missing, falling back to rules: %s", path)
        return None
    try:
        return cls(path)
    except Exception:  # noqa: BLE001 - a corrupt artifact must not take the API down
        log.exception("could not load %s", path)
        return None


def load_registry(artifacts: Path = ARTIFACTS, reports: Path = REPORTS) -> Registry:
    message = _try_load(MessageModel, artifacts / "message_model.joblib")
    txn = _try_load(TxnModel, artifacts / "txn_model.joblib")
    return Registry(message_model=message, txn_model=txn, fusion=load_fusion(reports / "fusion.json"))  # type: ignore[arg-type]
