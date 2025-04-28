# Google Agent Development Kit (ADK) Tutorial

このリポジトリは、GoogleのAgent Development Kit (ADK)を使用してインテリジェントなエージェントを開発する方法を学ぶためのチュートリアルプロジェクトです。

## 概要

Google Agent Development Kit (ADK)は、Googleの生成AIモデルを活用して、特定のタスクを実行するインテリジェントなエージェントを構築するためのツールキットです。このチュートリアルでは、ADKの基本的な概念から高度な機能まで、段階的に学ぶことができます。

## チュートリアルの内容

このリポジトリには以下のチュートリアル資料が含まれています：

1. **Pythonチュートリアル**: ADKを使用したエージェント開発の基本を学ぶためのPythonコード例
   - 基本的なエージェントの作成
   - ツールを統合したエージェントの開発
   - コンテキスト管理を活用したエージェントの実装

2. **Webベースのチュートリアル**: ADKの概念と使用方法を学ぶためのインタラクティブなWebアプリケーション
   - ADKの概要と主な特徴の説明
   - コード例とデモンストレーション
   - 実践的な演習

## 使用方法

### Pythonチュートリアル

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/adk_tutorial.git
cd adk_tutorial/python_tutorial

# 依存関係をインストール
pip install -e .

# チュートリアルを実行
cd src/google_adk
python main_tutorial.py

# 特定のデモを実行
python main_tutorial.py --demo basic    # 基本的なエージェント
python main_tutorial.py --demo tool     # ツールを使用するエージェント
python main_tutorial.py --demo context  # コンテキスト管理を活用したエージェント
```

### Webチュートリアル

```bash
# バックエンドを起動
cd backend
poetry install
poetry run uvicorn app.main:app --reload

# フロントエンドを起動（別のターミナルで）
cd frontend
npm install
npm run dev
```

その後、ブラウザで http://localhost:5173 にアクセスしてWebチュートリアルを開始できます。

## 前提条件

- Python 3.8以上
- Google AI APIキー（[Google AI Studio](https://ai.google.dev/)から取得可能）
- Node.js 14以上（Webチュートリアルの場合）

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細については[LICENSE](LICENSE)ファイルを参照してください。
