# ランダムノイズ対照実験プロンプト

## 仮説
- H0: EEGをランダムノイズに置き換えてもswitch_gainは変わらない（構造的対応は偶然）
- H1: switch_gainが有意に低下する（構造的対応は実際のEEG信号に依存）
- サブ仮説: 境界インパルス則 J ≈ α∆h（R²≈0.79）もランダムEEGでは崩れる

## Claude Codeへの指示

```
以下の対照実験を実施してください。

### 実験設計
IDPC_Repro_Demo.ipynb のパイプラインをベースに、EEGデータを
ランダムノイズに置き換えた条件で同じ解析を実行する。

### 具体的な手順
1. 各セッションの EEG時系列（PX_eeg_timeseries.csv）を読み込む
2. 同じ平均・分散を持つガウスランダムノイズで置き換える
   - mean = original EEG の mean
   - std = original EEG の std
   - ただし時間構造（自己相関）は破壊する
3. ランダムEEGから Neural Ricci曲率を再計算
4. 元のQuantum Ricci曲率はそのまま使用
5. 以下の指標を計算してオリジナルと比較:
   - switch_gain（observed vs null vs random条件）
   - permutation p値
   - AUC・Accuracy（状態分類）
   - mean abs Pearson（再構成一致度）
   - 境界インパルス則: J ≈ α∆h の回帰係数αとR²

### 図の出力
1. switch_gain比較棒グラフ（original vs random、nullラインも表示）
2. 境界インパルス散布図（original vs random を並べて）
3. Pearson分布（original vs random）

### レポート（日本語・確認用）
reports/random_noise_experiment_report_ja.md に出力

### レポート（英語・公開用）
reports/random_noise_experiment_report_en.md に出力

### 期待される結果
- H1が正しければ: random条件でswitch_gain ≈ null mean（≈0.565）に低下
- H1が正しければ: 境界インパルスのR²が大幅に低下（0.79 → ？）
- H0が正しければ: random条件でもswitch_gainが高いまま
```

## 解釈の指針
- switch_gainがnull平均まで低下 → EEGの実信号が対応構造に必須
- 境界インパルスR²が低下 → 境界事象はEEGの実構造に依存
- どちらも低下しない → 量子側だけで構造が決まる可能性（別の仮説へ）
