"""Plot ERicci vs QRicci for subject P1 and compute correspondence stats."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "IDPC_Reproduction_ricci" / "P1_timeseries.csv"
FIG_DIR = ROOT / "reports" / "figs"
FIG_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(SRC)
t = df["task_idx"].to_numpy()
e = df["E_Ricci"].to_numpy()
q = df["Q_Ricci"].to_numpy()

def znorm(x):
    return (x - np.nanmean(x)) / np.nanstd(x)

ez, qz = znorm(e), znorm(q)
mask = ~(np.isnan(ez) | np.isnan(qz))
r_p, p_p = pearsonr(ez[mask], qz[mask])
r_s, p_s = spearmanr(ez[mask], qz[mask])

fig, axes = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
axes[0].plot(t, ez, "o-", color="#1f77b4", label="E_Ricci (z)")
axes[0].plot(t, qz, "s-", color="#d62728", label="Q_Ricci (z)")
axes[0].set_ylabel("z-score")
axes[0].set_title(f"P1 — Neural vs Quantum Ricci (Pearson r={r_p:.2f}, p={p_p:.3f})")
axes[0].legend(loc="best")
axes[0].grid(alpha=0.3)

axes[1].plot(t, ez - qz, "o-", color="#2ca02c")
axes[1].axhline(0, color="k", lw=0.5)
axes[1].set_ylabel("E_z − Q_z")
axes[1].set_xlabel("task_idx")
axes[1].set_title("Residual (structural mismatch)")
axes[1].grid(alpha=0.3)

fig.tight_layout()
out1 = FIG_DIR / "p1_ricci_timeseries.png"
fig.savefig(out1, dpi=140)
plt.close(fig)

fig, ax = plt.subplots(figsize=(5, 5))
ax.scatter(ez, qz, c=t, cmap="viridis", s=50, edgecolor="k")
lims = [min(ez.min(), qz.min()), max(ez.max(), qz.max())]
ax.plot(lims, lims, "k--", alpha=0.4, label="y=x")
ax.set_xlabel("E_Ricci (z)")
ax.set_ylabel("Q_Ricci (z)")
ax.set_title(f"P1 scatter — Spearman ρ={r_s:.2f}, p={p_s:.3f}")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
out2 = FIG_DIR / "p1_ricci_scatter.png"
fig.savefig(out2, dpi=140)
plt.close(fig)

print(f"n={mask.sum()}  Pearson r={r_p:.3f} (p={p_p:.4f})  Spearman ρ={r_s:.3f} (p={p_s:.4f})")
print(f"saved: {out1.relative_to(ROOT)}")
print(f"saved: {out2.relative_to(ROOT)}")
