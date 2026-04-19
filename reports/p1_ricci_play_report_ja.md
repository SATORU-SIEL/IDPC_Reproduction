# P1 Ricci曲率 可視化メモ（退屈しのぎ版）

## 概要
被験者P1の `E_Ricci`（Neural）と `Q_Ricci`（Quantum）の時系列を
z正規化して並べ、対応構造を目視・統計の両面から確認した軽い観察ノート。

## データ
- ソース: `IDPC_Reproduction_ricci/P1_timeseries.csv`
- サンプル数: n = 30（task_idx 0–29）
- 列: `task_idx, E_Ricci, Q_Ricci, Q_Ricci_shifted, Q_Ricci_affine`

## 結果

| 指標 | 値 | p値 |
|---|---:|---:|
| Pearson r (E_z, Q_z) | 0.05 | 0.80 |
| Spearman ρ (E_z, Q_z) | -0.03 | 0.88 |

- 図1: 時系列重ね描き（z正規化） → `reports/figs/p1_ricci_timeseries.png`
- 図2: 散布図（色=task_idx） → `reports/figs/p1_ricci_scatter.png`

## コメント
P1単独・task_idx粒度では E/Q の一致は有意ではない（論文の集団
平均 mean|r|≈0.42 と比べて明確に弱い）。これは単一被験者・短い
時系列のノイズで埋もれたと解釈するのが素直。`Q_Ricci_shifted` や
`Q_Ricci_affine`（空欄が多い）を使った位相補正後で再評価するか、
P1–P26プールで見るのが次の自然な一手。

## 再現手順
```bash
python3 scripts/plot_p1_ricci.py
```
