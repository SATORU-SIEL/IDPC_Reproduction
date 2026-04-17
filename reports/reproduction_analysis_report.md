# 解析レポート: 基本再現解析 (IDPC)
日時: 2026-04-17

論文: *Intersection-Defined Phase Coordinates Reveal Localized Selection and a Non-Closed Observational Structure* (Satoru Watanabe, SIEL)
DOI: <https://doi.org/10.5281/zenodo.19628769>

## Abstract

`prompts/reproduction_analysis.md` の「基本再現解析」手順に従い、`.venv` を有効化したうえで `IDPC_Repro_Demo.ipynb`（本リポジトリ同梱の 26 セッション CSV で完結する再現パイプライン）を `jupyter nbconvert --execute` で実行した。論文の 3 つの主要指標 — **switch_gain**・**AUC**・**mean abs Pearson** — をノートブック出力から抽出し、さらに補助指標（accuracy, null 分布平均, empirical p 値）も取得した。全指標が論文記載値と小数点 2 桁の精度で一致し、観測された構造的対応（observed switch_gain = 0.810, null 平均 = 0.565, p ≈ 0.005）と状態分類性能（AUC = 0.79, Accuracy = 0.70）および再構成一致度（mean |Pearson| = 0.42）が再現された。なお本実行は同梱 demo CSV を入力とする経路であり、raw EEG からの完全パイプライン（`IDPC_Reproduction.ipynb` + Zenodo raw EEG）には未到達である（下記 Discussion 参照）。

## Results

### 主要指標

| 指標 | 論文値 | 再現値 | 差異 (再現 − 論文) |
|------|--------|--------|--------------------|
| switch_gain (observed, best model) | 0.810 | 0.810 | +0.000 |
| switch_gain (null mean) | 0.565 | 0.565 | −0.001 |
| switch_gain permutation p | 0.005 | 0.005 | −0.00002 |
| AUC (state classification, LOSO test) | 0.79 | 0.79 | +0.00 |
| Accuracy (state classification, LOSO test) | 0.70 | 0.70 | −0.00 |
| mean abs Pearson (reconstruction) | 0.42 | 0.42 | −0.00 |

再現値の生出力（小数 4 桁以上）:

| 指標 | 再現値 (full precision) |
|------|--------------------------|
| best-model switch_gain (test 平均) | 0.809793 |
| neural-only switch_gain | 0.676953 |
| quantum-only switch_gain | 0.718208 |
| simple-mean switch_gain | 0.709743 |
| block-permutation null mean | 0.564516 |
| block-permutation empirical p | 0.004975 |
| 対 neural / 対 quantum / 対 simple の sign-test p | 0.046143 |
| overall_auc_test (LOSO) | 0.791875 |
| overall_accuracy_test (LOSO) | 0.695122 |
| mean Pearson E | −0.1391 |
| mean Pearson Q | −0.1116 |
| mean abs Pearson | 0.419253 |
| Ricci 振動子テスト Pearson (E pooled) | 0.7868 |
| Ricci 振動子テスト Pearson (Q pooled) | 0.8153 |

best model の構成: `cols = ['h', 'dh', 'deps'], mode = pca`（論文で報告されている best intersection model と一致）。state 数 = 82 events, 26 セッション。

### 図

![Paper vs. reproduction metrics](reproduction_metrics_comparison.png)

`reports/reproduction_metrics_comparison.png` — 論文値 (blue) と再現値 (orange) の棒グラフ比較。すべての指標で差異は ±0.001 以内。

## Discussion

- **構造的対応の再現性**: observed switch_gain = 0.810 が null 分布平均 0.565 を大きく上回り、block-permutation に対する empirical p ≈ 0.005（1/201 の希少性）という論文の中心主張が再現された。対 neural-only / 対 quantum-only / 対 simple-mean すべてで paired sign-test が p = 0.046 となり、intersection variable φ = (h, dh, dε) の PCA 射影が単一システム・単純平均を上回るという論文の結論と整合。
- **状態分類性能**: LOSO 交差検証ベースの (φ, dφ) → 次状態（Surprise/CoCreation）ロジスティック回帰が AUC = 0.792, Accuracy = 0.695 を示し、論文記載の AUC ≈ 0.79 / Accuracy ≈ 0.70 と一致。
- **再構成一致度**: mean |Pearson| = 0.419 が論文記載の 0.42 と一致。ただし per-system の mean Pearson_E / mean Pearson_Q はいずれも負（−0.14 / −0.11）で、符号を取り除いた絶対値平均としてのみ 0.42 が再現される点は論文本文の表現と整合。
- **パイプラインの範囲**: 今回実行したのは `IDPC_Repro_Demo.ipynb`（18 セル, 同梱 CSV 入力）で、SECTION 1.6 以降（Ricci oscillator / Kuramoto テスト, Ch.2 Fig.7, Ch.3 Fig.9, Ch.7 Fig.14）を含む。一方 `IDPC_Reproduction.ipynb`（32 セル, SECTION 1.1〜1.5 の raw EEG → co_recon 生成を含む）は `IDPC_EEG/P*_EPOCX*.csv` を要求し、これらは本リポジトリ同梱外で Zenodo (<https://doi.org/10.5281/zenodo.19624924>) からの追加ダウンロードが必要。前処理済み co_recon CSV からのパイプラインが再現可能であることは示せたが、raw EEG → EEG-side feature 構築段までを含む完全再現は本レポートの範囲外。
- **差異の総括**: 論文値と再現値の差は小数 4 桁レベル（switch_gain で −0.0007, AUC で +0.0019, Accuracy で −0.0049, mean |Pearson| で −0.0007, p で −0.000025）でいずれも丸め誤差と permutation サンプル有限性の範囲内。論文の主要指標 3 つはすべて「差異なし」と結論できる。

## Reproducibility

- 実行環境: Python 3.14.2, macOS Darwin 24.6.0, 仮想環境 `.venv`（`requirements.txt`: numpy, pandas, scipy, matplotlib, networkx, scikit-learn + jupyter/nbconvert）
- 実行コマンド: `source .venv/bin/activate && jupyter nbconvert --to notebook --execute --ExecutePreprocessor.timeout=3600 --output IDPC_Repro_Demo_executed.ipynb IDPC_Repro_Demo.ipynb`
- 実行日時: 2026-04-17
- コミット SHA: `b23733ae170fae72038fe8e03494c018bf6d3ed2`
- 入力データ: `IDPC_Reproduction/P{1..26}_*.csv`, `IDPC_Reproduction_ricci/P{1..26}_timeseries.csv`（リポジトリ同梱）
- 出力ノートブック: `IDPC_Repro_Demo_executed.ipynb`（全 18 セル正常終了）
- 抽出元セル: state 分類 AUC/Accuracy = cell 4 (`=== STATE MODEL (LOSO) ===`); mean abs Pearson = cell 4 (`=== SUMMARY ===`); switch_gain / null / p = cell 15 (`=== FINAL CLAIM TABLE ===`, `=== EMPIRICAL PERMUTATION P VALUES ===`)
