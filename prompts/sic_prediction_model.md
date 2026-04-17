# SIC予測モデル実験プロンプト

## 仮説
SICが成立するタイミング（境界事象の発生）は、直前のφ軌道・位相・残差から
事前予測できるか？

- H0: 予測精度がランダム（AUC ≈ 0.50）→ 境界事象は予測不能
- H1: AUC > 0.65 → φ軌道から事前予測可能

## Claude Codeへの指示

```
以下のSIC予測モデル実験を実施してください。

### 予測タスクの定義
各時点tで「t+1またはt+2で境界事象が発生するか？」を予測する
二値分類タスク（発生=1, 非発生=0）

### 特徴量（各時点tで計算）
- φ(t), φ(t-1), φ(t-2)   : intersection variable の値
- dφ(t) = φ(t) - φ(t-1)  : φの変化率
- ε(t)                    : 構造的位相残差
- dε(t) = ε(t) - ε(t-1)  : 残差の変化率
- ψE(t) - ψQ(t)           : 位相差
- |ψE(t) - ψQ(t)|         : 位相差の絶対値
- 直近境界事象からの経過時間
- 直近境界事象の強度J

### モデル
以下の3つを比較:
1. Logistic Regression（解釈性重視）
2. Random Forest（特徴量重要度）
3. 直近事象からの経過時間だけのベースライン

### 評価
- LOSO（Leave-One-Session-Out）交差検証
- AUC、Precision、Recall、F1
- 特徴量重要度（Random Forestの場合）
- 予測リードタイム: t+1 vs t+2 vs t+3で精度がどう変わるか

### 追加解析
- 予測精度が高いセッションと低いセッションの比較
- 「φが急激に変化するとき（|dφ|が大きいとき）に予測精度が上がるか？」
  （論文Section 8.11 Prediction 1の検証）

### 出力
- reports/sic_prediction_report_ja.md（日本語・確認用）
- reports/sic_prediction_report_en.md（英語・公開用）
- reports/sic_prediction_auc.png（モデル別AUC比較）
- reports/sic_prediction_features.png（特徴量重要度）
- reports/sic_prediction_leadtime.png（リードタイム別精度）
- reports/sic_prediction_metrics.json

### 解釈の指針
AUCが...
- 0.50〜0.55 → 予測不能（H0支持）
- 0.55〜0.65 → 弱い予測可能性
- 0.65〜0.75 → 中程度の予測可能性（H1支持）
- 0.75以上   → 強い予測可能性（論文の新たな発見）
```

## 論文との接続
- Section 8.11 Prediction 1:「動的遷移依存性」の定量的検証
  「|dφ|が大きいときに対応の一意性が局在する」→ 予測精度との相関で確認
- 結果次第で論文の次バージョンに「SIC予測可能性」のセクションを追加可能

## 期待される特徴量重要度の順位（仮説）
1. |dφ|   （論文Prediction 1と整合）
2. ε(t)   （残差収縮との関係）
3. |位相差| （位相同期との関係）
4. 経過時間 （周期性があれば）
