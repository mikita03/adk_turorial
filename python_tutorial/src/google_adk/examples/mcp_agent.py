"""
Google ADK - Model Contexts Protocol (MCP)を使用するエージェントの例

このサンプルでは、Google Agent Development Kit (ADK)とModel Contexts Protocol (MCP)を
組み合わせて使用する方法を示します。MCPを使用することで、エージェントは複数のコンテキストを
管理し、それらの間で情報を共有することができます。
"""

import os
import sys
import json
import logging

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

try:
    from google_adk import Agent, AgentConfig, Tool
    from google_adk.mcp import (
        create_context,
        list_contexts,
        set_active_context,
        get_active_context,
        set_context_value,
        get_context_value,
        delete_context
    )
except ImportError:
    print(f"Error: Could not import from google_adk. Path: {parent_dir}")
    print("Make sure the google_adk package is properly installed.")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ADK-MCPAgent")

def main():
    """MCPを使用するエージェントのデモを実行する"""
    print("Google ADK - Model Contexts Protocol (MCP)を使用するエージェントの例")
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("\n警告: GOOGLE_API_KEY環境変数が設定されていません。")
        print("実際のAPIリクエストを行うには、APIキーが必要です。")
        print("APIキーを取得するには、https://ai.google.dev/ にアクセスしてください。")
        print("APIキーを取得したら、以下のコマンドで環境変数を設定してください：")
        print("export GOOGLE_API_KEY='あなたのAPIキー'")
        print("\nAPIキーなしでデモを続行します（シミュレーションモード）。\n")
    
    config = AgentConfig(
        model_name="gemini-1.5-pro",  # 使用するモデル
        temperature=0.7,              # 生成の多様性（0.0〜1.0）
        max_output_tokens=1024        # 生成される最大トークン数
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
                },
                "metadata": {
                    "type": "object",
                    "description": "コンテキストに関連するメタデータ"
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
    
    set_active_context_tool = Tool(
        name="set_active_context",
        description="アクティブなコンテキストを設定します",
        function=set_active_context,
        parameter_schema={
            "type": "object",
            "properties": {
                "context_id": {
                    "type": "string",
                    "description": "アクティブにするコンテキストのID"
                }
            },
            "required": ["context_id"]
        }
    )
    
    get_active_context_tool = Tool(
        name="get_active_context",
        description="現在アクティブなコンテキストを取得します",
        function=get_active_context,
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
    
    delete_context_tool = Tool(
        name="delete_context",
        description="コンテキストを削除します",
        function=delete_context,
        parameter_schema={
            "type": "object",
            "properties": {
                "context_id": {
                    "type": "string",
                    "description": "削除するコンテキストのID"
                }
            },
            "required": ["context_id"]
        }
    )
    
    agent = Agent(
        name="MCPアシスタント",
        description="Model Contexts Protocol (MCP)を使用して、複数のコンテキストを管理し、情報を共有するアシスタントです。",
        config=config,
        tools=[
            create_context_tool,
            list_contexts_tool,
            set_active_context_tool,
            get_active_context_tool,
            set_context_value_tool,
            get_context_value_tool,
            delete_context_tool
        ],
        system_prompt="""
        あなたはModel Contexts Protocol (MCP)を使用するアシスタントです。
        MCPを使用して、複数のコンテキストを管理し、それらの間で情報を共有することができます。
        
        以下のMCP機能を使用できます：
        - create_context: 新しいコンテキストを作成する
        - list_contexts: すべてのコンテキストのリストを取得する
        - set_active_context: アクティブなコンテキストを設定する
        - get_active_context: 現在アクティブなコンテキストを取得する
        - set_context_value: コンテキストに値を設定する
        - get_context_value: コンテキストから値を取得する
        - delete_context: コンテキストを削除する
        
        ユーザーがコンテキストの管理や情報の保存・取得を行いたい場合は、
        適切なMCPツールを使用して対応してください。
        """
    )
    
    print(f"\n===== {agent.name} との対話デモ =====")
    print(f"説明: {agent.description}")
    print("このデモでは、Model Contexts Protocol (MCP)を使用して、")
    print("複数のコンテキストを管理し、それらの間で情報を共有する方法を示します。")
    print("終了するには 'exit' または 'quit' と入力してください。")
    print("MCPツールを直接実行するには 'tool:ツール名 パラメータ1=値1 パラメータ2=値2...' と入力してください。")
    print("例: tool:create_context name=旅行プラン description=旅行の計画情報")
    print("=" * 50)
    
    print("\nデモ用のコンテキストを作成しています...")
    
    travel_context = create_context(
        name="旅行プラン",
        description="旅行の計画情報を保存するコンテキスト"
    )
    print(f"コンテキスト '{travel_context['name']}' を作成しました (ID: {travel_context['context_id']})")
    
    set_context_value(
        key="destination",
        value="京都",
        context_id=travel_context['context_id']
    )
    set_context_value(
        key="duration",
        value="3日間",
        context_id=travel_context['context_id']
    )
    set_context_value(
        key="budget",
        value=50000,
        context_id=travel_context['context_id']
    )
    
    work_context = create_context(
        name="仕事",
        description="仕事関連の情報を保存するコンテキスト"
    )
    print(f"コンテキスト '{work_context['name']}' を作成しました (ID: {work_context['context_id']})")
    
    set_context_value(
        key="project",
        value="AIアシスタント開発",
        context_id=work_context['context_id']
    )
    set_context_value(
        key="deadline",
        value="2025-05-15",
        context_id=work_context['context_id']
    )
    
    shopping_context = create_context(
        name="買い物リスト",
        description="買い物リストを保存するコンテキスト"
    )
    print(f"コンテキスト '{shopping_context['name']}' を作成しました (ID: {shopping_context['context_id']})")
    
    set_context_value(
        key="items",
        value=["牛乳", "卵", "パン", "野菜", "果物"],
        context_id=shopping_context['context_id']
    )
    
    set_active_context(travel_context['context_id'])
    print(f"コンテキスト '{travel_context['name']}' をアクティブに設定しました")
    
    print("\n利用可能なコンテキスト:")
    contexts = list_contexts()
    for ctx in contexts:
        active_mark = "✓" if ctx["is_active"] else " "
        print(f"[{active_mark}] {ctx['name']} (ID: {ctx['context_id']}): {ctx['description']}")
    
    print("\n対話を開始します...")
    
    while True:
        try:
            user_input = input("\nあなた: ")
            
            if user_input.lower() in ["exit", "quit", "終了"]:
                print("デモを終了します。")
                break
            
            if user_input.startswith("tool:"):
                parts = user_input[5:].strip().split()
                if not parts:
                    print("エラー: ツール名が指定されていません。")
                    continue
                
                tool_name = parts[0]
                params = {}
                
                for param in parts[1:]:
                    if "=" in param:
                        key, value = param.split("=", 1)
                        if value.isdigit():
                            value = int(value)
                        elif value.replace(".", "", 1).isdigit() and value.count(".") <= 1:
                            value = float(value)
                        params[key] = value
                
                result = agent.execute_tool(tool_name, **params)
                print(f"\n{agent.name}: ツール実行結果:")
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                response = agent.process_message(user_input)
                print(f"\n{agent.name}: {response}")
        
        except KeyboardInterrupt:
            print("\nデモを終了します。")
            break
        except Exception as e:
            print(f"エラーが発生しました: {e}")


if __name__ == "__main__":
    main()
