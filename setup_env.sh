#!/bin/bash
# IDPC_Reproduction — 環境セットアップスクリプト
# 使い方: bash setup_env.sh

echo "=== IDPC_Reproduction 環境セットアップ ==="

# Pythonバージョン確認
python3 --version

# 仮想環境作成
if [ ! -d ".venv" ]; then
  echo "仮想環境を作成中..."
  python3 -m venv .venv
fi

# 仮想環境を有効化
source .venv/bin/activate

# 依存関係インストール
echo "依存関係をインストール中..."
pip install --upgrade pip
pip install -r requirements.txt
pip install jupyter nbconvert

echo ""
echo "=== セットアップ完了 ==="
echo "次のコマンドで仮想環境を有効化してください:"
echo "  source .venv/bin/activate"
echo ""
echo "Jupyterを起動するには:"
echo "  jupyter notebook"
