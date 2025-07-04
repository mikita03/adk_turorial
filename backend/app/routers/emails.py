from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from pydantic import BaseModel

from ..services.shared_gmail import shared_gmail
from ..agents.supervisor import SupervisorAgent
from ..schemas.email import EmailSummary, EmailContent, AgentResponse

router = APIRouter(prefix="/emails", tags=["emails"])

class EmailProcessRequest(BaseModel):
    email_id: str
    force_reprocess: bool = False

class EmailListResponse(BaseModel):
    emails: List[EmailSummary]
    total_count: int
    unread_count: int

gmail_service = shared_gmail.get_service()
supervisor_agent = SupervisorAgent()

@router.get("/", response_model=EmailListResponse)
async def get_emails(limit: int = 20):
    """Get recent emails with AI analysis"""
    try:
        if not gmail_service.service:
            raise HTTPException(status_code=401, detail="Gmail認証が必要です")
        
        emails = gmail_service.get_recent_emails(max_results=limit)
        
        processed_emails = []
        for email in emails:
            try:
                routing_decision = await supervisor_agent.route_email(email)
                result = await supervisor_agent.coordinate_agents(email, routing_decision)
                
                analyzer_result = result.get("agent_results", {}).get("analyzer", {})
                if analyzer_result.get("success") and analyzer_result.get("email_summary"):
                    email_summary_data = analyzer_result["email_summary"]
                    email_summary = EmailSummary(**email_summary_data)
                    processed_emails.append(email_summary)
                else:
                    from ..schemas.email import Priority, Category
                    fallback_summary = EmailSummary(
                        id=email.id,
                        from_email=email.from_email,
                        from_name=email.from_email.split('@')[0],
                        subject=email.subject,
                        date=email.date,
                        summary=email.body[:100] + "..." if len(email.body) > 100 else email.body,
                        priority=Priority.NORMAL,
                        category=Category.CONFIRM_ONLY,
                        has_attachment=len(email.attachments) > 0,
                        important_entities=[]
                    )
                    processed_emails.append(fallback_summary)
                    
            except Exception as e:
                print(f"Error processing email {email.id}: {e}")
                continue
        
        return EmailListResponse(
            emails=processed_emails,
            total_count=len(processed_emails),
            unread_count=len([e for e in processed_emails if e.category.value == "reply_needed"])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"メール取得エラー: {str(e)}")

@router.get("/{email_id}")
async def get_email_detail(email_id: str):
    """Get detailed email content and analysis"""
    try:
        if not gmail_service.service:
            raise HTTPException(status_code=401, detail="Gmail認証が必要です")
        
        email = gmail_service._get_email_content(email_id)
        if not email:
            raise HTTPException(status_code=404, detail="メールが見つかりません")
        
        routing_decision = await supervisor_agent.route_email(email)
        result = await supervisor_agent.coordinate_agents(email, routing_decision)
        
        return {
            "email": email.dict(),
            "analysis": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"メール詳細取得エラー: {str(e)}")

@router.post("/{email_id}/process")
async def process_email(email_id: str, request: EmailProcessRequest):
    """Process specific email through agents"""
    try:
        if not gmail_service.service:
            raise HTTPException(status_code=401, detail="Gmail認証が必要です")
        
        email = gmail_service._get_email_content(email_id)
        if not email:
            raise HTTPException(status_code=404, detail="メールが見つかりません")
        
        routing_decision = await supervisor_agent.route_email(email)
        result = await supervisor_agent.coordinate_agents(email, routing_decision)
        
        return {
            "success": True,
            "email_id": email_id,
            "processing_result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"メール処理エラー: {str(e)}")

@router.post("/{email_id}/reply")
async def create_reply_draft(email_id: str):
    """Create reply draft for email"""
    try:
        if not gmail_service.service:
            raise HTTPException(status_code=401, detail="Gmail認証が必要です")
        
        email = gmail_service._get_email_content(email_id)
        if not email:
            raise HTTPException(status_code=404, detail="メールが見つかりません")
        
        from ..agents.responder import ResponderAgent
        responder = ResponderAgent()
        reply_result = await responder.generate_reply(email)
        
        if reply_result.get("success"):
            reply_draft = reply_result["reply_draft"]
            
            draft_id = gmail_service.create_draft(
                to_email=reply_draft["to_email"][0],
                subject=reply_draft["subject"],
                body=reply_draft["body"]
            )
            
            return {
                "success": True,
                "draft_id": draft_id,
                "reply_draft": reply_draft
            }
        else:
            raise HTTPException(status_code=500, detail=reply_result.get("error", "返信生成に失敗しました"))
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"返信作成エラー: {str(e)}")
