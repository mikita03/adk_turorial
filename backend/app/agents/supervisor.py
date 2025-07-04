import logging
from typing import Dict, Any, List
from langgraph.graph import StateGraph, MessagesState
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
import asyncio

from ..schemas.email import EmailContent, AgentResponse

logger = logging.getLogger(__name__)

class SupervisorAgent:
    def __init__(self, llm_model: str = "gpt-4"):
        logger.info(f"Initializing SupervisorAgent with model: {llm_model}")
        try:
            self.llm = ChatOpenAI(model=llm_model, temperature=0.1)
            logger.info("SupervisorAgent ChatOpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SupervisorAgent ChatOpenAI: {e}")
            raise
        self.role = """
        あなたはメール秘書システムの統括マネージャーです。
        受信したメールを分析し、適切な専門エージェントに作業を振り分けます。
        各エージェントからの結果を統合し、最終的な判断を行います。
        """
    
    async def route_email(self, email: EmailContent) -> Dict[str, Any]:
        """Determine which agents should process the email"""
        
        routing_prompt = f"""
        以下のメールを分析し、どのエージェントに処理を依頼すべきか判断してください。

        メール情報:
        - 送信者: {email.from_email}
        - 件名: {email.subject}
        - 本文: {email.body[:500]}...
        - 添付ファイル: {len(email.attachments) > 0}

        利用可能なエージェント:
        1. analyzer: メール要約・分類・優先度判定
        2. responder: 返信案作成・日程調整
        3. manager: 添付ファイル管理・フォルダ振り分け

        以下のJSON形式で回答してください:
        {{
            "agents_to_use": ["analyzer", "responder"],
            "priority": "urgent|normal|fyi",
            "reasoning": "判断理由",
            "parallel_execution": true
        }}
        """
        
        response = await self.llm.ainvoke([HumanMessage(content=routing_prompt)])
        
        try:
            import json
            routing_decision = json.loads(response.content)
            return routing_decision
        except:
            return {
                "agents_to_use": ["analyzer"],
                "priority": "normal",
                "reasoning": "デフォルトルーティング",
                "parallel_execution": False
            }
    
    async def coordinate_agents(self, email: EmailContent, routing_decision: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate multiple agents to process the email"""
        
        results = {}
        agents_to_use = routing_decision.get("agents_to_use", ["analyzer"])
        
        from .analyzer import AnalyzerAgent
        from .responder import ResponderAgent
        from .manager import ManagerAgent
        
        agent_instances = {
            "analyzer": AnalyzerAgent(),
            "responder": ResponderAgent(),
            "manager": ManagerAgent()
        }
        
        if routing_decision.get("parallel_execution", False):
            tasks = []
            for agent_name in agents_to_use:
                if agent_name in agent_instances:
                    agent = agent_instances[agent_name]
                    if agent_name == "analyzer":
                        tasks.append(agent.analyze_email(email))
                    elif agent_name == "responder":
                        tasks.append(agent.generate_reply(email))
                    elif agent_name == "manager":
                        tasks.append(agent.manage_attachments(email))
            
            agent_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, agent_name in enumerate(agents_to_use):
                if isinstance(agent_results[i], Exception):
                    results[agent_name] = {
                        "success": False,
                        "error": str(agent_results[i])
                    }
                else:
                    results[agent_name] = agent_results[i]
        else:
            for agent_name in agents_to_use:
                if agent_name in agent_instances:
                    agent = agent_instances[agent_name]
                    try:
                        if agent_name == "analyzer":
                            result = await agent.analyze_email(email)
                        elif agent_name == "responder":
                            result = await agent.generate_reply(email)
                        elif agent_name == "manager":
                            result = await agent.manage_attachments(email)
                        
                        results[agent_name] = result
                    except Exception as e:
                        results[agent_name] = {
                            "success": False,
                            "error": str(e)
                        }
        
        return {
            "routing_decision": routing_decision,
            "agent_results": results,
            "final_recommendation": await self._generate_final_recommendation(email, results)
        }
    
    async def _generate_final_recommendation(self, email: EmailContent, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final recommendation based on all agent results"""
        
        summary_prompt = f"""
        以下のエージェント処理結果を統合し、最終的な推奨アクションを決定してください。

        メール: {email.subject}
        エージェント結果: {agent_results}

        以下のJSON形式で回答してください:
        {{
            "recommended_actions": ["reply", "file", "schedule"],
            "priority_level": "urgent|normal|fyi",
            "summary": "3行以内の要約",
            "next_steps": "推奨される次のステップ"
        }}
        """
        
        response = await self.llm.ainvoke([HumanMessage(content=summary_prompt)])
        
        try:
            import json
            return json.loads(response.content)
        except:
            return {
                "recommended_actions": ["review"],
                "priority_level": "normal",
                "summary": "メールの処理が完了しました。",
                "next_steps": "内容を確認してください。"
            }
