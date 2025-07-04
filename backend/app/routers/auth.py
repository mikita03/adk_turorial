from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
import os

from ..services.shared_gmail import shared_gmail

router = APIRouter(prefix="/auth", tags=["authentication"])

class AuthResponse(BaseModel):
    success: bool
    message: str
    auth_url: Optional[str] = None

class AuthCallbackRequest(BaseModel):
    code: str
    state: Optional[str] = None

gmail_service = shared_gmail.get_service()

@router.get("/google")
async def google_auth():
    """Initiate Google OAuth flow"""
    try:
        redirect_uri = f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/auth/callback"
        auth_url = gmail_service.get_auth_url(redirect_uri)
        
        return AuthResponse(
            success=True,
            message="認証URLを生成しました",
            auth_url=auth_url
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"認証エラー: {str(e)}")

@router.get("/callback")
async def auth_callback(code: str, state: Optional[str] = None):
    """Handle Google OAuth callback"""
    try:
        redirect_uri = f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/auth/callback"
        success = gmail_service.authenticate_with_code(code, redirect_uri)
        
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        if success:
            return RedirectResponse(url=frontend_url)
        else:
            return RedirectResponse(url=f"{frontend_url}?auth=error")
            
    except Exception as e:
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        return RedirectResponse(url=f"{frontend_url}?auth=error&message={str(e)}")

@router.post("/callback")
async def auth_callback_post(request: AuthCallbackRequest):
    """Handle OAuth callback via POST (for SPA)"""
    try:
        redirect_uri = f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/auth/callback"
        success = gmail_service.authenticate_with_code(request.code, redirect_uri)
        
        return AuthResponse(
            success=success,
            message="認証が完了しました" if success else "認証に失敗しました"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"認証エラー: {str(e)}")

@router.get("/status")
async def auth_status():
    """Check authentication status"""
    is_authenticated = gmail_service.service is not None
    
    return {
        "authenticated": is_authenticated,
        "message": "認証済み" if is_authenticated else "未認証"
    }
