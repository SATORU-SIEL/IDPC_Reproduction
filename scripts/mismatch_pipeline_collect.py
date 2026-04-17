"""
Collect switch_gain + p + shift-test + boundary-impulse metrics from the
four full-notebook mismatch runs (derangement / shift1 / reverse /
random), saved under backups/mm_fullnb_<pattern>/Chapter7/.  The `correct`
baseline is pulled from the original snapshot in
backups/mm_original_state/Chapter7/.
"""
from __future__ import annotations

import json
import os
import re

import numpy as np
import pandas as pd

PATTERNS = ["derangement", "shift1", "reverse", "random"]
BACKUPS = "backups"


def parse_chapter7(root):
    out = {"root": root}
    fc = os.path.join(root, "Chapter7", "final_claim_table.csv")
    bp = os.path.join(root, "Chapter7", "block_permutation_test.csv")
    st = os.path.join(root, "Chapter7", "temporal_shift_test.csv")
    sw = os.path.join(root, "Chapter7", "session_wise_metrics_all_models.csv")

    if os.path.exists(fc):
        df = pd.read_csv(fc)
        row = df[df["claim"].str.contains("block-permuted", case=False)]
        if len(row):
            ev = row["evidence"].iloc[0]
            m = re.search(r"obs\s*switch_gain=([\-\d.eE]+)", ev)
            if m: out["observed_switch_gain"] = float(m.group(1))
            m = re.search(r"null mean=([\-\d.eE]+)", ev)
            if m: out["null_mean_from_claim"] = float(m.group(1))
            m = re.search(r"empirical p=([\-\d.eE]+)", ev)
            if m: out["empirical_p"] = float(m.group(1))
            # grab the best-model cols/mode too
            m = re.search(r"cols=\[([^\]]+)\], mode=(\w+)", ev)
            if m:
                out["best_cols"] = m.group(1)
                out["best_mode"] = m.group(2)
        for tag, key in [("neural-only", "neural_only"),
                         ("quantum-only", "quantum_only"),
                         ("simple mean", "simple_mean")]:
            r = df[df["claim"].str.contains(tag, case=False)]
            if len(r):
                ev = r["evidence"].iloc[0]
                m = re.search(rf"{tag}=([\-\d.eE]+)", ev)
                if m: out[f"baseline_{key}"] = float(m.group(1))
                m = re.search(r"paired sign-test p=([\-\d.eE]+)", ev)
                if m: out[f"baseline_{key}_p"] = float(m.group(1))

    if os.path.exists(bp):
        sg = pd.read_csv(bp)["switch_gain"].to_numpy(float)
        out["null_mean"] = float(sg.mean())
        out["null_sd"] = float(sg.std())
        out["null_min"] = float(sg.min())
        out["null_max"] = float(sg.max())
        out["null_n"] = int(len(sg))
    if os.path.exists(st):
        s = pd.read_csv(st).set_index("shift")["switch_gain"].to_dict()
        out["shift0"] = float(s.get(0, np.nan))
        out["shift20"] = float(s.get(20, np.nan))
    if os.path.exists(sw):
        sw_df = pd.read_csv(sw)
        btr = sw_df[sw_df["model"] == "best_true_search"]
        if len(btr):
            out["per_session_best_mean"] = float(btr["switch_gain"].mean())
            out["per_session_best_median"] = float(btr["switch_gain"].median())
            out["per_session_best_min"] = float(btr["switch_gain"].min())
            out["per_session_best_max"] = float(btr["switch_gain"].max())
            out["n_test_sessions"] = int(len(btr))
    return out


def main():
    per_pattern = {}
    per_pattern["correct"] = parse_chapter7(os.path.join(BACKUPS, "mm_original_state"))
    per_pattern["correct"]["note"] = "original pipeline (correct pairing)"
    for p in PATTERNS:
        per_pattern[p] = parse_chapter7(os.path.join(BACKUPS, f"mm_fullnb_{p}"))

    # derived
    correct = per_pattern["correct"]
    comparison = {
        "correct": {
            "gap_observed_minus_null":
                correct["observed_switch_gain"] - correct["null_mean"],
            "empirical_p": correct["empirical_p"],
        }
    }
    for p in PATTERNS:
        r = per_pattern[p]
        comparison[p] = {
            "delta_vs_correct_obs":
                r["observed_switch_gain"] - correct["observed_switch_gain"],
            "gap_observed_minus_null":
                r["observed_switch_gain"] - r["null_mean"],
            "null_shift_up_vs_correct":
                r["null_mean"] - correct["null_mean"],
            "empirical_p": r["empirical_p"],
            "empirical_p_correct": correct["empirical_p"],
        }
    # rank by empirical p (closer to 1 = more collapsed)
    collapse_ranking = sorted(
        [(p, per_pattern[p]["empirical_p"]) for p in PATTERNS],
        key=lambda t: -t[1])

    out = {
        "per_pattern": per_pattern,
        "comparison": comparison,
        "collapse_ranking": collapse_ranking,
        "method": ("Full-notebook execution of IDPC_Reproduction.ipynb with "
                   "SECTION 1.1-1.3 + SECTION 1.4 (real) cells converted to "
                   "cell_type='raw', and SECTION 1.4 ALTERNATIVE (fake "
                   "pairing) modified per pattern. All downstream cells "
                   "(SECTION 1.5 onwards, Chapter 2-7) run unchanged."),
    }
    os.makedirs("reports", exist_ok=True)
    with open("reports/mismatch_pipeline_metrics.json", "w") as f:
        json.dump(out, f, indent=2, default=float)

    print("\n=== Full-notebook mismatch pipeline summary ===")
    header = f"{'condition':<14s}{'obs':>8s}{'null_mean':>12s}{'gap':>8s}{'empir_p':>10s}"
    print(header)
    print("-" * len(header))
    for cond in ["correct"] + PATTERNS:
        r = per_pattern[cond]
        print(f"{cond:<14s}"
              f"{r['observed_switch_gain']:>8.3f}"
              f"{r['null_mean']:>12.3f}"
              f"{r['observed_switch_gain']-r['null_mean']:>8.3f}"
              f"{r['empirical_p']:>10.3f}")
    print("\nwrote reports/mismatch_pipeline_metrics.json")


if __name__ == "__main__":
    main()
