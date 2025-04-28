import { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";

interface CodeExample {
  title: string;
  description: string;
  language: string;
  code: string;
}

const CodeExamples = () => {
  const [examples, setExamples] = useState<Record<string, CodeExample>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchExamples = async () => {
      try {
        const exampleTypes = ['android_app', 'accessory_firmware', 'protocol_implementation'];
        const fetchedExamples: Record<string, CodeExample> = {};
        
        for (const type of exampleTypes) {
          const response = await fetch(`http://localhost:8000/adk/code-examples/${type}`);
          if (!response.ok) {
            throw new Error(`Failed to fetch ${type} example`);
          }
          const data = await response.json();
          fetchedExamples[type] = data;
        }
        
        setExamples(fetchedExamples);
        setLoading(false);
      } catch (err) {
        setError('Error fetching code examples. Using simulated examples.');
        setLoading(false);
        
        setExamples({
          android_app: {
            title: "Android App with ADK Support",
            description: "Example Android application that connects to an ADK accessory",
            language: "java",
            code: `
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
        mUsbManager = (UsbManager) context.getSystemService(Context.USB_SERVICE);
        
        mPermissionIntent = PendingIntent.getBroadcast(context, 0, 
            new Intent("com.example.USB_PERMISSION"), 0);
            
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
    }
}`
          },
          accessory_firmware: {
            title: "Arduino-based ADK Accessory",
            description: "Example firmware for an Arduino-based ADK accessory",
            language: "cpp",
            code: `
#include <AndroidAccessory.h>

AndroidAccessory acc("Manufacturer", "Model", "Description",
                     "Version", "URI", "Serial");

byte buffer[255];

void setup() {
  Serial.begin(115200);
  Serial.println("Accessory setup");
  
  acc.powerOn();
}

void loop() {
  if (acc.isConnected()) {
    int len = acc.read(buffer, sizeof(buffer), 1);
    
    if (len > 0) {
      Serial.print("Received command: ");
      Serial.write(buffer, len);
      Serial.println();
      
      byte response[2] = {0x1, 0x2};
      acc.write(response, 2);
    }
  }
}`
          },
          protocol_implementation: {
            title: "ADK Protocol Implementation",
            description: "Example of implementing the ADK protocol",
            language: "cpp",
            code: `

#define AOA_GET_PROTOCOL        51
#define AOA_SEND_IDENTIFIER     52
#define AOA_START_ACCESSORY     53
#define AOA_REGISTER_HID        54
#define AOA_UNREGISTER_HID      55
#define AOA_SET_HID_REPORT_DESC 56
#define AOA_SEND_HID_EVENT      57
#define AOA_AUDIO_SUPPORT       58

void sendAOAString(uint8_t index, const char* string) {
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
  
  usb.controlRequest(
    USB_SETUP_DEVICE_TO_HOST | USB_SETUP_TYPE_VENDOR | USB_SETUP_RECIPIENT_DEVICE,
    AOA_GET_PROTOCOL,
    0,
    0,
    (uint8_t*)&protocol,
    2
  );
  
  sendAOAString(0, "Manufacturer");
  sendAOAString(1, "Model");
  sendAOAString(2, "Description");
  sendAOAString(3, "Version");
  sendAOAString(4, "URI");
  sendAOAString(5, "Serial");
  
  usb.controlRequest(
    USB_SETUP_HOST_TO_DEVICE | USB_SETUP_TYPE_VENDOR | USB_SETUP_RECIPIENT_DEVICE,
    AOA_START_ACCESSORY,
    0,
    0,
    NULL,
    0
  );
}`
          }
        });
      }
    };

    fetchExamples();
  }, []);

  const formatCode = (code: string) => {
    return code.trim();
  };

  if (loading) {
    return <div>Loading code examples...</div>;
  }

  return (
    <div className="space-y-6">
      <p className="text-gray-700 dark:text-gray-300 mb-6">
        These code examples demonstrate how to implement ADK in different contexts. 
        You can use these as a starting point for your own ADK projects.
      </p>
      
      <Tabs defaultValue="android_app" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="android_app">Android App</TabsTrigger>
          <TabsTrigger value="accessory_firmware">Accessory Firmware</TabsTrigger>
          <TabsTrigger value="protocol_implementation">Protocol Implementation</TabsTrigger>
        </TabsList>
        
        {Object.entries(examples).map(([key, example]) => (
          <TabsContent key={key} value={key}>
            <Card>
              <CardHeader>
                <CardTitle>{example.title}</CardTitle>
                <CardDescription>{example.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <pre className="bg-gray-100 dark:bg-gray-800 p-4 rounded-md overflow-x-auto">
                  <code>{formatCode(example.code)}</code>
                </pre>
              </CardContent>
            </Card>
          </TabsContent>
        ))}
      </Tabs>
      
      {error && (
        <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 mt-4" role="alert">
          <p>{error}</p>
        </div>
      )}
    </div>
  );
};

export default CodeExamples;
