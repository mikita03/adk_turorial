import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Any, List
import json
import asyncio
from datetime import datetime

from ..services.shared_gmail import shared_gmail

logger = logging.getLogger(__name__)

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                self.active_connections.remove(connection)

manager = ConnectionManager()
gmail_service = shared_gmail.get_service()

def get_supervisor_agent():
    """Get SupervisorAgent instance with detailed error logging"""
    logger.info("Attempting to initialize SupervisorAgent for WebSocket")
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
        
        raise Exception(f"AI分析サービスが利用できません: {str(e)}")

@router.websocket("/ws/agent")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            message_type = message.get("type")
            
            if message_type == "process_email":
                await handle_email_processing(websocket, message)
            elif message_type == "generate_reply":
                await handle_reply_generation(websocket, message)
            elif message_type == "analyze_email":
                await handle_email_analysis(websocket, message)
            elif message_type == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }))
            else:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"WebSocket error: {str(e)}"
        }))
        manager.disconnect(websocket)

async def handle_email_processing(websocket: WebSocket, message: Dict[str, Any]):
    """Handle email processing through agents"""
    try:
        email_id = message.get("email_id")
        if not email_id:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "email_id is required"
            }))
            return
        
        await websocket.send_text(json.dumps({
            "type": "processing_started",
            "email_id": email_id,
            "timestamp": datetime.now().isoformat()
        }))
        
        email = gmail_service._get_email_content(email_id)
        if not email:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Email not found"
            }))
            return
        
        try:
            supervisor_agent = get_supervisor_agent()
            logger.info("SupervisorAgent initialized for WebSocket processing")
        except Exception as e:
            logger.error(f"Failed to initialize SupervisorAgent for WebSocket: {e}")
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"AI分析サービスが利用できません: {str(e)}"
            }))
            return
        
        routing_decision = await supervisor_agent.route_email(email)
        logger.debug(f"WebSocket routing decision: {routing_decision}")
        await websocket.send_text(json.dumps({
            "type": "routing_decision",
            "email_id": email_id,
            "routing": routing_decision,
            "timestamp": datetime.now().isoformat()
        }))
        
        result = await supervisor_agent.coordinate_agents(email, routing_decision)
        logger.info("WebSocket AI processing completed successfully")
        
        for agent_name, agent_result in result.get("agent_results", {}).items():
            await websocket.send_text(json.dumps({
                "type": "agent_result",
                "email_id": email_id,
                "agent": agent_name,
                "result": agent_result,
                "timestamp": datetime.now().isoformat()
            }))
        
        await websocket.send_text(json.dumps({
            "type": "processing_complete",
            "email_id": email_id,
            "final_result": result,
            "timestamp": datetime.now().isoformat()
        }))
        
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"Processing error: {str(e)}"
        }))

async def handle_reply_generation(websocket: WebSocket, message: Dict[str, Any]):
    """Handle reply generation"""
    try:
        email_id = message.get("email_id")
        if not email_id:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "email_id is required"
            }))
            return
        
        await websocket.send_text(json.dumps({
            "type": "reply_generation_started",
            "email_id": email_id,
            "timestamp": datetime.now().isoformat()
        }))
        
        email = gmail_service._get_email_content(email_id)
        if not email:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Email not found"
            }))
            return
        
        try:
            from ..agents.responder import ResponderAgent
            logger.debug("ResponderAgent import successful")
            responder = ResponderAgent()
            logger.info("ResponderAgent initialized successfully")
        except Exception as e:
            logger.error(f"ResponderAgent initialization failed: {e}", exc_info=True)
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"返信生成サービスが利用できません: {str(e)}"
            }))
            return
        
        reply_result = await responder.generate_reply(email)
        logger.debug(f"Reply generation result: {reply_result.get('success', False)}")
        
        await websocket.send_text(json.dumps({
            "type": "reply_generated",
            "email_id": email_id,
            "reply_result": reply_result,
            "timestamp": datetime.now().isoformat()
        }))
        
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"Reply generation error: {str(e)}"
        }))

async def handle_email_analysis(websocket: WebSocket, message: Dict[str, Any]):
    """Handle email analysis"""
    try:
        email_id = message.get("email_id")
        if not email_id:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "email_id is required"
            }))
            return
        
        await websocket.send_text(json.dumps({
            "type": "analysis_started",
            "email_id": email_id,
            "timestamp": datetime.now().isoformat()
        }))
        
        email = gmail_service._get_email_content(email_id)
        if not email:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Email not found"
            }))
            return
        
        try:
            from ..agents.analyzer import AnalyzerAgent
            logger.debug("AnalyzerAgent import successful")
            analyzer = AnalyzerAgent()
            logger.info("AnalyzerAgent initialized successfully")
        except Exception as e:
            logger.error(f"AnalyzerAgent initialization failed: {e}", exc_info=True)
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"分析サービスが利用できません: {str(e)}"
            }))
            return
        
        analysis_result = await analyzer.analyze_email(email)
        logger.debug(f"Analysis result: {analysis_result.get('success', False)}")
        
        await websocket.send_text(json.dumps({
            "type": "analysis_complete",
            "email_id": email_id,
            "analysis_result": analysis_result,
            "timestamp": datetime.now().isoformat()
        }))
        
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"Analysis error: {str(e)}"
        }))
