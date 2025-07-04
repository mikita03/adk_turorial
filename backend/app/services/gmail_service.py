import os
from typing import List, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json

from ..schemas.email import EmailContent, EmailSummary

class GmailService:
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.compose',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    def __init__(self):
        self.service = None
        self.credentials = None
    
    def get_auth_url(self, redirect_uri: str) -> str:
        """Generate OAuth authorization URL"""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                    "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [redirect_uri]
                }
            },
            scopes=self.SCOPES
        )
        flow.redirect_uri = redirect_uri
        
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        return auth_url
    
    def authenticate_with_code(self, code: str, redirect_uri: str) -> bool:
        """Authenticate using OAuth code"""
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [redirect_uri]
                    }
                },
                scopes=self.SCOPES
            )
            flow.redirect_uri = redirect_uri
            
            flow.fetch_token(code=code)
            self.credentials = flow.credentials
            self.service = build('gmail', 'v1', credentials=self.credentials)
            return True
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    def get_recent_emails(self, max_results: int = 10) -> List[EmailContent]:
        """Get recent emails from inbox"""
        if not self.service:
            raise Exception("Gmail service not authenticated")
        
        try:
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['INBOX'],
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for message in messages:
                email_data = self._get_email_content(message['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
        except HttpError as error:
            print(f"Gmail API error: {error}")
            print(f"Error details: {error.error_details if hasattr(error, 'error_details') else 'No details'}")
            return []
    
    def get_recent_emails_optimized(self, days_back: int = 14, max_results: int = 100, page_token: str = None) -> dict:
        """Get recent emails with date filtering and pagination"""
        if not self.service:
            raise Exception("Gmail service not authenticated")
        
        try:
            from datetime import datetime, timedelta
            cutoff_date = datetime.now() - timedelta(days=days_back)
            date_filter = cutoff_date.strftime('%Y/%m/%d')
            
            query = f"in:inbox after:{date_filter}"
            
            params = {
                'userId': 'me',
                'q': query,
                'maxResults': min(max_results, 500)
            }
            if page_token:
                params['pageToken'] = page_token
                
            results = self.service.users().messages().list(**params).execute()
            
            messages = results.get('messages', [])
            next_page_token = results.get('nextPageToken')
            
            emails = []
            for message in messages:
                email_data = self._get_email_content(message['id'])
                if email_data:
                    emails.append(email_data)
            
            return {
                'emails': emails,
                'next_page_token': next_page_token,
                'total_fetched': len(emails)
            }
        except HttpError as error:
            print(f"Gmail API error: {error}")
            return {'emails': [], 'next_page_token': None, 'total_fetched': 0}
    
    def get_emails_since_date(self, since_date: datetime, max_results: int = 100) -> List[EmailContent]:
        """Get emails since a specific date (for differential sync)"""
        if not self.service:
            raise Exception("Gmail service not authenticated")
        
        try:
            date_filter = since_date.strftime('%Y/%m/%d')
            query = f"in:inbox after:{date_filter}"
            
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for message in messages:
                email_data = self._get_email_content(message['id'])
                if email_data and email_data.date > since_date:
                    emails.append(email_data)
            
            return emails
        except HttpError as error:
            print(f"Gmail API error: {error}")
            return []
    
    def _get_email_content(self, message_id: str) -> Optional[EmailContent]:
        """Get detailed email content"""
        if not self.service:
            return None
            
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            headers = message['payload'].get('headers', [])
            header_dict = {h['name']: h['value'] for h in headers}
            
            body = self._extract_body(message['payload'])
            
            date_str = header_dict.get('Date', '')
            try:
                date = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
            except:
                date = datetime.now()
            
            return EmailContent(
                id=message_id,
                from_email=header_dict.get('From', ''),
                to_email=[header_dict.get('To', '')],
                cc_email=[header_dict.get('Cc', '')] if header_dict.get('Cc') else [],
                subject=header_dict.get('Subject', ''),
                body=body,
                date=date,
                attachments=[]
            )
        except Exception as e:
            print(f"Error getting email content: {e}")
            return None
    
    def _extract_body(self, payload) -> str:
        """Extract email body from payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    break
        else:
            if payload['mimeType'] == 'text/plain':
                data = payload['body']['data']
                body = base64.urlsafe_b64decode(data).decode('utf-8')
        
        return body
    
    def create_draft(self, to_email: str, subject: str, body: str) -> Optional[str]:
        """Create email draft"""
        if not self.service:
            raise Exception("Gmail service not authenticated")
        
        try:
            message = MIMEText(body)
            message['to'] = to_email
            message['subject'] = subject
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            draft = self.service.users().drafts().create(
                userId='me',
                body={'message': {'raw': raw_message}}
            ).execute()
            
            return draft['id']
        except Exception as e:
            print(f"Error creating draft: {e}")
            return None
