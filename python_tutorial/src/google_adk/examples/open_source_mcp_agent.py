"""
Google ADK - オープンソースMCP実装（lastmile-ai/mcp-agent）を使用するエージェントの例

このサンプルでは、Google Agent Development Kit (ADK)と人気のあるオープンソースMCP実装である
lastmile-ai/mcp-agentを組み合わせて使用する方法を示します。
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any, List, Optional

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

try:
    from google_adk import Agent as ADKAgent, AgentConfig, Tool
    
    from mcp_agent.app import MCPApp
    from mcp_agent.config import (
        GoogleSettings,
        Settings,
        LoggerSettings,
        MCPSettings,
        MCPServerSettings
    )
    from mcp_agent.agents.agent import Agent as MCPAgent
    from mcp_agent.workflows.llm.augmented_llm_google import GoogleAugmentedLLM
except ImportError as e:
    print(f"Error: Could not import required modules. {e}")
    print("Make sure the google_adk and mcp-agent packages are properly installed.")
    print("Install with: pip install -e .")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ADK-OpenSourceMCP")

class WebSearchResult:
    """検索結果を表すクラス"""
    title: str
    url: str
    snippet: str
    
    def __init__(self, title: str, url: str, snippet: str):
        self.title = title
        self.url = url
        self.snippet = snippet

def simulate_web_search(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """
    Webでの検索をシミュレートする関数
    
    Args:
        query: 検索クエリ
        max_results: 返す結果の最大数
        
    Returns:
        検索結果のリスト
    """
    results = [
        {
            "title": f"{query}に関する情報 1",
            "url": f"https://example.com/info1?q={query}",
            "snippet": f"{query}についての詳細な情報が含まれています。"
        },
        {
            "title": f"{query}の使い方ガイド",
            "url": f"https://example.com/guide?q={query}",
            "snippet": f"{query}の使用方法について説明しています。"
        },
        {
            "title": f"{query}に関するよくある質問",
            "url": f"https://example.com/faq?q={query}",
            "snippet": f"{query}についてのよくある質問と回答です。"
        },
        {
            "title": f"{query}の最新情報",
            "url": f"https://example.com/news?q={query}",
            "snippet": f"{query}に関する最新のニュースと更新情報です。"
        }
    ]
    return results[:max_results]

async def setup_mcp_agent() -> MCPAgent:
    """
    lastmile-ai/mcp-agentを使用したエージェントをセットアップする
    
    Returns:
        設定されたMCPエージェント
    """
    settings = Settings(
        execution_engine="asyncio",
        logger=LoggerSettings(type="file", level="debug"),
        mcp=MCPSettings(
            servers={
                "fetch": MCPServerSettings(
                    command="uvx",
                    args=["mcp-server-fetch"],
                )
            }
        )
    )
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        logger.warning("GOOGLE_API_KEY環境変数が設定されていません。シミュレーションモードで実行します。")
    
    app = MCPApp(settings=settings)
    
    llm = GoogleAugmentedLLM(
        model="gemini-1.5-pro",
        api_key=api_key or "dummy_api_key",
        temperature=0.7,
        max_output_tokens=1024
    )
    
    agent = MCPAgent(
        name="Finder",
        description="情報を検索して要約するエージェント",
        llm=llm
    )
    
    return agent

async def run_mcp_agent_example():
    """lastmile-ai/mcp-agentを使用した例を実行する"""
    print("Google ADK - オープンソースMCP実装（lastmile-ai/mcp-agent）を使用するエージェントの例")
    
    try:
        mcp_agent = await setup_mcp_agent()
        print(f"\nMCPエージェント '{mcp_agent.name}' を設定しました")
        print(f"説明: {mcp_agent.description}")
        
        query = "人工知能の最新トレンド"
        print(f"\n検索クエリ: '{query}'")
        
        search_results = simulate_web_search(query)
        print("\n検索結果:")
        for i, result in enumerate(search_results, 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   概要: {result['snippet']}")
        
        print("\nMCPエージェントを使用して検索結果を要約しています...")
        
        if os.environ.get("GOOGLE_API_KEY"):
            prompt = f"""
            以下の検索結果を要約してください:
            
            {search_results}
            
            要約は3つの重要なポイントを含め、200文字以内にしてください。
            """
            
            summary = "シミュレーションモード: 人工知能の最新トレンドには、(1)大規模言語モデルの進化、(2)マルチモーダルAIの発展、(3)エッジAIの普及が含まれます。これらのトレンドは様々な産業に革新をもたらし、AIの実用性と普及を加速させています。"
        else:
            summary = "シミュレーションモード: 人工知能の最新トレンドには、(1)大規模言語モデルの進化、(2)マルチモーダルAIの発展、(3)エッジAIの普及が含まれます。これらのトレンドは様々な産業に革新をもたらし、AIの実用性と普及を加速させています。"
        
        print(f"\nMCPエージェントによる要約:\n{summary}")
        
        print("\nGoogle ADKとlastmile-ai/mcp-agentの統合例:")
        
        config = AgentConfig(
            model_name="gemini-1.5-pro",
            temperature=0.7,
            max_output_tokens=1024
        )
        
        search_tool = Tool(
            name="search_with_mcp",
            description="MCPを使用して情報を検索し、要約します",
            function=lambda query, max_results=3: {
                "query": query,
                "results": simulate_web_search(query, max_results),
                "summary": f"シミュレーションモード: {query}に関する主要な情報をまとめると、(1)最新の開発動向、(2)一般的な使用方法、(3)よくある問題と解決策が重要です。詳細は検索結果を参照してください。"
            },
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
        
        adk_agent = ADKAgent(
            name="ADK-MCPアシスタント",
            description="Google ADKとlastmile-ai/mcp-agentを統合したアシスタント",
            config=config,
            tools=[search_tool]
        )
        
        print(f"\nADKエージェント '{adk_agent.name}' を設定しました")
        print(f"説明: {adk_agent.description}")
        
        print("\nADKエージェントを使用して検索を実行しています...")
        search_query = "量子コンピューティング"
        
        result = adk_agent.execute_tool("search_with_mcp", query=search_query)
        
        print(f"\n検索クエリ: '{search_query}'")
        print("\n検索結果:")
        for i, res in enumerate(result["results"], 1):
            print(f"{i}. {res['title']}")
            print(f"   URL: {res['url']}")
            print(f"   概要: {res['snippet']}")
        
        print(f"\n要約:\n{result['summary']}")
        
        print("\nlastmile-ai/mcp-agentとGoogle ADKの統合デモが完了しました")
        
    except Exception as e:
        logger.error(f"MCPエージェントの実行中にエラーが発生しました: {e}")
        print(f"エラーが発生しました: {e}")
        print("APIキーが設定されていない場合は、環境変数GOOGLE_API_KEYを設定してください。")
        print("export GOOGLE_API_KEY='あなたのAPIキー'")

def main():
    """メイン関数"""
    try:
        asyncio.run(run_mcp_agent_example())
    except KeyboardInterrupt:
        print("\nデモを終了します。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
