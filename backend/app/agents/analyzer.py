import logging
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import re
from datetime import datetime

from ..schemas.email import EmailContent, EmailSummary, Priority, Category

logger = logging.getLogger(__name__)

class AnalyzerAgent:
    def __init__(self, llm_model: str = "gpt-4o"):
        logger.info(f"Initializing AnalyzerAgent with model: {llm_model}")
        try:
            import os
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key or api_key == 'your_openai_api_key_here':
                logger.warning("OPENAI_API_KEY not configured or using placeholder value. AI analysis will be disabled.")
                self.llm = None
                self.ai_enabled = False
            else:
                self.llm = ChatOpenAI(model=llm_model, temperature=0.1)
                self.ai_enabled = True
                logger.info("AnalyzerAgent ChatOpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AnalyzerAgent ChatOpenAI: {e}")
            self.llm = None
            self.ai_enabled = False
        self.role = """
        あなたはメール分析の専門エージェントです。
        メールの要約、優先度判定、カテゴリ分類、重要情報抽出を行います。
        """
    
    async def analyze_email(self, email: EmailContent) -> Dict[str, Any]:
        """Analyze email and extract key information"""
        
        if not self.ai_enabled or not self.llm:
            logger.info(f"AI analysis disabled, using fallback for email: {email.subject}")
            return self._create_fallback_analysis(email)
        
        analysis_prompt = f"""
        以下のメールを分析し、要約・分類・重要情報を抽出してください。

        送信者: {email.from_email}
        件名: {email.subject}
        本文:
        {email.body}

        以下の項目について分析してください:

        1. 要約（3行以内）
        2. 優先度（urgent/normal/fyi）
        3. カテゴリ（reply_needed/confirm_only/info）
        4. 重要な情報（日付、金額、人名、タスクなど）

        以下のJSON形式で回答してください:
        {{
            "summary": "3行以内の要約",
            "priority": "urgent|normal|fyi",
            "category": "reply_needed|confirm_only|info",
            "important_entities": ["日付: 2025年1月15日", "金額: 100万円", "人名: 田中部長"],
            "key_points": ["重要なポイント1", "重要なポイント2"],
            "action_required": "必要なアクション",
            "deadline": "期限があれば記載",
            "confidence_score": 0.95
        }}
        """
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=analysis_prompt)])
            
            import json
            analysis_result = json.loads(response.content)
            
            email_summary = EmailSummary(
                id=email.id,
                from_email=email.from_email,
                from_name=self._extract_name_from_email(email.from_email),
                subject=email.subject,
                date=email.date,
                summary=analysis_result.get("summary", ""),
                priority=Priority(analysis_result.get("priority", "normal")),
                category=Category(analysis_result.get("category", "confirm_only")),
                has_attachment=len(email.attachments) > 0,
                important_entities=analysis_result.get("important_entities", [])
            )
            
            return {
                "success": True,
                "email_summary": email_summary.dict(),
                "analysis_details": analysis_result,
                "processing_time": 0.0,
                "ai_analyzed": True
            }
            
        except Exception as e:
            logger.error(f"AI analysis failed for email {email.id}: {e}")
            return self._create_fallback_analysis(email)
    
    def _extract_name_from_email(self, email_address: str) -> str:
        """Extract name from email address"""
        if '<' in email_address and '>' in email_address:
            name_part = email_address.split('<')[0].strip()
            return name_part.strip('"')
        else:
            return email_address.split('@')[0]
    
    async def extract_entities(self, text: str) -> List[str]:
        """Extract important entities from text"""
        
        entity_prompt = f"""
        以下のテキストから重要な情報を抽出してください:

        {text}

        抽出する情報:
        - 日付・時間
        - 金額・数値
        - 人名・会社名
        - 場所
        - タスク・アクション項目

        JSON配列形式で回答してください:
        ["日付: 2025年1月15日", "金額: 100万円", "人名: 田中部長"]
        """
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=entity_prompt)])
            import json
            entities = json.loads(response.content)
            return entities if isinstance(entities, list) else []
        except:
            return self._regex_entity_extraction(text)
    
    def _regex_entity_extraction(self, text: str) -> List[str]:
        """Fallback regex-based entity extraction"""
        entities = []
        
        date_patterns = [
            r'\d{4}年\d{1,2}月\d{1,2}日',
            r'\d{1,2}/\d{1,2}',
            r'\d{1,2}月\d{1,2}日'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                entities.append(f"日付: {match}")
        
        amount_patterns = [
            r'\d+万円',
            r'\d+円',
            r'¥\d+',
            r'\d+,\d+円'
        ]
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                entities.append(f"金額: {match}")
        
        return entities[:10]  # Limit to 10 entities
    
    def _create_fallback_analysis(self, email: EmailContent) -> Dict[str, Any]:
        """Create basic analysis when AI is not available"""
        
        priority = "normal"
        if any(keyword in email.subject.lower() for keyword in ["緊急", "urgent", "asap", "至急"]):
            priority = "urgent"
        elif any(keyword in email.subject.lower() for keyword in ["fyi", "参考", "情報"]):
            priority = "fyi"
        
        category = "confirm_only"
        if any(keyword in email.subject.lower() for keyword in ["返信", "reply", "回答", "確認"]):
            category = "reply_needed"
        elif any(keyword in email.subject.lower() for keyword in ["情報", "fyi", "参考"]):
            category = "info"
        
        summary = email.body[:100] + "..." if len(email.body) > 100 else email.body
        
        email_summary = EmailSummary(
            id=email.id,
            from_email=email.from_email,
            from_name=self._extract_name_from_email(email.from_email),
            subject=email.subject,
            date=email.date,
            summary=summary,
            priority=Priority(priority),
            category=Category(category),
            has_attachment=len(email.attachments) > 0,
            important_entities=self._regex_entity_extraction(email.body)
        )
        
        return {
            "success": True,
            "email_summary": email_summary.dict(),
            "analysis_details": {
                "summary": summary,
                "priority": priority,
                "category": category,
                "important_entities": self._regex_entity_extraction(email.body),
                "confidence_score": 0.5
            },
            "processing_time": 0.0,
            "ai_analyzed": False
        }
