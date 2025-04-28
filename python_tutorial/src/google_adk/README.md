# Google Agent Development Kit (ADK) チュートリアル

このチュートリアルでは、GoogleのAgent Development Kit (ADK)を使用してインテリジェントなエージェントを開発する方法を説明します。

## 目次

1. [概要](#概要)
2. [前提条件](#前提条件)
3. [インストール](#インストール)
4. [チュートリアルの構成](#チュートリアルの構成)
5. [基本的な使い方](#基本的な使い方)
6. [高度な機能](#高度な機能)
7. [サンプルコード](#サンプルコード)
8. [参考リソース](#参考リソース)

## 概要

Google Agent Development Kit (ADK)は、Googleの生成AIモデルを活用して、特定のタスクを実行するインテリジェントなエージェントを構築するためのツールキットです。ADKを使用することで、開発者は自然言語処理、情報検索、タスク実行などの機能を持つエージェントを簡単に作成できます。

このチュートリアルでは、ADKの基本的な概念から高度な機能まで、段階的に学ぶことができます。サンプルコードと詳細な解説を通じて、実際のアプリケーションでADKを活用する方法を学びましょう。

### ADKの主な特徴

- **自然言語理解**: ユーザーの入力を理解し、適切な応答を生成
- **ツール統合**: 外部APIやサービスと連携して情報を取得・処理
- **コンテキスト管理**: 会話の文脈を維持し、一貫した対話を実現
- **カスタマイズ可能**: 特定のドメインやタスクに特化したエージェントを構築可能
- **マルチモーダル対応**: テキスト、画像、音声などの複数のモダリティを処理可能

## 前提条件

- Python 3.8以上
- Google AI APIキー（[Google AI Studio](https://ai.google.dev/)から取得可能）
- 基本的なPythonプログラミングの知識

## インストール

1. 必要なパッケージをインストール:

```bash
pip install google-generativeai
```

2. Google AI APIキーを環境変数に設定:

```bash
export GOOGLE_API_KEY='あなたのAPIキー'
```

## チュートリアルの構成

このチュートリアルは以下のセクションで構成されています：

1. **基本概念**: ADKの基本的な概念と構成要素について学びます
2. **シンプルなエージェント**: 基本的な対話エージェントの作成方法を学びます
3. **ツールの統合**: エージェントに外部ツールを統合する方法を学びます
4. **高度な機能**: コンテキスト管理、マルチモーダル入力などの高度な機能を学びます

## 基本的な使い方

### エージェントの作成

```python
from google_adk.adk_tutorial import Agent, AgentConfig

# エージェント設定の作成
config = AgentConfig(
    model_name="gemini-1.5-pro",
    temperature=0.7,
    max_output_tokens=1024
)

# エージェントの作成
agent = Agent(
    name="シンプルアシスタント",
    description="ユーザーの質問に答える基本的なアシスタントです。",
    config=config
)

# エージェントとの対話
response = agent.process_message("こんにちは、今日の天気を教えてください。")
print(response)
```

### ツールの統合

```python
from google_adk.adk_tutorial import Agent, AgentConfig, Tool

# 天気情報を取得するツール関数
def get_weather(location, unit="celsius"):
    # 実際のAPIを呼び出す代わりにシミュレーションデータを返す
    return {
        "location": location,
        "temperature": 22 if unit == "celsius" else 72,
        "condition": "晴れ"
    }

# ツールの作成
weather_tool = Tool(
    name="get_weather",
    description="指定された場所の天気情報を取得します",
    function=get_weather,
    parameter_schema={
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "天気を取得する場所（都市名など）"
            },
            "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "温度の単位"
            }
        },
        "required": ["location"]
    }
)

# エージェントの作成とツールの追加
agent = Agent(
    name="天気アシスタント",
    description="天気情報を提供するアシスタントです。",
    config=AgentConfig(),
    tools=[weather_tool]
)

# ツールを実行
result = agent.execute_tool("get_weather", location="東京", unit="celsius")
print(result)
```

## 高度な機能

### コンテキスト管理

ADKは会話のコンテキストを自動的に管理し、一貫した対話を実現します。エージェントは過去の会話履歴を考慮して応答を生成します。

```python
# 会話の開始
response1 = agent.process_message("東京の天気を教えて")
print(response1)

# コンテキストを維持した続きの会話
response2 = agent.process_message("明日はどう？")  # 「東京」のコンテキストが維持される
print(response2)
```

## サンプルコード

このチュートリアルには、以下のサンプルコードが含まれています：

- `basic_agent.py`: 基本的なエージェントの作成と対話のサンプル
- `tool_agent.py`: ツールを統合したエージェントのサンプル

サンプルコードを実行するには：

```bash
# 基本的なエージェントのサンプルを実行
python examples/basic_agent.py

# ツールを統合したエージェントのサンプルを実行
python examples/tool_agent.py
```

## 参考リソース

- [Google AI Platform ドキュメント](https://ai.google.dev/)
- [Gemini API リファレンス](https://ai.google.dev/gemini-api/docs)
- [Google AI Python SDK](https://github.com/google/generative-ai-python)
