
"""
Google ADK - 基本的なエージェントの例

このサンプルでは、Google Agent Development Kit (ADK)を使用して
基本的なエージェントを作成し、対話する方法を示します。
"""

import os
import sys
import logging

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

try:
    from google_adk import Agent, AgentConfig
except ImportError:
    print(f"Error: Could not import from google_adk. Path: {parent_dir}")
    print("Make sure the google_adk package is properly installed.")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ADK-BasicAgent")

def main():
    """基本的なエージェントのデモを実行する"""
    print("Google ADK - 基本的なエージェントの例")
    
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
    
    agent = Agent(
        name="シンプルアシスタント",
        description="ユーザーの質問に答える基本的なアシスタントです。",
        config=config
    )
    
    print(f"\n===== {agent.name} との対話デモ =====")
    print(f"説明: {agent.description}")
    print("終了するには 'exit' または 'quit' と入力してください。")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\nあなた: ")
            
            if user_input.lower() in ["exit", "quit", "終了"]:
                print("デモを終了します。")
                break
            
            response = agent.process_message(user_input)
            print(f"\n{agent.name}: {response}")
        
        except KeyboardInterrupt:
            print("\nデモを終了します。")
            break
        except Exception as e:
            print(f"エラーが発生しました: {e}")


if __name__ == "__main__":
    main()
