# 再現解析プロンプトテンプレート

## 基本再現解析

```
IDPC_Reproductionリポジトリをcloneして、以下を実行してください:
1. bash setup_env.sh で環境を構築
2. IDPC_Reproduction.ipynb を実行
3. 論文の主要指標（switch_gain, AUC, mean abs Pearson）を抽出
4. 論文記載値と比較してレポートをMarkdownで出力
```

## 感度分析

```
以下のパラメータを変えて感度分析を実行し、結果をレポートしてください:
- top_k_edges: [3, 4, 5]
- smoothing_window: [0.1, 0.25, 0.5] 秒
- permutation_n: [200, 1000, 2000]
各条件でswitch_gain, AUC, p値を記録し、元論文の値との差異を表で示してください。
```

## 新セッション解析

```
新しいセッションデータ [ファイルパス] を追加して:
1. EEG・量子時系列を読み込む
2. Ricci曲率を算出
3. intersection variable φを構築
4. switch_gain, AUC, state classificationを計算
5. 既存26セッションの結果と比較したレポートを出力
```

## ロバストネス検証

```
以下の操作を行い、構造がどのように崩れるかを検証してください:
1. 時間シフト（shift=2, 5, 10, 20）でswitch_gainの変化を確認
2. ミスマッチペアリングでpermutation testを再実行
3. 各条件の結果を論文Fig.14と比較したレポートを出力
```

## レポート出力形式

```markdown
# 解析レポート: [解析名]
日時: YYYY-MM-DD

## Abstract
（3-5文で結果の要約）

## Results
### 主要指標
| 指標 | 論文値 | 再現値 | 差異 |
|------|--------|--------|------|

### 図
（matplotlibで生成した図）

## Discussion
（論文との比較・考察）

## Reproducibility
- 実行環境: Python x.x
- 実行日時: 
- コミットSHA: 
```
