"""Generate reports/mismatch_pipeline_switch_gain.png from the four mismatch
runs plus the correct/reference pipeline."""
from __future__ import annotations

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPORTS = "reports"
METRICS = os.path.join(REPORTS, "mismatch_pipeline_metrics.json")


def main():
    m = json.load(open(METRICS))
    per = m["per_pattern"]
    order = ["correct", "derangement", "shift1", "reverse", "random"]
    pretty = {"correct": "correct\npairing",
              "derangement": "derangement\n(seed=0)",
              "shift1": "shift +1\nσ(i)=i+1",
              "reverse": "reverse\nσ(i)=25-i",
              "random": "random\n(seed=42)"}

    obs = [per[c]["observed_switch_gain"] for c in order]
    nulls = [per[c]["null_mean"] for c in order]
    null_sds = [per[c]["null_sd"] for c in order]
    ps = [per[c]["empirical_p"] for c in order]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.8))

    x = np.arange(len(order)); w = 0.35
    axes[0].bar(x - w/2, obs, w, color=["#1f77b4"] + ["#d62728"] * 4,
                label="observed switch_gain")
    axes[0].bar(x + w/2, nulls, w, yerr=null_sds, capsize=3,
                color=["#aec7e8"] + ["#ff9896"] * 4,
                label="null mean (block-perm, 200)")
    for i, p in enumerate(ps):
        y = max(obs[i], nulls[i]) + 0.02
        axes[0].text(x[i], y, f"p={p:.3f}", ha="center", fontsize=9)
    for i, v in enumerate(obs):
        axes[0].text(x[i] - w/2, v - 0.04, f"{v:.2f}",
                     ha="center", color="white", fontsize=9, fontweight="bold")
    axes[0].axhline(0.565, ls=":", color="grey",
                    label="paper null mean (0.565)")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels([pretty[c] for c in order], fontsize=9)
    axes[0].set_ylabel("switch_gain")
    axes[0].set_ylim(0.45, 0.90)
    axes[0].set_title(
        "A. observed vs null switch_gain under correct vs mismatched pairings"
    )
    axes[0].grid(axis="y", alpha=0.3)
    axes[0].legend(loc="upper right", fontsize=9)

    # Panel B: gap (observed − null) by condition, which is the key scalar
    gap = [o - n for o, n in zip(obs, nulls)]
    colors_gap = ["#1f77b4"] + ["#d62728"] * 4
    axes[1].bar(x, gap, color=colors_gap, edgecolor="black", alpha=0.85)
    for i, (g, p) in enumerate(zip(gap, ps)):
        axes[1].text(i, g + 0.005, f"{g:+.3f}\np={p:.3f}",
                     ha="center", fontsize=9)
    axes[1].axhline(0, color="black", linewidth=0.6)
    axes[1].axhline(0.05, ls="--", color="purple", alpha=0.5,
                    label="5% gap threshold")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels([pretty[c] for c in order], fontsize=9)
    axes[1].set_ylabel("observed − null  (session-specific block-perm gap)")
    axes[1].set_title(
        "B. observed-minus-null gap (structural-correspondence margin)"
    )
    axes[1].set_ylim(0, 0.30)
    axes[1].grid(axis="y", alpha=0.3)
    axes[1].legend(loc="upper right", fontsize=9)

    plt.suptitle(
        "Mismatched-pairing full-pipeline experiment — Section 7.2 reproduction",
        y=1.02)
    plt.tight_layout()
    p = os.path.join(REPORTS, "mismatch_pipeline_switch_gain.png")
    plt.savefig(p, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print("wrote", p)


if __name__ == "__main__":
    main()
