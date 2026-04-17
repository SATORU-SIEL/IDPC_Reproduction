#!/bin/bash
# IDPC_Reproduction — 解析実行スクリプト
# 使い方: bash run_analysis.sh [notebook_name]
# 例: bash run_analysis.sh IDPC_Reproduction

NOTEBOOK=${1:-IDPC_Reproduction}

echo "=== 解析実行: ${NOTEBOOK}.ipynb ==="

# 仮想環境を有効化
if [ -d ".venv" ]; then
  source .venv/bin/activate
else
  echo "ERROR: 仮想環境が見つかりません。先に bash setup_env.sh を実行してください。"
  exit 1
fi

# ノートブックをPythonスクリプトとして実行
echo "実行中: ${NOTEBOOK}.ipynb"
jupyter nbconvert \
  --to notebook \
  --execute \
  --ExecutePreprocessor.timeout=3600 \
  --output ${NOTEBOOK}_executed.ipynb \
  ${NOTEBOOK}.ipynb

echo ""
echo "=== 実行完了 ==="
echo "出力: ${NOTEBOOK}_executed.ipynb"
