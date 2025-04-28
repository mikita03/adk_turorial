from fastapi import APIRouter, HTTPException
from typing import List
import uuid

from .models import AccessoryDevice, AccessoryCommand, AccessoryResponse

router = APIRouter(prefix="/adk", tags=["ADK"])

devices = [
    AccessoryDevice(
        id="adk-001",
        name="LED Controller",
        type="lighting",
        description="RGB LED controller for Android devices",
        connection_type="USB",
        protocol_version="AOAv2",
        features=["color_control", "brightness_control", "pattern_selection"]
    ),
    AccessoryDevice(
        id="adk-002",
        name="Temperature Sensor",
        type="sensor",
        description="Temperature and humidity sensor for Android devices",
        connection_type="Bluetooth",
        protocol_version="AOAv1",
        features=["temperature_reading", "humidity_reading", "data_logging"]
    ),
    AccessoryDevice(
        id="adk-003",
        name="Game Controller",
        type="input",
        description="Game controller for Android devices",
        connection_type="USB",
        protocol_version="AOAv2",
        features=["buttons", "joystick", "accelerometer", "vibration"]
    )
]

device_states = {
    "adk-001": {
        "connected": False,
        "color": "#FFFFFF",
        "brightness": 50,
        "pattern": "solid"
    },
    "adk-002": {
        "connected": False,
        "temperature": 22.5,
        "humidity": 45.0,
        "logging": False
    },
    "adk-003": {
        "connected": False,
        "button_states": {},
        "joystick_position": {"x": 0, "y": 0},
        "vibration": 0
    }
}

@router.get("/devices", response_model=List[AccessoryDevice])
async def get_devices():
    """Get all available ADK devices."""
    return devices

@router.get("/devices/{device_id}", response_model=AccessoryDevice)
async def get_device(device_id: str):
    """Get a specific ADK device by ID."""
    for device in devices:
        if device.id == device_id:
            return device
    raise HTTPException(status_code=404, detail="Device not found")

@router.get("/devices/{device_id}/state")
async def get_device_state(device_id: str):
    """Get the current state of a device."""
    if device_id not in device_states:
        raise HTTPException(status_code=404, detail="Device not found")
    return device_states[device_id]

@router.post("/devices/{device_id}/connect", response_model=AccessoryResponse)
async def connect_device(device_id: str):
    """Connect to an ADK device."""
    if device_id not in device_states:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device_states[device_id]["connected"] = True
    
    return AccessoryResponse(
        device_id=device_id,
        status="success",
        message="Device connected successfully"
    )

@router.post("/devices/{device_id}/disconnect", response_model=AccessoryResponse)
async def disconnect_device(device_id: str):
    """Disconnect from an ADK device."""
    if device_id not in device_states:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device_states[device_id]["connected"] = False
    
    return AccessoryResponse(
        device_id=device_id,
        status="success",
        message="Device disconnected successfully"
    )

@router.post("/devices/{device_id}/command", response_model=AccessoryResponse)
async def send_command(device_id: str, command: AccessoryCommand):
    """Send a command to an ADK device."""
    if device_id not in device_states:
        raise HTTPException(status_code=404, detail="Device not found")
    
    if not device_states[device_id]["connected"]:
        raise HTTPException(status_code=400, detail="Device not connected")
    
    if device_id == "adk-001":  # LED Controller
        if command.command_type == "set_color":
            device_states[device_id]["color"] = command.parameters.get("color", "#FFFFFF")
        elif command.command_type == "set_brightness":
            device_states[device_id]["brightness"] = command.parameters.get("brightness", 50)
        elif command.command_type == "set_pattern":
            device_states[device_id]["pattern"] = command.parameters.get("pattern", "solid")
    
    elif device_id == "adk-002":  # Temperature Sensor
        if command.command_type == "start_logging":
            device_states[device_id]["logging"] = True
        elif command.command_type == "stop_logging":
            device_states[device_id]["logging"] = False
    
    elif device_id == "adk-003":  # Game Controller
        if command.command_type == "set_vibration":
            device_states[device_id]["vibration"] = command.parameters.get("intensity", 0)
    
    return AccessoryResponse(
        device_id=device_id,
        status="success",
        data=device_states[device_id],
        message=f"Command {command.command_type} executed successfully"
    )

@router.get("/code-examples/{example_type}")
async def get_code_example(example_type: str):
    """Get code examples for ADK implementation."""
    examples = {
        "android_app": {
            "title": "Android App with ADK Support",
            "description": "Example Android application that connects to an ADK accessory",
            "language": "java",
            "code": """
import android.hardware.usb.UsbAccessory;
import android.hardware.usb.UsbManager;
import android.content.Context;
import android.content.Intent;
import android.app.PendingIntent;

public class ADKExample {
    private UsbManager mUsbManager;
    private UsbAccessory mAccessory;
    private PendingIntent mPermissionIntent;
    
    public void initializeUSB(Context context) {
        // Get USB manager
        mUsbManager = (UsbManager) context.getSystemService(Context.USB_SERVICE);
        
        // Create a permission intent
        mPermissionIntent = PendingIntent.getBroadcast(context, 0, 
            new Intent("com.example.USB_PERMISSION"), 0);
            
        // Find the accessory
        UsbAccessory[] accessories = mUsbManager.getAccessoryList();
        if (accessories != null) {
            mAccessory = accessories[0];
            if (mAccessory != null) {
                if (mUsbManager.hasPermission(mAccessory)) {
                    openAccessory(mAccessory);
                } else {
                    mUsbManager.requestPermission(mAccessory, mPermissionIntent);
                }
            }
        }
    }
    
    private void openAccessory(UsbAccessory accessory) {
        // Open communication with the accessory
        // Implementation details...
    }
}
"""
        },
        "accessory_firmware": {
            "title": "Arduino-based ADK Accessory",
            "description": "Example firmware for an Arduino-based ADK accessory",
            "language": "cpp",
            "code": """

// Define the accessory
AndroidAccessory acc("Manufacturer", "Model", "Description",
                     "Version", "URI", "Serial");

// Buffer for incoming data
byte buffer[255];

void setup() {
  // Initialize serial for debugging
  Serial.begin(115200);
  Serial.println("Accessory setup");
  
  // Initialize the accessory
  acc.powerOn();
}

void loop() {
  // Check if device is connected
  if (acc.isConnected()) {
    // Read data from Android device
    int len = acc.read(buffer, sizeof(buffer), 1);
    
    if (len > 0) {
      // Process the command
      Serial.print("Received command: ");
      Serial.write(buffer, len);
      Serial.println();
      
      // Send a response back
      byte response[2] = {0x1, 0x2};
      acc.write(response, 2);
    }
  }
}
"""
        },
        "protocol_implementation": {
            "title": "ADK Protocol Implementation",
            "description": "Example of implementing the ADK protocol",
            "language": "cpp",
            "code": """
// ADK Protocol Implementation Example

// AOA Protocol Constants

// Vendor-specific control request for AOA
void sendAOAString(uint8_t index, const char* string) {
  // Send identifier strings to the Android device
  usb.controlRequest(
    USB_SETUP_HOST_TO_DEVICE | USB_SETUP_TYPE_VENDOR | USB_SETUP_RECIPIENT_DEVICE,
    AOA_SEND_IDENTIFIER,
    0,
    index,
    (uint8_t*)string,
    strlen(string) + 1
  );
}

void setupAOAMode() {
  uint16_t protocol;
  
  // Get the AOA protocol version
  usb.controlRequest(
    USB_SETUP_DEVICE_TO_HOST | USB_SETUP_TYPE_VENDOR | USB_SETUP_RECIPIENT_DEVICE,
    AOA_GET_PROTOCOL,
    0,
    0,
    (uint8_t*)&protocol,
    2
  );
  
  // Send accessory information
  sendAOAString(0, "Manufacturer");
  sendAOAString(1, "Model");
  sendAOAString(2, "Description");
  sendAOAString(3, "Version");
  sendAOAString(4, "URI");
  sendAOAString(5, "Serial");
  
  // Start accessory mode
  usb.controlRequest(
    USB_SETUP_HOST_TO_DEVICE | USB_SETUP_TYPE_VENDOR | USB_SETUP_RECIPIENT_DEVICE,
    AOA_START_ACCESSORY,
    0,
    0,
    NULL,
    0
  );
}
"""
        }
    }
    
    if example_type not in examples:
        raise HTTPException(status_code=404, detail="Example not found")
    
    return examples[example_type]
