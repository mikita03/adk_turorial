from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class Priority(str, Enum):
    URGENT = "urgent"
    NORMAL = "normal"
    FYI = "fyi"

class Category(str, Enum):
    REPLY_NEEDED = "reply_needed"
    CONFIRM_ONLY = "confirm_only"
    INFO = "info"

class EmailSummary(BaseModel):
    id: str
    from_email: str
    from_name: str
    subject: str
    date: datetime
    summary: str
    priority: Priority
    category: Category
    has_attachment: bool
    important_entities: List[str] = []

class EmailContent(BaseModel):
    id: str
    from_email: str
    to_email: List[str]
    cc_email: List[str] = []
    subject: str
    body: str
    html_body: Optional[str] = None
    date: datetime
    attachments: List[Dict[str, Any]] = []

class ReplyDraft(BaseModel):
    to_email: List[str]
    cc_email: List[str] = []
    subject: str
    body: str
    confidence_score: float
    reasoning: str

class AgentResponse(BaseModel):
    agent_name: str
    task_type: str
    success: bool
    result: Dict[str, Any]
    error_message: Optional[str] = None
    processing_time: float

class LearningFeedback(BaseModel):
    original_draft: str
    corrected_draft: str
    recipient: str
    correction_type: str
    context: Dict[str, Any]
    timestamp: datetime
