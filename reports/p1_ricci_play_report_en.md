# P1 Ricci Curvature — Quick Visualization Note

## Summary
A lightweight observational note plotting z-normalized `E_Ricci` (Neural)
and `Q_Ricci` (Quantum) time series for subject P1, with correspondence
statistics.

## Data
- Source: `IDPC_Reproduction_ricci/P1_timeseries.csv`
- Samples: n = 30 (task_idx 0–29)
- Columns: `task_idx, E_Ricci, Q_Ricci, Q_Ricci_shifted, Q_Ricci_affine`

## Results

| Metric | Value | p-value |
|---|---:|---:|
| Pearson r (E_z, Q_z) | 0.05 | 0.80 |
| Spearman ρ (E_z, Q_z) | -0.03 | 0.88 |

- Figure 1: overlaid z-scored time series → `reports/figs/p1_ricci_timeseries.png`
- Figure 2: scatter (color = task_idx) → `reports/figs/p1_ricci_scatter.png`

## Comment
At the single-subject, task-index granularity, the E/Q agreement for P1
is not significant — visibly weaker than the paper's group-level
mean |r| ≈ 0.42. This is consistent with noise dominating a short,
single-subject sequence. Natural next steps: re-evaluate after phase
correction using `Q_Ricci_shifted` / `Q_Ricci_affine`, or pool across
P1–P26.

## Reproduction
```bash
python3 scripts/plot_p1_ricci.py
```
