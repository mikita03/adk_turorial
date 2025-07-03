from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from datetime import datetime, timedelta
import json

from ..schemas.email import EmailContent, ReplyDraft
from ..services.learning_service import LearningService

class ResponderAgent:
    def __init__(self, llm_model: str = "gpt-4"):
        self.llm = ChatOpenAI(model=llm_model, temperature=0.3)
        self.learning_service = LearningService()
        self.role = """
        あなたはメール返信の専門エージェントです。
        適切な敬語レベルと文体で返信案を作成し、日程調整も行います。
        過去の修正履歴から学習し、相手の好みに合わせた返信を生成します。
        """
    
    async def generate_reply(self, email: EmailContent) -> Dict[str, Any]:
        """Generate reply draft for the email"""
        
        try:
            recipient = email.from_email
            similar_cases = await self.learning_service.get_similar_corrections(
                email.body, recipient, limit=3
            )
            recipient_profile = await self.learning_service.get_recipient_profile(recipient)
            
            reply_prompt = self._build_reply_prompt(email, similar_cases, recipient_profile)
            response = await self.llm.ainvoke([HumanMessage(content=reply_prompt)])
            
            reply_data = json.loads(response.content)
            
            reply_draft = ReplyDraft(
                to_email=[email.from_email],
                cc_email=[],
                subject=f"Re: {email.subject}",
                body=reply_data.get("body", ""),
                confidence_score=reply_data.get("confidence_score", 0.8),
                reasoning=reply_data.get("reasoning", "")
            )
            
            return {
                "success": True,
                "reply_draft": reply_draft.dict(),
                "suggestions": reply_data.get("suggestions", []),
                "processing_time": 0.0
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "reply_draft": None,
                "processing_time": 0.0
            }
    
    def _build_reply_prompt(self, email: EmailContent, similar_cases: List[Dict], profile: Optional[Dict]) -> str:
        """Build prompt for reply generation"""
        
        sender_name = self._extract_sender_name(email.from_email)
        
        similar_context = ""
        if similar_cases:
            similar_context = "\n過去の類似ケースでの修正例:\n"
            for case in similar_cases:
                similar_context += f"- 修正前: {case.get('original', '')[:100]}...\n"
                similar_context += f"  修正後: {case.get('corrected', '')[:100]}...\n"
        
        profile_context = ""
        if profile:
            preferences = profile.get('preferences', {})
            if preferences:
                profile_context = f"\n{sender_name}さんの好み:\n"
                for key, value in preferences.items():
                    profile_context += f"- {key}: {value}\n"
        
        prompt = f"""
        以下のメールに対する返信案を作成してください。

        受信メール:
        送信者: {email.from_email}
        件名: {email.subject}
        本文:
        {email.body}

        {similar_context}
        {profile_context}

        返信作成の指針:
        1. 適切な敬語レベルを使用
        2. 簡潔で分かりやすい文章
        3. 必要に応じて日程提案を含める
        4. 相手の好みや過去の修正例を考慮
        5. ビジネスメールとして適切な構成

        以下のJSON形式で回答してください:
        {{
            "body": "返信本文",
            "confidence_score": 0.85,
            "reasoning": "この返信案を選んだ理由",
            "suggestions": ["代替案1", "代替案2"],
            "schedule_proposal": "日程提案があれば記載"
        }}
        """
        
        return prompt
    
    def _extract_sender_name(self, email_address: str) -> str:
        """Extract sender name from email address"""
        if '<' in email_address and '>' in email_address:
            name_part = email_address.split('<')[0].strip()
            return name_part.strip('"') or email_address.split('@')[0]
        else:
            return email_address.split('@')[0]
    
    async def suggest_meeting_times(self, email_content: str) -> List[str]:
        """Suggest meeting times based on email content"""
        
        schedule_prompt = f"""
        以下のメール内容から、適切な会議時間を3つ提案してください。

        メール内容:
        {email_content}

        提案する時間帯:
        - 平日の営業時間内（9:00-18:00）
        - 1時間の会議を想定
        - 今日から1週間以内

        JSON配列形式で回答してください:
        ["1月15日(水) 14:00-15:00", "1月16日(木) 10:00-11:00", "1月17日(金) 15:00-16:00"]
        """
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=schedule_prompt)])
            suggestions = json.loads(response.content)
            return suggestions if isinstance(suggestions, list) else []
        except:
            base_date = datetime.now()
            suggestions = []
            for i in range(3):
                future_date = base_date + timedelta(days=i+1)
                if future_date.weekday() < 5:  # Weekday
                    time_slot = f"{future_date.strftime('%m月%d日(%a)')} 14:00-15:00"
                    suggestions.append(time_slot)
            return suggestions[:3]
    
    async def save_correction(self, original_draft: str, corrected_draft: str, recipient: str, context: Dict[str, Any]):
        """Save user correction for learning"""
        await self.learning_service.save_correction(
            original=original_draft,
            corrected=corrected_draft,
            context={
                "recipient": recipient,
                "timestamp": datetime.now().isoformat(),
                "correction_type": context.get("type", "general"),
                **context
            }
        )
