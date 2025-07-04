import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from ..schemas.email import EmailContent, EmailSummary

class FilteringService:
    def __init__(self):
        vector_db_path = os.getenv("VECTOR_DB_PATH", "./vector_db")
        os.makedirs(vector_db_path, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=vector_db_path)
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
        
        self.rules_collection = self.client.get_or_create_collection(
            name="filtering_rules",
            metadata={"description": "Natural language email filtering rules"}
        )
        
        self.suggestions_collection = self.client.get_or_create_collection(
            name="filtering_suggestions", 
            metadata={"description": "AI-generated filtering suggestions"}
        )
    
    async def analyze_email_patterns(self, emails: List[EmailContent]) -> Dict[str, Any]:
        """Analyze email patterns to generate filtering suggestions"""
        
        automated_patterns = []
        for email in emails:
            if self._detect_automated_characteristics(email):
                automated_patterns.append({
                    "from_email": email.from_email,
                    "subject": email.subject,
                    "body_snippet": email.body[:200]
                })
        
        if not automated_patterns:
            return {"suggestions": [], "analysis": "No automated email patterns detected"}
        
        analysis_prompt = f"""
        以下の自動送信メールのパターンを分析し、フィルタリングルールを自然言語で提案してください。

        検出されたパターン:
        {json.dumps(automated_patterns[:10], ensure_ascii=False, indent=2)}

        以下のJSON形式で回答してください:
        {{
            "suggestions": [
                {{
                    "rule_description": "GitHubからの通知メールを除外",
                    "confidence": 0.9,
                    "affected_count": 15,
                    "reasoning": "多数のGitHub通知が検出されました"
                }}
            ],
            "analysis": "パターン分析の詳細説明"
        }}
        """
        
        response = await self.llm.ainvoke([HumanMessage(content=analysis_prompt)])
        
        try:
            result = json.loads(response.content)
            self._save_suggestions(result["suggestions"])
            return result
        except:
            return {"suggestions": [], "analysis": "分析に失敗しました"}
    
    def _detect_automated_characteristics(self, email: EmailContent) -> bool:
        """Detect if email has automated characteristics"""
        automated_indicators = [
            "noreply@", "no-reply@", "donotreply@", "automated@", "system@",
            "notification@", "github.com", "pull request", "pr #", "merge request",
            "ci/cd", "build failed", "build passed", "deployment"
        ]
        
        email_text = f"{email.from_email} {email.subject} {email.body}".lower()
        return any(indicator in email_text for indicator in automated_indicators)
    
    def _save_suggestions(self, suggestions: List[Dict[str, Any]]):
        """Save AI suggestions to ChromaDB"""
        for i, suggestion in enumerate(suggestions):
            self.suggestions_collection.add(
                documents=[suggestion["rule_description"]],
                metadatas=[{
                    "confidence": suggestion["confidence"],
                    "affected_count": suggestion["affected_count"],
                    "reasoning": suggestion["reasoning"],
                    "created_at": datetime.now().isoformat(),
                    "status": "pending"
                }],
                ids=[f"suggestion_{datetime.now().timestamp()}_{i}"]
            )
    
    async def apply_filtering_rule(self, rule_description: str) -> bool:
        """Apply a natural language filtering rule"""
        try:
            conversion_prompt = f"""
            以下の自然言語フィルタリングルールを、メール判定用の構造化データに変換してください。

            ルール: {rule_description}

            以下のJSON形式で回答してください:
            {{
                "filter_type": "sender|subject|content|combined",
                "patterns": ["pattern1", "pattern2"],
                "action": "exclude|include",
                "description": "ルールの説明"
            }}
            """
            
            response = await self.llm.ainvoke([HumanMessage(content=conversion_prompt)])
            filter_config = json.loads(response.content)
            
            self.rules_collection.add(
                documents=[rule_description],
                metadatas=[{
                    "filter_config": json.dumps(filter_config),
                    "created_at": datetime.now().isoformat(),
                    "active": True
                }],
                ids=[f"rule_{datetime.now().timestamp()}"]
            )
            
            return True
        except Exception as e:
            print(f"Error applying filtering rule: {e}")
            return False
    
    async def should_filter_email(self, email: EmailContent) -> bool:
        """Check if email should be filtered based on active rules"""
        try:
            rules = self.rules_collection.get(
                where={"active": True}
            )
            
            for i, rule_doc in enumerate(rules["documents"]):
                metadata = rules["metadatas"][i]
                filter_config = json.loads(metadata["filter_config"])
                
                if self._email_matches_filter(email, filter_config):
                    return filter_config["action"] == "exclude"
            
            return False
        except Exception as e:
            print(f"Error checking email filter: {e}")
            return False
    
    def _email_matches_filter(self, email: EmailContent, filter_config: Dict[str, Any]) -> bool:
        """Check if email matches a specific filter configuration"""
        patterns = filter_config["patterns"]
        filter_type = filter_config["filter_type"]
        
        if filter_type == "sender":
            return any(pattern.lower() in email.from_email.lower() for pattern in patterns)
        elif filter_type == "subject":
            return any(pattern.lower() in email.subject.lower() for pattern in patterns)
        elif filter_type == "content":
            return any(pattern.lower() in email.body.lower() for pattern in patterns)
        elif filter_type == "combined":
            email_text = f"{email.from_email} {email.subject} {email.body}".lower()
            return any(pattern.lower() in email_text for pattern in patterns)
        
        return False
