
"""
Google Agent Development Kit (ADK) チュートリアル

このスクリプトは、Google ADKを使用してインテリジェントなエージェントを
開発する方法を示すメインチュートリアルです。
"""

import os
import sys
import argparse
import logging
import json
from typing import Dict, Any, List, Optional, Union

try:
    from google_adk import Agent, AgentConfig, Tool, get_weather, search_information, create_sample_agent
    from google_adk.mcp import (
        create_context, list_contexts, set_active_context, get_active_context,
        set_context_value, get_context_value, delete_context
    )
except ImportError:
    print("Error: Could not import from google_adk.")
    print("Make sure the google_adk package is properly installed.")
    print("Run: pip install -e . from the python_tutorial directory")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ADK-Tutorial")

def check_api_key() -> bool:
    """
    Google API Keyが設定されているかチェックする
    
    Returns:
        bool: APIキーが設定されている場合はTrue、そうでない場合はFalse
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        logger.warning("GOOGLE_API_KEY環境変数が設定されていません。")
        logger.warning("実際のAPIリクエストを行うには、APIキーが必要です。")
        print("\n警告: GOOGLE_API_KEY環境変数が設定されていません。")
        print("実際のAPIリクエストを行うには、APIキーが必要です。")
        print("APIキーを取得するには、https://ai.google.dev/ にアクセスしてください。")
        print("APIキーを取得したら、以下のコマンドで環境変数を設定してください：")
        print("export GOOGLE_API_KEY='あなたのAPIキー'")
        print("\nAPIキーなしでデモを続行します（シミュレーションモード）。\n")
        return False
    return True

def run_basic_agent_demo():
    """基本的なエージェントのデモを実行する"""
    print("\n===== 基本的なエージェントのデモ =====")
    
    has_api_key = check_api_key()
    
    config = AgentConfig(
        model_name="gemini-1.5-pro",  # 使用するモデル
        temperature=0.7,              # 生成の多様性（0.0〜1.0）
        max_output_tokens=1024        # 生成される最大トークン数
    )
    
    agent = Agent(
        name="シンプルアシスタント",
        description="ユーザーの質問に答える基本的なアシスタントです。",
        config=config
    )
    
    print(f"\nエージェント '{agent.name}' を作成しました。")
    print(f"説明: {agent.description}")
    print(f"モデル: {config.model_name}")
    print(f"温度: {config.temperature}")
    print(f"最大出力トークン: {config.max_output_tokens}")
    
    print("\n対話の例:")
    
    example_messages = [
        "こんにちは、あなたは何ができますか？",
        "東京の観光スポットを教えてください",
        "ありがとう、それでは終了します"
    ]
    
    for message in example_messages:
        print(f"\nユーザー: {message}")
        try:
            if has_api_key:
                response = agent.process_message(message)
                print(f"{agent.name}: {response}")
            else:
                print(f"{agent.name}: [シミュレーションモード] ユーザーの質問に対する応答をここに生成します。")
        except Exception as e:
            print(f"エラーが発生しました: {e}")
    
    print("\n基本的なエージェントのデモが完了しました。")
    print("詳細な実装は examples/basic_agent.py を参照してください。")

def run_tool_agent_demo():
    """ツールを使用するエージェントのデモを実行する"""
    print("\n===== ツールを使用するエージェントのデモ =====")
    
    has_api_key = check_api_key()
    
    config = AgentConfig(
        model_name="gemini-1.5-pro",
        temperature=0.7,
        max_output_tokens=1024
    )
    
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
    
    search_tool = Tool(
        name="search_information",
        description="指定されたクエリに関する情報を検索します",
        function=search_information,
        parameter_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "検索クエリ"
                },
                "max_results": {
                    "type": "integer",
                    "description": "返す結果の最大数",
                    "minimum": 1,
                    "maximum": 10
                }
            },
            "required": ["query"]
        }
    )
    
    agent = Agent(
        name="ツール活用アシスタント",
        description="ユーザーの質問に答え、ツールを使用してタスクを実行するアシスタントです。",
        config=config,
        tools=[weather_tool, search_tool]
    )
    
    print(f"\nエージェント '{agent.name}' を作成しました。")
    print(f"説明: {agent.description}")
    print("\n利用可能なツール:")
    for tool in agent.tools:
        print(f"- {tool.name}: {tool.description}")
    
    print("\nツール実行の例:")
    
    print("\n1. 天気情報の取得:")
    location = "東京"
    unit = "celsius"
    print(f"パラメータ: location={location}, unit={unit}")
    
    try:
        weather_result = agent.execute_tool("get_weather", location=location, unit=unit)
        print("結果:")
        print(json.dumps(weather_result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    
    print("\n2. 情報検索:")
    query = "Google ADK"
    max_results = 2
    print(f"パラメータ: query='{query}', max_results={max_results}")
    
    try:
        search_result = agent.execute_tool("search_information", query=query, max_results=max_results)
        print("結果:")
        print(json.dumps(search_result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    
    print("\nツールを使用するエージェントのデモが完了しました。")
    print("詳細な実装は examples/tool_agent.py を参照してください。")

def run_context_agent_demo():
    """コンテキスト管理を活用したエージェントのデモを実行する"""
    print("\n===== コンテキスト管理を活用したエージェントのデモ =====")
    
    has_api_key = check_api_key()
    
    config = AgentConfig(
        model_name="gemini-1.5-pro",
        temperature=0.7,
        max_output_tokens=1024
    )
    
    agent = Agent(
        name="コンテキスト対応アシスタント",
        description="会話の文脈を理解し、一貫した対話を行うアシスタントです。",
        config=config,
        system_prompt="""
        あなたは会話の文脈を理解し、一貫した対話を行うアシスタントです。
        ユーザーが前の会話を参照する場合（例：「それ」「そこ」「その人」などの指示語を使用する場合）、
        会話の履歴を考慮して適切に応答してください。
        """
    )
    
    print(f"\nエージェント '{agent.name}' を作成しました。")
    print(f"説明: {agent.description}")
    print("このデモでは、エージェントが会話の文脈をどのように維持するかを示します。")
    
    print("\n対話の例:")
    
    conversation_examples = [
        ("東京の観光スポットを3つ教えて", "東京の主要な観光スポットには、東京スカイツリー、浅草寺、東京ディズニーリゾートなどがあります。"),
        ("その中で一番人気なのはどこ？", "東京ディズニーリゾートが最も人気があります。年間約3000万人の来場者があり、東京を訪れる観光客に非常に人気があります。"),
        ("そこへの行き方を教えて", "東京ディズニーリゾートへは、JR京葉線の「舞浜駅」で下車し、徒歩約5分です。東京駅から電車で約15分かかります。"),
    ]
    
    for i, (user_msg, agent_msg) in enumerate(conversation_examples):
        print(f"\nユーザー: {user_msg}")
        
        if i > 0:
            print("（前の会話を参照しています）")
        
        print(f"{agent.name}: {agent_msg}")
        
        if has_api_key and i < len(conversation_examples) - 1:
            agent.add_to_history(user_msg, agent_msg)
    
    print("\nコンテキスト管理を活用したエージェントのデモが完了しました。")
    print("詳細な実装は examples/context_agent.py を参照してください。")

def run_mcp_agent_demo():
    """Model Contexts Protocol (MCP)を使用するエージェントのデモを実行する"""
    print("\n===== Model Contexts Protocol (MCP)を使用するエージェントのデモ =====")
    
    has_api_key = check_api_key()
    
    config = AgentConfig(
        model_name="gemini-1.5-pro",
        temperature=0.7,
        max_output_tokens=1024
    )
    
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
    
    list_contexts_tool = Tool(
        name="list_contexts",
        description="すべてのコンテキストのリストを取得します",
        function=list_contexts,
        parameter_schema={
            "type": "object",
            "properties": {}
        }
    )
    
    set_context_value_tool = Tool(
        name="set_context_value",
        description="コンテキストに値を設定します",
        function=set_context_value,
        parameter_schema={
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "値のキー"
                },
                "value": {
                    "description": "設定する値"
                },
                "context_id": {
                    "type": "string",
                    "description": "値を設定するコンテキストのID（指定しない場合はアクティブなコンテキスト）"
                }
            },
            "required": ["key", "value"]
        }
    )
    
    get_context_value_tool = Tool(
        name="get_context_value",
        description="コンテキストから値を取得します",
        function=get_context_value,
        parameter_schema={
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "値のキー"
                },
                "context_id": {
                    "type": "string",
                    "description": "値を取得するコンテキストのID（指定しない場合はアクティブなコンテキスト）"
                }
            },
            "required": ["key"]
        }
    )
    
    agent = Agent(
        name="MCPアシスタント",
        description="Model Contexts Protocol (MCP)を使用して、複数のコンテキストを管理し、情報を共有するアシスタントです。",
        config=config,
        tools=[
            create_context_tool,
            list_contexts_tool,
            set_context_value_tool,
            get_context_value_tool
        ]
    )
    
    print(f"\nエージェント '{agent.name}' を作成しました。")
    print(f"説明: {agent.description}")
    print("\n利用可能なMCPツール:")
    for tool in agent.tools:
        print(f"- {tool.name}: {tool.description}")
    
    print("\nModel Contexts Protocol (MCP)とは:")
    print("MCPは、エージェントが複数のコンテキストを管理し、それらの間で情報を共有するための")
    print("プロトコルです。これにより、エージェントはより複雑なタスクを実行し、長期的な会話や")
    print("マルチステップのタスクをより効果的に管理できるようになります。")
    
    print("\nMCPの主な機能:")
    print("- 複数のコンテキストの作成と管理")
    print("- コンテキスト内での情報の保存と取得")
    print("- コンテキスト間での情報の共有")
    print("- 異なるコンテキスト間での切り替え")
    
    print("\nMCPの使用例:")
    
    print("\n1. 新しいコンテキストの作成:")
    context_name = "旅行プラン"
    context_description = "旅行の計画情報を保存するコンテキスト"
    print(f"パラメータ: name='{context_name}', description='{context_description}'")
    
    try:
        context_result = agent.execute_tool("create_context", name=context_name, description=context_description)
        print("結果:")
        print(json.dumps(context_result, ensure_ascii=False, indent=2))
        context_id = context_result.get("context_id")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        context_id = None
    
    if context_id:
        print("\n2. コンテキストに値を設定:")
        key = "destination"
        value = "京都"
        print(f"パラメータ: key='{key}', value='{value}', context_id='{context_id}'")
        
        try:
            set_result = agent.execute_tool("set_context_value", key=key, value=value, context_id=context_id)
            print("結果:")
            print(json.dumps(set_result, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"エラーが発生しました: {e}")
        
        print("\n3. コンテキストから値を取得:")
        print(f"パラメータ: key='{key}', context_id='{context_id}'")
        
        try:
            get_result = agent.execute_tool("get_context_value", key=key, context_id=context_id)
            print("結果:")
            print(json.dumps(get_result, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"エラーが発生しました: {e}")
    
    print("\n4. すべてのコンテキストのリストを取得:")
    
    try:
        list_result = agent.execute_tool("list_contexts")
        print("結果:")
        print(json.dumps(list_result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    
    print("\nModel Contexts Protocol (MCP)を使用するエージェントのデモが完了しました。")
    print("詳細な実装は examples/mcp_agent.py を参照してください。")

def main():
    """メインチュートリアルを実行する"""
    parser = argparse.ArgumentParser(description="Google Agent Development Kit (ADK) チュートリアル")
    parser.add_argument("--demo", choices=["basic", "tool", "context", "mcp", "all"], default="all",
                        help="実行するデモを指定します（basic: 基本的なエージェント, tool: ツールを使用するエージェント, context: コンテキスト管理を活用したエージェント, mcp: Model Contexts Protocol (MCP)を使用するエージェント, all: すべて）")
    parser.add_argument("--verbose", action="store_true", help="詳細なログを表示します")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print("=" * 80)
    print("Google Agent Development Kit (ADK) チュートリアル")
    print("=" * 80)
    print("\nこのチュートリアルでは、GoogleのAgent Development Kit (ADK)を使用して")
    print("インテリジェントなエージェントを開発する方法を示します。")
    print("\nADKの主な特徴:")
    print("- 自然言語理解: ユーザーの入力を理解し、適切な応答を生成")
    print("- ツール統合: 外部APIやサービスと連携して情報を取得・処理")
    print("- コンテキスト管理: 会話の文脈を維持し、一貫した対話を実現")
    print("- Model Contexts Protocol (MCP): 複数のコンテキストを管理し、情報を共有")
    print("- カスタマイズ可能: 特定のドメインやタスクに特化したエージェントを構築可能")
    print("- マルチモーダル対応: テキスト、画像、音声などの複数のモダリティを処理可能")
    
    if args.demo in ["basic", "all"]:
        run_basic_agent_demo()
    
    if args.demo in ["tool", "all"]:
        run_tool_agent_demo()
    
    if args.demo in ["context", "all"]:
        run_context_agent_demo()
    
    if args.demo in ["mcp", "all"]:
        run_mcp_agent_demo()
    
    print("\n" + "=" * 80)
    print("チュートリアルが完了しました。")
    print("詳細な情報は README.md を参照してください。")
    print("=" * 80)


if __name__ == "__main__":
    main()
