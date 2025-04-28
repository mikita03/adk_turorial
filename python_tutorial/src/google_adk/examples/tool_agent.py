
"""
Google ADK - ツールを使用するエージェントの例

このサンプルでは、Google Agent Development Kit (ADK)を使用して
ツールを活用するエージェントを作成し、対話する方法を示します。
"""

import os
import sys
import json
import logging

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

try:
    from google_adk import Agent, AgentConfig, Tool
except ImportError:
    print(f"Error: Could not import from google_adk. Path: {parent_dir}")
    print("Make sure the google_adk package is properly installed.")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ADK-ToolAgent")

def get_weather(location: str, unit: str = "celsius") -> dict:
    """
    指定された場所の天気情報を取得する（シミュレーション）
    
    Args:
        location: 天気を取得する場所
        unit: 温度の単位（celsius または fahrenheit）
        
    Returns:
        天気情報を含む辞書
    """
    weather_data = {
        "location": location,
        "temperature": 22 if unit == "celsius" else 72,
        "unit": unit,
        "condition": "晴れ",
        "humidity": 65,
        "wind_speed": 10
    }
    return weather_data


def search_information(query: str, max_results: int = 3) -> list:
    """
    指定されたクエリに関する情報を検索する（シミュレーション）
    
    Args:
        query: 検索クエリ
        max_results: 返す結果の最大数
        
    Returns:
        検索結果のリスト
    """
    results = [
        {
            "title": f"{query}に関する情報 1",
            "snippet": f"{query}についての詳細な情報が含まれています。",
            "url": f"https://example.com/info1?q={query}"
        },
        {
            "title": f"{query}の使い方ガイド",
            "snippet": f"{query}の使用方法について説明しています。",
            "url": f"https://example.com/guide?q={query}"
        },
        {
            "title": f"{query}に関するよくある質問",
            "snippet": f"{query}についてのよくある質問と回答です。",
            "url": f"https://example.com/faq?q={query}"
        },
        {
            "title": f"{query}の最新情報",
            "snippet": f"{query}に関する最新のニュースと更新情報です。",
            "url": f"https://example.com/news?q={query}"
        }
    ]
    return results[:max_results]


def main():
    """ツールを使用するエージェントのデモを実行する"""
    print("Google ADK - ツールを使用するエージェントの例")
    
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
    
    print(f"\n===== {agent.name} との対話デモ =====")
    print(f"説明: {agent.description}")
    print("終了するには 'exit' または 'quit' と入力してください。")
    print("ツールを実行するには 'tool:ツール名 パラメータ1=値1 パラメータ2=値2...' と入力してください。")
    print("例: tool:get_weather location=東京 unit=celsius")
    print("=" * 50)
    
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
