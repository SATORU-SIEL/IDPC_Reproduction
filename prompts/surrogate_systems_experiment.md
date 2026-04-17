# サロゲートシステム実験プロンプト

## 仮説
- H0: 全く無関係な2系列（株価・気温など）でも同じswtich_gainが出る → 方法論的バグ
- H1: switch_gainがnull平均付近に留まる → EEG-量子対応は特異的
- 哲学的可能性: H0が支持された場合、O3があらゆる独立システムの対応を観測している可能性

## Claude Codeへの指示

```
以下のサロゲートシステム実験を実施してください。

### 使用するデータ
yfinanceとopen-meteoで以下を取得:
- System A（EEGの代わり）: 日経平均株価（^N225）の日次終値
- System B（量子の代わり）: 東京の日次平均気温（Open-Meteo API、緯度35.68、経度139.69）
- 期間: 2023-01-01 〜 2024-12-31（約500日）

### データ前処理
1. 欠損値を線形補間
2. 26セッション × 約19時点に分割（元データのセッション構造に合わせる）
3. 各セッション内でz-score標準化
4. Ricci曲率の代わりにローリング相関行列からOllivier-Ricci曲率を計算

### 実行する解析（元論文と同じパイプライン）
1. 各セッションでRicci曲率時系列を構築
2. intersection variable φを構築
3. switch_gainを計算（block permutation n=200）
4. 状態分類（AUC）
5. 境界インパルス則 J ≈ α∆h のR²

### 追加データセット（ロバストネス確認）
- System A: S&P500（^GSPC）/ System B: ニューヨーク気温
- System A: BTC-USD / System B: 東京気温

### 出力
- reports/surrogate_experiment_report_ja.md（日本語・確認用）
- reports/surrogate_experiment_report_en.md（英語・公開用）
- reports/surrogate_switch_gain_comparison.png（元論文・ランダム・サロゲートの3条件比較）
- reports/surrogate_metrics.json

### 解釈の指針
switch_gainが...
- 0.75以上 → 方法論的問題の可能性（または O3 仮説）
- 0.60〜0.75 → 要注意・追加検討が必要
- null平均（0.565）付近 → EEG-量子対応は特異的（論文の主張を強化）
```

## 必要なライブラリ
```bash
pip install yfinance requests
```

## 期待される結果と論文への影響
| 結果 | 解釈 | 論文への影響 |
|------|------|-------------|
| switch_gain ≈ null（0.565） | EEG-量子対応は特異的 | 主張を大幅に強化 |
| switch_gain 高い（0.75+） | 方法論の問題 or O3普遍性 | 重要な追加考察が必要 |
| 中間（0.60〜0.75） | 部分的特異性 | 条件付き支持 |
