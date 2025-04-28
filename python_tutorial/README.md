# Google Agent Development Kit (ADK) チュートリアル

このチュートリアルでは、Google Agent Development Kit (ADK) の基本的な使い方を Python で実装したサンプルを通じて学びます。ADK を使用すると、Googleの生成AIモデルを活用して、特定のタスクを実行するインテリジェントなエージェントを構築することができます。

## 目次

1. [ADK の概要](#adk-の概要)
2. [チュートリアルの構成](#チュートリアルの構成)
3. [使用方法](#使用方法)
4. [コンポーネントの説明](#コンポーネントの説明)
   - [Agent](#agent)
   - [AgentConfig](#agentconfig)
   - [Tool](#tool)
   - [Model Contexts Protocol (MCP)](#model-contexts-protocol-mcp)
5. [デモの実行](#デモの実行)
6. [コード例](#コード例)
7. [参考リソース](#参考リソース)

## ADK の概要

Google Agent Development Kit (ADK) は、Googleの生成AIモデルを活用して、特定のタスクを実行するインテリジェントなエージェントを構築するためのツールキットです。ADK を使用することで、自然言語理解、ツール統合、コンテキスト管理などの機能を持つエージェントを簡単に開発することができます。

### 主な特徴

- **自然言語理解**: ユーザーの入力を理解し、適切な応答を生成
- **ツール統合**: 外部APIやサービスと連携して情報を取得・処理
- **コンテキスト管理**: 会話の文脈を維持し、一貫した対話を実現
- **Model Contexts Protocol (MCP)**: 複数のコンテキストを管理し、情報を共有
- **カスタマイズ可能**: 特定のドメインやタスクに特化したエージェントを構築可能
- **マルチモーダル対応**: テキスト、画像、音声などの複数のモダリティを処理可能

### ADK の仕組み

1. **エージェント設定**: エージェントの名前、説明、使用するモデル、パラメータなどを設定
2. **ツール統合**: エージェントが使用するツール（外部API、関数など）を定義
3. **プロンプト設計**: エージェントの動作を制御するシステムプロンプトを設計
4. **対話処理**: ユーザーの入力を処理し、適切な応答を生成
5. **コンテキスト管理**: 会話の文脈を維持し、一貫した対話を実現

## チュートリアルの構成

このチュートリアルは、ADK の基本的な概念と使用方法を示すために、以下のコンポーネントで構成されています：

- **基本クラス**:
  - `Agent` - エージェントの基本クラス
  - `AgentConfig` - エージェントの設定を管理するクラス
  - `Tool` - エージェントが使用するツールを定義するクラス
- **デモ**:
  - 基本的なエージェント - シンプルな対話エージェント
  - ツールを使用するエージェント - 外部ツールを活用するエージェント
  - コンテキスト管理を活用したエージェント - 会話の文脈を維持するエージェント
  - Model Contexts Protocol (MCP)を使用するエージェント - 複数のコンテキストを管理するエージェント

## 使用方法

### 必要条件

- Python 3.8 以上
- Google AI APIキー（[Google AI Studio](https://ai.google.dev/)から取得可能）

### インストール

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/adk_tutorial.git
cd adk_tutorial/python_tutorial

# 依存関係をインストール
pip install -e .
```

### 実行方法

すべてのデモを実行するには：

```bash
cd src/google_adk
python main_tutorial.py
```

特定のデモのみを実行するには：

```bash
# 基本的なエージェントデモ
python main_tutorial.py --demo basic

# ツールを使用するエージェントデモ
python main_tutorial.py --demo tool

# コンテキスト管理を活用したエージェントデモ
python main_tutorial.py --demo context

# Model Contexts Protocol (MCP)を使用するエージェントデモ
python main_tutorial.py --demo mcp
```

詳細なログを表示するには：

```bash
python main_tutorial.py --verbose
```

## コンポーネントの説明

### Agent

`Agent` は、エージェントの基本クラスです。このクラスは、エージェントの基本的な属性と機能を定義します：

- **属性**:
  - `name`: エージェントの名前
  - `description`: エージェントの説明
  - `config`: エージェントの設定（AgentConfig）
  - `tools`: エージェントが使用するツールのリスト
  - `system_prompt`: エージェントの動作を制御するシステムプロンプト
  - `history`: 会話の履歴

- **メソッド**:
  - `process_message(message)`: ユーザーのメッセージを処理し、応答を生成する
  - `execute_tool(tool_name, **params)`: 指定されたツールを実行する
  - `add_to_history(user_message, agent_message)`: 会話の履歴に追加する

### AgentConfig

`AgentConfig` は、エージェントの設定を管理するクラスです：

- **属性**:
  - `model_name`: 使用するモデルの名前
  - `temperature`: 生成の多様性（0.0〜1.0）
  - `max_output_tokens`: 生成される最大トークン数
  - `top_p`: 生成のランダム性を制御するパラメータ
  - `top_k`: 生成のランダム性を制御するパラメータ

### Tool

`Tool` は、エージェントが使用するツールを定義するクラスです：

- **属性**:
  - `name`: ツールの名前
  - `description`: ツールの説明
  - `function`: ツールの実行関数
  - `parameter_schema`: ツールのパラメータスキーマ（JSON Schema形式）

- **メソッド**:
  - `execute(**params)`: ツールを実行する

### Model Contexts Protocol (MCP)

`Model Contexts Protocol (MCP)` は、エージェントが複数のコンテキストを管理し、それらの間で情報を共有するためのプロトコルです：

- **主な機能**:
  - 複数のコンテキストの作成と管理
  - コンテキスト内での情報の保存と取得
  - コンテキスト間での情報の共有
  - 異なるコンテキスト間での切り替え

- **主要な関数**:
  - `create_context(name, description)`: 新しいコンテキストを作成する
  - `list_contexts()`: すべてのコンテキストのリストを取得する
  - `set_active_context(context_id)`: アクティブなコンテキストを設定する
  - `get_active_context()`: 現在アクティブなコンテキストを取得する
  - `set_context_value(key, value, context_id)`: コンテキストに値を設定する
  - `get_context_value(key, context_id)`: コンテキストから値を取得する
  - `delete_context(context_id)`: コンテキストを削除する

## デモの実行

このチュートリアルには、4つのデモが含まれています：

### 基本的なエージェントデモ

基本的なエージェントデモでは、シンプルな対話エージェントを作成し、ユーザーの質問に答える方法を示します。

### ツールを使用するエージェントデモ

ツールを使用するエージェントデモでは、外部ツール（天気情報の取得、情報検索など）を活用するエージェントを作成し、より高度なタスクを実行する方法を示します。

### コンテキスト管理を活用したエージェントデモ

コンテキスト管理を活用したエージェントデモでは、会話の文脈を維持し、一貫した対話を行うエージェントを作成する方法を示します。

### Model Contexts Protocol (MCP)を使用するエージェントデモ

Model Contexts Protocol (MCP)を使用するエージェントデモでは、複数のコンテキストを管理し、それらの間で情報を共有するエージェントを作成する方法を示します。

## コード例

### 基本的なエージェントの作成

```python
from google_adk import Agent, AgentConfig

# エージェントの設定
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
response = agent.process_message("こんにちは、あなたは何ができますか？")
print(response)
```

### ツールを使用するエージェントの作成

```python
from google_adk import Agent, AgentConfig, Tool

# 天気情報を取得するツール
def get_weather(location: str, unit: str = "celsius") -> dict:
    # 実際のAPIリクエストの代わりにシミュレーションデータを返す
    return {
        "location": location,
        "temperature": 22 if unit == "celsius" else 72,
        "condition": "晴れ",
        "humidity": 65
    }

# 天気ツールの定義
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

# エージェントの作成
agent = Agent(
    name="ツール活用アシスタント",
    description="ユーザーの質問に答え、ツールを使用してタスクを実行するアシスタントです。",
    config=AgentConfig(model_name="gemini-1.5-pro"),
    tools=[weather_tool]
)

# ツールの実行
weather_result = agent.execute_tool("get_weather", location="東京", unit="celsius")
print(weather_result)
```

### Model Contexts Protocol (MCP)を使用するエージェントの作成

```python
from google_adk import Agent, AgentConfig, Tool
from google_adk.mcp import create_context, set_context_value, get_context_value

# コンテキストの作成
travel_context = create_context(
    name="旅行プラン",
    description="旅行の計画情報を保存するコンテキスト"
)

# コンテキストに値を設定
set_context_value(
    key="destination",
    value="京都",
    context_id=travel_context['context_id']
)

# コンテキストから値を取得
destination = get_context_value(
    key="destination",
    context_id=travel_context['context_id']
)

print(f"旅行先: {destination}")

# MCPツールの作成
create_context_tool = Tool(
    name="create_context",
    description="新しいコンテキストを作成します",
    function=create_context,
    parameter_schema={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "コンテキストの名前"
            },
            "description": {
                "type": "string",
                "description": "コンテキストの説明"
            }
        },
        "required": ["name"]
    }
)

# MCPツールを使用するエージェントの作成
agent = Agent(
    name="MCPアシスタント",
    description="Model Contexts Protocol (MCP)を使用して、複数のコンテキストを管理し、情報を共有するアシスタントです。",
    config=AgentConfig(model_name="gemini-1.5-pro"),
    tools=[create_context_tool]
)
```

## 参考リソース

- [Google AI Platform](https://ai.google.dev/)
- [Google Generative AI Python SDK](https://github.com/google/generative-ai-python)
- [Gemini API Documentation](https://ai.google.dev/docs/gemini_api_overview)
