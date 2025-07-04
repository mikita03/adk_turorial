from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import json

from ..models.database import SessionLocal, EmailCache, engine, Base
from ..schemas.email import EmailContent, EmailSummary

class DatabaseService:
    def __init__(self):
        Base.metadata.create_all(bind=engine)
    
    def get_db(self):
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def cache_email(self, db: Session, email: EmailContent, analysis_result: dict = None):
        existing = db.query(EmailCache).filter(EmailCache.id == email.id).first()
        if existing:
            return existing
        
        cached_email = EmailCache(
            id=email.id,
            from_email=email.from_email,
            from_name=email.from_email.split('@')[0] if '@' in email.from_email else email.from_email,
            subject=email.subject,
            body=email.body,
            date=email.date,
            processed=analysis_result is not None,
            analysis_result=json.dumps(analysis_result) if analysis_result else None
        )
        db.add(cached_email)
        db.commit()
        db.refresh(cached_email)
        return cached_email
    
    def get_cached_emails(self, db: Session, limit: int = 20, days_back: int = 14) -> List[EmailCache]:
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        return db.query(EmailCache).filter(
            EmailCache.date >= cutoff_date
        ).order_by(EmailCache.date.desc()).limit(limit).all()
    
    def get_latest_email_date(self, db: Session) -> Optional[datetime]:
        latest = db.query(EmailCache).order_by(EmailCache.date.desc()).first()
        return latest.date if latest else None
