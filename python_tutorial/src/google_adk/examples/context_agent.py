
"""
Google ADK - コンテキスト管理を活用したエージェントの例

このサンプルでは、Google Agent Development Kit (ADK)を使用して
会話のコンテキストを維持するエージェントを作成し、対話する方法を示します。
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
logger = logging.getLogger("ADK-ContextAgent")

def main():
    """コンテキスト管理を活用したエージェントのデモを実行する"""
    print("Google ADK - コンテキスト管理を活用したエージェントの例")
    
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
        name="コンテキスト対応アシスタント",
        description="会話の文脈を理解し、一貫した対話を行うアシスタントです。",
        config=config,
        system_prompt="""
        あなたは会話の文脈を理解し、一貫した対話を行うアシスタントです。
        ユーザーが前の会話を参照する場合（例：「それ」「そこ」「その人」などの指示語を使用する場合）、
        会話の履歴を考慮して適切に応答してください。
        
        例えば：
        ユーザー: 「東京の天気を教えて」
        あなた: 「東京の天気は晴れです。気温は22度です。」
        ユーザー: 「明日はどう？」
        あなた: 「明日の東京の天気は曇りの予報です。気温は20度になる見込みです。」
        
        このように、「明日はどう？」という質問に対して、前の会話で話題になった「東京の天気」について
        回答することができます。
        """
    )
    
    print(f"\n===== {agent.name} との対話デモ =====")
    print(f"説明: {agent.description}")
    print("このデモでは、エージェントが会話の文脈をどのように維持するかを示します。")
    print("指示語（それ、そこ、その人など）を使って、前の会話を参照してみてください。")
    print("終了するには 'exit' または 'quit' と入力してください。")
    print("=" * 50)
    
    conversation_examples = [
        ("東京の観光スポットを3つ教えて", "東京の主要な観光スポットには、東京スカイツリー、浅草寺、東京ディズニーリゾートなどがあります。"),
        ("その中で一番人気なのはどこ？", "東京ディズニーリゾートが最も人気があります。年間約3000万人の来場者があり、東京を訪れる観光客に非常に人気があります。"),
        ("そこへの行き方を教えて", "東京ディズニーリゾートへは、JR京葉線の「舞浜駅」で下車し、徒歩約5分です。東京駅から電車で約15分かかります。"),
    ]
    
    print("\n会話例：")
    for i, (user_msg, agent_msg) in enumerate(conversation_examples):
        print(f"\nあなた: {user_msg}")
        print(f"{agent.name}: {agent_msg}")
    
    print("\n実際に対話してみましょう：")
    
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
