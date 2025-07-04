from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from .database_service import DatabaseService
from .shared_gmail import shared_gmail
from ..schemas.email import EmailContent, EmailSummary, Priority, Category
from ..models.database import EmailCache
import json

class EmailCacheService:
    def __init__(self):
        self.db_service = DatabaseService()
        self.gmail_service = shared_gmail.get_service()
    
    def get_recent_emails_cached(self, limit: int = 20, force_refresh: bool = False) -> List[EmailSummary]:
        db = next(self.db_service.get_db())
        
        try:
            if not force_refresh:
                cached_emails = self.db_service.get_cached_emails(db, limit=limit, days_back=14)
                if cached_emails and len(cached_emails) >= min(limit, 10):
                    return self._convert_cached_to_summaries(cached_emails)
            
            latest_date = self.db_service.get_latest_email_date(db)
            
            if latest_date:
                new_emails = self.gmail_service.get_emails_since_date(latest_date, max_results=100)
            else:
                result = self.gmail_service.get_recent_emails_optimized(days_back=14, max_results=100)
                new_emails = result['emails']
            
            processed_summaries = []
            for email in new_emails:
                cached_email = self.db_service.cache_email(db, email)
                
                summary = self._convert_email_to_summary(email)
                processed_summaries.append(summary)
            
            all_cached = self.db_service.get_cached_emails(db, limit=limit, days_back=14)
            return self._convert_cached_to_summaries(all_cached)
            
        finally:
            db.close()
    
    def _convert_cached_to_summaries(self, cached_emails: List[EmailCache]) -> List[EmailSummary]:
        summaries = []
        for cached in cached_emails:
            if cached.analysis_result:
                try:
                    analysis = json.loads(cached.analysis_result)
                    summary_data = analysis.get('email_summary', {})
                    if summary_data:
                        summaries.append(EmailSummary(**summary_data))
                        continue
                except:
                    pass
            
            summary = EmailSummary(
                id=cached.id,
                from_email=cached.from_email,
                from_name=cached.from_name or cached.from_email.split('@')[0],
                subject=cached.subject or "",
                date=cached.date,
                summary=cached.body[:100] + "..." if cached.body and len(cached.body) > 100 else cached.body or "",
                priority=Priority.NORMAL,
                category=Category.CONFIRM_ONLY,
                has_attachment=False,
                important_entities=[]
            )
            summaries.append(summary)
        
        return summaries
    
    def _convert_email_to_summary(self, email: EmailContent) -> EmailSummary:
        return EmailSummary(
            id=email.id,
            from_email=email.from_email,
            from_name=email.from_email.split('@')[0] if '@' in email.from_email else email.from_email,
            subject=email.subject,
            date=email.date,
            summary=email.body[:100] + "..." if len(email.body) > 100 else email.body,
            priority=Priority.NORMAL,
            category=Category.CONFIRM_ONLY,
            has_attachment=len(email.attachments) > 0,
            important_entities=[]
        )
