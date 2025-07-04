import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from pydantic import BaseModel

from ..services.shared_gmail import shared_gmail
from ..services.email_cache_service import EmailCacheService
from ..schemas.email import EmailSummary, EmailContent, AgentResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/emails", tags=["emails"])

class EmailProcessRequest(BaseModel):
    email_id: str
    force_reprocess: bool = False

class EmailListResponse(BaseModel):
    emails: List[EmailSummary]
    total_count: int
    unread_count: int
    urgent_count: int
    reply_needed_count: int
    normal_count: int
    fyi_count: int
    cache_status: str

gmail_service = shared_gmail.get_service()
email_cache_service = EmailCacheService()

def get_supervisor_agent():
    """Get SupervisorAgent instance with detailed error logging and lazy initialization"""
    logger.info("Attempting to initialize SupervisorAgent")
    try:
        from ..agents.supervisor import SupervisorAgent
        logger.debug("SupervisorAgent import successful")
        
        agent = SupervisorAgent()
        logger.info("SupervisorAgent initialization successful")
        return agent
        
    except Exception as e:
        logger.error(f"SupervisorAgent initialization failed: {type(e).__name__}: {str(e)}")
        logger.debug("Full traceback:", exc_info=True)
        
        if "api_key" in str(e).lower():
            logger.error("OpenAI API key not configured. Set OPENAI_API_KEY environment variable.")
        elif "openai" in str(e).lower():
            logger.error("OpenAI client initialization failed. Check API configuration.")
        else:
            logger.error(f"Unexpected SupervisorAgent error: {e}")
        
        raise HTTPException(
            status_code=503, 
            detail=f"AI分析サービスが利用できません: {str(e)}"
        )

@router.get("/", response_model=EmailListResponse)
async def get_emails(limit: int = 20, force_refresh: bool = False):
    """Get recent emails with intelligent caching and 2-week limit"""
    try:
        logger.info(f"Getting emails with limit={limit}, force_refresh={force_refresh}")
        
        if not gmail_service.service:
            logger.warning("Gmail service not authenticated")
            raise HTTPException(status_code=401, detail="Gmail認証が必要です")
        
        processed_emails = await email_cache_service.get_recent_emails_cached(
            limit=limit, 
            force_refresh=force_refresh
        )
        
        logger.info(f"Successfully processed {len(processed_emails)} emails")
        
        urgent_count = len([e for e in processed_emails if e.priority.value == "urgent"])
        reply_needed_count = len([e for e in processed_emails if e.category.value == "reply_needed"])
        normal_count = len([e for e in processed_emails if e.priority.value == "normal"])
        fyi_count = len([e for e in processed_emails if e.priority.value == "fyi"])
        
        response = EmailListResponse(
            emails=processed_emails,
            total_count=len(processed_emails),
            unread_count=reply_needed_count,  # Use reply_needed as unread
            urgent_count=urgent_count,
            reply_needed_count=reply_needed_count,
            normal_count=normal_count,
            fyi_count=fyi_count,
            cache_status="cached" if not force_refresh else "refreshed"
        )
        
        logger.debug(f"Response structure: total={response.total_count}, urgent={response.urgent_count}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_emails: {type(e).__name__}: {str(e)}")
        logger.debug("Full traceback:", exc_info=True)
        raise HTTPException(status_code=500, detail=f"メール取得エラー: {str(e)}")

@router.get("/{email_id}")
async def get_email_detail(email_id: str):
    """Get detailed email content and analysis"""
    try:
        logger.info(f"Processing email detail request for email_id: {email_id}")
        
        if not gmail_service.service:
            logger.warning("Gmail service not authenticated")
            raise HTTPException(status_code=401, detail="Gmail認証が必要です")
        
        logger.debug("Attempting to retrieve email from cache")
        email = email_cache_service.get_email_by_id_cached(email_id)
        if not email:
            logger.warning(f"Email not found in cache or Gmail: {email_id}")
            raise HTTPException(status_code=404, detail="メールが見つかりません")
        
        logger.debug(f"Email retrieved successfully: {email.subject}")
        
        logger.info("Initializing SupervisorAgent for AI analysis")
        supervisor_agent = get_supervisor_agent()
        
        logger.info("Starting AI analysis for email")
        routing_decision = await supervisor_agent.route_email(email)
        logger.debug(f"Routing decision: {routing_decision}")
        
        result = await supervisor_agent.coordinate_agents(email, routing_decision)
        logger.info("AI analysis completed successfully")
        
        return {
            "email": email.dict(),
            "analysis": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_email_detail: {type(e).__name__}: {str(e)}")
        logger.debug("Full traceback:", exc_info=True)
        raise HTTPException(status_code=500, detail=f"メール詳細取得エラー: {str(e)}")

@router.post("/{email_id}/process")
async def process_email(email_id: str, request: EmailProcessRequest):
    """Process specific email through agents"""
    try:
        logger.info(f"Processing email through agents for email_id: {email_id}")
        
        if not gmail_service.service:
            logger.warning("Gmail service not authenticated")
            raise HTTPException(status_code=401, detail="Gmail認証が必要です")
        
        logger.debug("Retrieving email from Gmail")
        email = gmail_service._get_email_content(email_id)
        if not email:
            logger.warning(f"Email not found in Gmail: {email_id}")
            raise HTTPException(status_code=404, detail="メールが見つかりません")
        
        logger.debug(f"Email retrieved from Gmail: {email.subject}")
        
        logger.info("Initializing SupervisorAgent for AI processing")
        supervisor_agent = get_supervisor_agent()
        
        logger.info("Starting AI processing for email")
        routing_decision = await supervisor_agent.route_email(email)
        logger.debug(f"Routing decision: {routing_decision}")
        
        result = await supervisor_agent.coordinate_agents(email, routing_decision)
        logger.info("AI processing completed successfully")
        
        return {
            "success": True,
            "email_id": email_id,
            "processing_result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in process_email: {type(e).__name__}: {str(e)}")
        logger.debug("Full traceback:", exc_info=True)
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

@router.post("/filtering/analyze")
async def analyze_email_patterns():
    """Analyze email patterns and generate filtering suggestions"""
    try:
        if not gmail_service.service:
            raise HTTPException(status_code=401, detail="Gmail認証が必要です")
        
        result = gmail_service.get_recent_emails_optimized(days_back=14, max_results=100)
        emails = result['emails']
        
        from ..services.filtering_service import FilteringService
        filtering_service = FilteringService()
        analysis_result = await filtering_service.analyze_email_patterns(emails)
        
        return {
            "success": True,
            "analysis": analysis_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"パターン分析エラー: {str(e)}")

@router.post("/filtering/rules")
async def apply_filtering_rule(rule_description: str):
    """Apply a natural language filtering rule"""
    try:
        from ..services.filtering_service import FilteringService
        filtering_service = FilteringService()
        
        success = await filtering_service.apply_filtering_rule(rule_description)
        
        if success:
            return {"success": True, "message": "フィルタリングルールが適用されました"}
        else:
            raise HTTPException(status_code=500, detail="ルール適用に失敗しました")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ルール適用エラー: {str(e)}")

@router.get("/filtering/suggestions")
async def get_filtering_suggestions():
    """Get pending filtering suggestions"""
    try:
        from ..services.filtering_service import FilteringService
        filtering_service = FilteringService()
        
        suggestions = filtering_service.suggestions_collection.get(
            where={"status": "pending"}
        )
        
        return {
            "success": True,
            "suggestions": [
                {
                    "id": suggestions["ids"][i],
                    "description": suggestions["documents"][i],
                    "metadata": suggestions["metadatas"][i]
                }
                for i in range(len(suggestions["documents"]))
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提案取得エラー: {str(e)}")
