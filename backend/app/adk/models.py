from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class AccessoryDevice(BaseModel):
    """Model representing an Android accessory device."""
    id: str
    name: str
    type: str
    description: str
    connection_type: str  # USB or Bluetooth
    protocol_version: str  # AOAv1 or AOAv2
    features: List[str]
    
class AccessoryCommand(BaseModel):
    """Model representing a command sent to an accessory."""
    device_id: str
    command_type: str
    parameters: Dict[str, Any]
    
class AccessoryResponse(BaseModel):
    """Model representing a response from an accessory."""
    device_id: str
    status: str
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
