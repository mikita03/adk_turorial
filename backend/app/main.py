import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('gmail_secretary.log')
    ]
)
logger = logging.getLogger(__name__)
logger.info("Gmail Secretary Agent API starting up with detailed logging")

from .models.database import Base, engine
Base.metadata.create_all(bind=engine)

from .routers import auth, emails, websocket

app = FastAPI(
    title="Gmail Secretary Agent API",
    description="AI-powered Gmail management system with multi-agent architecture",
    version="1.0.0"
)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(auth.router)
app.include_router(emails.router)
app.include_router(websocket.router)

@app.get("/")
async def root():
    return {
        "message": "Gmail Secretary Agent API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Gmail Secretary Agent API is running"}

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/config")
async def get_config():
    """Get client configuration"""
    return {
        "google_client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
        "backend_url": os.getenv("BACKEND_URL", "http://localhost:8000"),
        "frontend_url": os.getenv("FRONTEND_URL", "http://localhost:3000")
    }
