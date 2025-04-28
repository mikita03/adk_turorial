
"""
Google Agent Development Kit (ADK) チュートリアル

このチュートリアルでは、GoogleのAgent Development Kit (ADK)を使用して
インテリジェントなエージェントを開発する方法を説明します。
ADKは、Googleの生成AIモデルを活用して、特定のタスクを実行する
エージェントを構築するためのツールキットです。

作成者: Devin AI
日付: 2025-04-28
"""

import os
import sys
import json
import argparse
import logging
from typing import Dict, List, Any, Optional, Union, Callable

try:
    import google.generativeai as genai
except ImportError:
    print("Google Generative AI ライブラリがインストールされていません。")
    print("以下のコマンドでインストールしてください：")
    print("pip install google-generativeai")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ADK-Tutorial")

class AgentConfig:
    """
    エージェントの設定を管理するクラス
    
    このクラスは、エージェントの動作を制御するための設定パラメータを保持します。
    モデル名、温度、トークン制限などの設定を管理します。
    """
    
    def __init__(
        self,
        model_name: str = "gemini-1.5-pro",
        temperature: float = 0.7,
        top_p: float = 0.95,
        top_k: int = 40,
        max_output_tokens: int = 2048,
        api_key: Optional[str] = None
    ):
        """
        AgentConfigクラスの初期化
        
        Args:
            model_name: 使用するGeminiモデルの名前
            temperature: 生成の多様性を制御するパラメータ（0.0〜1.0）
            top_p: 生成時に考慮するトークンの確率質量の割合
            top_k: 生成時に考慮するトークンの数
            max_output_tokens: 生成される最大トークン数
            api_key: Google AI APIキー（Noneの場合は環境変数から取得）
        """
        self.model_name = model_name
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.max_output_tokens = max_output_tokens
        
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            logger.warning("GOOGLE_API_KEY環境変数が設定されていません。")
            logger.warning("実際のAPIリクエストを行うには、APIキーが必要です。")
    
    def to_dict(self) -> Dict[str, Any]:
        """設定を辞書形式で返す"""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "max_output_tokens": self.max_output_tokens
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'AgentConfig':
        """辞書から設定を読み込む"""
        return cls(
            model_name=config_dict.get("model_name", "gemini-1.5-pro"),
            temperature=config_dict.get("temperature", 0.7),
            top_p=config_dict.get("top_p", 0.95),
            top_k=config_dict.get("top_k", 40),
            max_output_tokens=config_dict.get("max_output_tokens", 2048),
            api_key=config_dict.get("api_key")
        )


class Tool:
    """
    エージェントが使用できるツールを定義するクラス
    
    ツールは、エージェントが特定のタスクを実行するために使用できる
    関数やAPIなどの機能を表します。
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        function: Callable,
        parameter_schema: Dict[str, Any]
    ):
        """
        Toolクラスの初期化
        
        Args:
            name: ツールの名前
            description: ツールの説明
            function: ツールの実行時に呼び出される関数
            parameter_schema: ツールのパラメータスキーマ（JSON Schema形式）
        """
        self.name = name
        self.description = description
        self.function = function
        self.parameter_schema = parameter_schema
    
    def execute(self, **kwargs) -> Any:
        """
        ツールを実行する
        
        Args:
            **kwargs: ツールに渡すパラメータ
            
        Returns:
            ツールの実行結果
        """
        return self.function(**kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """ツール定義を辞書形式で返す"""
        return {
            "name": self.name,
            "description": self.description,
            "parameter_schema": self.parameter_schema
        }


class Agent:
    """
    Google ADKを使用したインテリジェントエージェント
    
    このクラスは、Googleの生成AIモデルを使用して、
    ユーザーの入力に応答し、タスクを実行するエージェントを表します。
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        config: AgentConfig,
        tools: Optional[List[Tool]] = None,
        system_prompt: Optional[str] = None
    ):
        """
        Agentクラスの初期化
        
        Args:
            name: エージェントの名前
            description: エージェントの説明
            config: エージェントの設定
            tools: エージェントが使用できるツールのリスト
            system_prompt: エージェントのシステムプロンプト
        """
        self.name = name
        self.description = description
        self.config = config
        self.tools = tools or []
        self.system_prompt = system_prompt or self._default_system_prompt()
        
        if self.config.api_key:
            genai.configure(api_key=self.config.api_key)
        
        self.model = genai.GenerativeModel(
            model_name=self.config.model_name,
            generation_config={
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                "top_k": self.config.top_k,
                "max_output_tokens": self.config.max_output_tokens
            }
        )
        
        self.chat_session = self.model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [self.system_prompt]
                },
                {
                    "role": "model",
                    "parts": ["了解しました。お手伝いします。"]
                }
            ]
        )
        
        logger.info(f"エージェント '{self.name}' を初期化しました")
    
    def _default_system_prompt(self) -> str:
        """デフォルトのシステムプロンプトを生成"""
        prompt = f"あなたは '{self.name}' という名前のAIアシスタントです。"
        prompt += f"\n\n{self.description}"
        
        if self.tools:
            prompt += "\n\nあなたは以下のツールを使用できます：\n"
            for tool in self.tools:
                prompt += f"- {tool.name}: {tool.description}\n"
        
        return prompt
    
    def add_tool(self, tool: Tool) -> None:
        """
        エージェントにツールを追加する
        
        Args:
            tool: 追加するツール
        """
        self.tools.append(tool)
        logger.info(f"ツール '{tool.name}' をエージェントに追加しました")
    
    def process_message(self, message: str) -> str:
        """
        ユーザーからのメッセージを処理する
        
        Args:
            message: ユーザーからのメッセージ
            
        Returns:
            エージェントの応答
        """
        try:
            response = self.chat_session.send_message(message)
            return response.text
        except Exception as e:
            logger.error(f"メッセージ処理中にエラーが発生しました: {e}")
            return f"エラーが発生しました: {e}"
    
    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """
        指定されたツールを実行する
        
        Args:
            tool_name: 実行するツールの名前
            **kwargs: ツールに渡すパラメータ
            
        Returns:
            ツールの実行結果
        """
        for tool in self.tools:
            if tool.name == tool_name:
                try:
                    result = tool.execute(**kwargs)
                    logger.info(f"ツール '{tool_name}' を実行しました")
                    return result
                except Exception as e:
                    logger.error(f"ツール '{tool_name}' の実行中にエラーが発生しました: {e}")
                    return f"エラーが発生しました: {e}"
        
        logger.warning(f"ツール '{tool_name}' が見つかりません")
        return f"ツール '{tool_name}' が見つかりません"


def get_weather(location: str, unit: str = "celsius") -> Dict[str, Any]:
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


def search_information(query: str, max_results: int = 3) -> List[Dict[str, str]]:
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


def create_sample_agent() -> Agent:
    """サンプルエージェントを作成する"""
    config = AgentConfig(
        model_name="gemini-1.5-pro",
        temperature=0.7,
        max_output_tokens=2048
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
        name="アシスタントエージェント",
        description="ユーザーの質問に答え、タスクを実行するアシスタントです。",
        config=config,
        tools=[weather_tool, search_tool]
    )
    
    return agent


def run_interactive_demo(agent: Agent) -> None:
    """
    対話型デモを実行する
    
    Args:
        agent: 使用するエージェント
    """
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


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="Google Agent Development Kit (ADK) チュートリアル")
    parser.add_argument("--demo", action="store_true", help="対話型デモを実行する")
    parser.add_argument("--verbose", action="store_true", help="詳細なログを表示する")
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    print("Google Agent Development Kit (ADK) チュートリアルへようこそ！")
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("\n警告: GOOGLE_API_KEY環境変数が設定されていません。")
        print("実際のAPIリクエストを行うには、APIキーが必要です。")
        print("APIキーを取得するには、https://ai.google.dev/ にアクセスしてください。")
        print("APIキーを取得したら、以下のコマンドで環境変数を設定してください：")
        print("export GOOGLE_API_KEY='あなたのAPIキー'")
        print("\nAPIキーなしでデモを続行します（シミュレーションモード）。\n")
    
    agent = create_sample_agent()
    
    if args.demo:
        run_interactive_demo(agent)
    else:
        print("\nデモを実行するには --demo オプションを指定してください。")
        print("例: python adk_tutorial.py --demo")
        print("\nヘルプを表示するには --help オプションを指定してください。")
        print("例: python adk_tutorial.py --help")


if __name__ == "__main__":
    main()
