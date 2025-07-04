from .gmail_service import GmailService

class SharedGmailService:
    _instance = None
    _gmail_service = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._gmail_service = GmailService()
        return cls._instance
    
    def get_service(self) -> GmailService:
        return self._gmail_service

shared_gmail = SharedGmailService()
