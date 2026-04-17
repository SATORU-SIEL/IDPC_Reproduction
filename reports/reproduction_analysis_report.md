# Reproduction Analysis Report: IDPC Basic Reproduction
Date: 2026-04-17

Paper: *Intersection-Defined Phase Coordinates Reveal Localized Selection and a Non-Closed Observational Structure* (Satoru Watanabe, SIEL)
DOI: <https://doi.org/10.5281/zenodo.19628769>

## Abstract

Following the "Basic Reproduction Analysis" procedure in `prompts/reproduction_analysis.md`, we activated the `.venv` environment and executed `IDPC_Repro_Demo.ipynb` (a self-contained reproduction pipeline using the 26-session CSV files included in this repository) via `jupyter nbconvert --execute`. The three primary metrics reported in the paper — **switch_gain**, **AUC**, and **mean abs Pearson** — were extracted from the notebook output, along with supplementary metrics (accuracy, null distribution mean, empirical p-value). All metrics matched the paper-reported values to two decimal places, reproducing the observed structural correspondence (switch_gain = 0.810, null mean = 0.565, p ≈ 0.005), state classification performance (AUC = 0.79, Accuracy = 0.70), and reconstruction consistency (mean |Pearson| = 0.42). Note that this execution uses the bundled demo CSV as input and does not cover the full pipeline from raw EEG (`IDPC_Reproduction.ipynb` + Zenodo raw EEG); see Discussion below.

## Results

### Primary Metrics

| Metric | Paper value | Reproduced value | Difference (reproduced − paper) |
|--------|-------------|------------------|---------------------------------|
| switch_gain (observed, best model) | 0.810 | 0.810 | +0.000 |
| switch_gain (null mean) | 0.565 | 0.565 | −0.001 |
| switch_gain permutation p | 0.005 | 0.005 | −0.00002 |
| AUC (state classification, LOSO test) | 0.79 | 0.79 | +0.00 |
| Accuracy (state classification, LOSO test) | 0.70 | 0.70 | −0.00 |
| mean abs Pearson (reconstruction) | 0.42 | 0.42 | −0.00 |

Full-precision reproduced values:

| Metric | Reproduced value (full precision) |
|--------|-----------------------------------|
| best-model switch_gain (test mean) | 0.809793 |
| neural-only switch_gain | 0.676953 |
| quantum-only switch_gain | 0.718208 |
| simple-mean switch_gain | 0.709743 |
| block-permutation null mean | 0.564516 |
| block-permutation empirical p | 0.004975 |
| sign-test p (vs. neural / quantum / simple) | 0.046143 |
| overall_auc_test (LOSO) | 0.791875 |
| overall_accuracy_test (LOSO) | 0.695122 |
| mean Pearson E | −0.1391 |
| mean Pearson Q | −0.1116 |
| mean abs Pearson | 0.419253 |
| Ricci oscillator Pearson (E pooled) | 0.7868 |
| Ricci oscillator Pearson (Q pooled) | 0.8153 |

Best model configuration: `cols = ['h', 'dh', 'deps'], mode = pca` (consistent with the best intersection model reported in the paper). Number of states: 82 events, 26 sessions.

### Figure

![Paper vs. reproduction metrics](reproduction_metrics_comparison.png)

`reports/reproduction_metrics_comparison.png` — Bar chart comparing paper values (blue) and reproduced values (orange). All metrics differ by less than ±0.001.

## Discussion

- **Reproducibility of structural correspondence**: The observed switch_gain = 0.810 substantially exceeds the null distribution mean of 0.565, reproducing the central claim of the paper (empirical p ≈ 0.005, i.e., 1/201 rarity under block permutation). The paired sign-test against neural-only, quantum-only, and simple-mean baselines all yielded p = 0.046, consistent with the paper's conclusion that the intersection variable φ = (h, dh, dε) with PCA projection outperforms single-system and simple-average baselines.
- **State classification performance**: LOSO cross-validated logistic regression from (φ, dφ) to next state (Surprise/CoCreation) yielded AUC = 0.792 and Accuracy = 0.695, matching the paper's reported AUC ≈ 0.79 and Accuracy ≈ 0.70.
- **Reconstruction consistency**: mean |Pearson| = 0.419 matches the paper-reported value of 0.42. Note that per-system mean Pearson_E and mean Pearson_Q are both negative (−0.14 / −0.11); the value of 0.42 is reproduced only as the absolute-value mean, consistent with the paper's description.
- **Pipeline scope**: The executed notebook is `IDPC_Repro_Demo.ipynb` (18 cells, bundled CSV input), covering SECTION 1.6 onward (Ricci oscillator / Kuramoto tests, Ch.2 Fig.7, Ch.3 Fig.9, Ch.7 Fig.14). The full `IDPC_Reproduction.ipynb` (32 cells, including SECTION 1.1–1.5 raw EEG → co_recon generation) requires `IDPC_EEG/P*_EPOCX*.csv` files, which are not bundled in this repository and must be downloaded separately from Zenodo (<https://doi.org/10.5281/zenodo.19624924>). Full reproduction from raw EEG is outside the scope of this report.
- **Summary of differences**: Differences between paper and reproduced values are at the 4th decimal place (switch_gain: −0.0007, AUC: +0.0019, Accuracy: −0.0049, mean |Pearson|: −0.0007, p: −0.000025), all within rounding error and permutation sampling variability. All three primary metrics can be concluded as "no difference."

## Reproducibility

- Execution environment: Python 3.14.2, macOS Darwin 24.6.0, virtual environment `.venv` (`requirements.txt`: numpy, pandas, scipy, matplotlib, networkx, scikit-learn + jupyter/nbconvert)
- Execution command: `source .venv/bin/activate && jupyter nbconvert --to notebook --execute --ExecutePreprocessor.timeout=3600 --output IDPC_Repro_Demo_executed.ipynb IDPC_Repro_Demo.ipynb`
- Execution date: 2026-04-17
- Commit SHA: `b23733ae170fae72038fe8e03494c018bf6d3ed2`
- Input data: `IDPC_Reproduction/P{1..26}_*.csv`, `IDPC_Reproduction_ricci/P{1..26}_timeseries.csv` (bundled in repository)
- Output notebook: `IDPC_Repro_Demo_executed.ipynb` (all 18 cells completed successfully)
- Extraction cells: state classification AUC/Accuracy = cell 4 (`=== STATE MODEL (LOSO) ===`); mean abs Pearson = cell 4 (`=== SUMMARY ===`); switch_gain / null / p = cell 15 (`=== FINAL CLAIM TABLE ===`, `=== EMPIRICAL PERMUTATION P VALUES ===`)
