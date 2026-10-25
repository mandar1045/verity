"""Confusion-matrix PNGs in the Verity light style (for the report and PPT)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

INK = "#1b1f27"
MUTED = "#5b6270"
BRAND = LinearSegmentedColormap.from_list("verity", ["#f3f6fb", "#1a4480"])


def save_confusion(cm: np.ndarray, title: str, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(3.6, 3.2), dpi=160)
    fig.patch.set_facecolor("white")
    ax.imshow(cm, cmap=BRAND)
    labels = ["Safe", "Scam / fraud"]
    ax.set_xticks([0, 1], labels=[f"Pred. {x.lower()}" for x in labels], fontsize=8, color=MUTED)
    ax.set_yticks([0, 1], labels=[f"True {x.lower()}" for x in labels], fontsize=8, color=MUTED)
    top = cm.max() or 1
    for (i, j), v in np.ndenumerate(cm):
        ax.text(j, i, f"{v:,}", ha="center", va="center", fontsize=12, fontweight="semibold",
                color="white" if v > top * 0.55 else INK)
    ax.set_title(title, fontsize=9, color=INK, pad=8)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, facecolor="white")
    plt.close(fig)
