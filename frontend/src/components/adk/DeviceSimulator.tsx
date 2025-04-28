import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Button } from "../ui/button";
import { Slider } from "../ui/slider";
import { Switch } from "../ui/switch";
import { Label } from "../ui/label";

interface Device {
  id: string;
  name: string;
  type: string;
  description: string;
  connection_type: string;
  protocol_version: string;
  features: string[];
}

interface DeviceState {
  connected: boolean;
  [key: string]: any;
}

const DeviceSimulator = () => {
  const [devices, setDevices] = useState<Device[]>([]);
  const [selectedDevice, setSelectedDevice] = useState<string | null>(null);
  const [deviceState, setDeviceState] = useState<DeviceState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDevices = async () => {
      try {
        const response = await fetch('http://localhost:8000/adk/devices');
        if (!response.ok) {
          throw new Error('Failed to fetch devices');
        }
        const data = await response.json();
        setDevices(data);
        setLoading(false);
      } catch (err) {
        setError('Error fetching devices. This is a simulation, so no real hardware is required.');
        setLoading(false);
        
        setDevices([
          {
            id: "adk-001",
            name: "LED Controller",
            type: "lighting",
            description: "RGB LED controller for Android devices",
            connection_type: "USB",
            protocol_version: "AOAv2",
            features: ["color_control", "brightness_control", "pattern_selection"]
          },
          {
            id: "adk-002",
            name: "Temperature Sensor",
            type: "sensor",
            description: "Temperature and humidity sensor for Android devices",
            connection_type: "Bluetooth",
            protocol_version: "AOAv1",
            features: ["temperature_reading", "humidity_reading", "data_logging"]
          },
          {
            id: "adk-003",
            name: "Game Controller",
            type: "input",
            description: "Game controller for Android devices",
            connection_type: "USB",
            protocol_version: "AOAv2",
            features: ["buttons", "joystick", "accelerometer", "vibration"]
          }
        ]);
      }
    };

    fetchDevices();
  }, []);

  useEffect(() => {
    if (selectedDevice) {
      const fetchDeviceState = async () => {
        try {
          const response = await fetch(`http://localhost:8000/adk/devices/${selectedDevice}/state`);
          if (!response.ok) {
            throw new Error('Failed to fetch device state');
          }
          const data = await response.json();
          setDeviceState(data);
        } catch (err) {
          setError('Error fetching device state. Using simulated data.');
          
          if (selectedDevice === 'adk-001') {
            setDeviceState({
              connected: false,
              color: "#FFFFFF",
              brightness: 50,
              pattern: "solid"
            });
          } else if (selectedDevice === 'adk-002') {
            setDeviceState({
              connected: false,
              temperature: 22.5,
              humidity: 45.0,
              logging: false
            });
          } else if (selectedDevice === 'adk-003') {
            setDeviceState({
              connected: false,
              button_states: {},
              joystick_position: { x: 0, y: 0 },
              vibration: 0
            });
          }
        }
      };

      fetchDeviceState();
    }
  }, [selectedDevice]);

  const connectDevice = async () => {
    if (!selectedDevice || !deviceState) return;
    
    try {
      const response = await fetch(`http://localhost:8000/adk/devices/${selectedDevice}/connect`, {
        method: 'POST'
      });
      
      if (!response.ok) {
        throw new Error('Failed to connect device');
      }
      
      setDeviceState({ ...deviceState, connected: true });
    } catch (err) {
      setError('Error connecting device. This is a simulation.');
      setDeviceState({ ...deviceState, connected: true });
    }
  };

  const disconnectDevice = async () => {
    if (!selectedDevice || !deviceState) return;
    
    try {
      const response = await fetch(`http://localhost:8000/adk/devices/${selectedDevice}/disconnect`, {
        method: 'POST'
      });
      
      if (!response.ok) {
        throw new Error('Failed to disconnect device');
      }
      
      setDeviceState({ ...deviceState, connected: false });
    } catch (err) {
      setError('Error disconnecting device. This is a simulation.');
      setDeviceState({ ...deviceState, connected: false });
    }
  };

  const sendCommand = async (commandType: string, parameters: any) => {
    if (!selectedDevice || !deviceState || !deviceState.connected) return;
    
    try {
      const response = await fetch(`http://localhost:8000/adk/devices/${selectedDevice}/command`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          device_id: selectedDevice,
          command_type: commandType,
          parameters
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to send command');
      }
      
      const data = await response.json();
      setDeviceState(data.data);
    } catch (err) {
      setError('Error sending command. This is a simulation.');
      
      if (selectedDevice === 'adk-001') {
        if (commandType === 'set_brightness') {
          setDeviceState({ ...deviceState, brightness: parameters.brightness });
        } else if (commandType === 'set_color') {
          setDeviceState({ ...deviceState, color: parameters.color });
        } else if (commandType === 'set_pattern') {
          setDeviceState({ ...deviceState, pattern: parameters.pattern });
        }
      } else if (selectedDevice === 'adk-002') {
        if (commandType === 'start_logging') {
          setDeviceState({ ...deviceState, logging: true });
        } else if (commandType === 'stop_logging') {
          setDeviceState({ ...deviceState, logging: false });
        }
      } else if (selectedDevice === 'adk-003') {
        if (commandType === 'set_vibration') {
          setDeviceState({ ...deviceState, vibration: parameters.intensity });
        }
      }
    }
  };

  if (loading) {
    return <div>Loading devices...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {devices.map(device => (
          <Card 
            key={device.id} 
            className={`cursor-pointer ${selectedDevice === device.id ? 'border-primary' : ''}`}
            onClick={() => setSelectedDevice(device.id)}
          >
            <CardHeader>
              <CardTitle>{device.name}</CardTitle>
              <CardDescription>{device.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div><strong>Type:</strong> {device.type}</div>
                <div><strong>Connection:</strong> {device.connection_type}</div>
                <div><strong>Protocol:</strong> {device.protocol_version}</div>
                <div>
                  <strong>Features:</strong>
                  <ul className="list-disc pl-5">
                    {device.features.map(feature => (
                      <li key={feature}>{feature.replace('_', ' ')}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {selectedDevice && deviceState && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>
              {devices.find(d => d.id === selectedDevice)?.name} Control Panel
            </CardTitle>
            <CardDescription>
              {deviceState.connected ? 'Connected' : 'Disconnected'} - 
              {devices.find(d => d.id === selectedDevice)?.connection_type} - 
              {devices.find(d => d.id === selectedDevice)?.protocol_version}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex space-x-4 mb-6">
              {!deviceState.connected ? (
                <Button onClick={connectDevice}>Connect Device</Button>
              ) : (
                <Button onClick={disconnectDevice} variant="destructive">Disconnect Device</Button>
              )}
            </div>

            {deviceState.connected && (
              <div className="mt-4">
                {selectedDevice === 'adk-001' && (
                  <div className="space-y-6">
                    <div className="space-y-2">
                      <Label>Brightness: {deviceState.brightness}%</Label>
                      <Slider 
                        value={[deviceState.brightness]} 
                        min={0} 
                        max={100} 
                        step={1}
                        onValueChange={(value) => sendCommand('set_brightness', { brightness: value[0] })}
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label>Color</Label>
                      <div className="flex items-center space-x-2">
                        <input 
                          type="color" 
                          value={deviceState.color} 
                          onChange={(e) => sendCommand('set_color', { color: e.target.value })}
                          className="w-12 h-12 rounded"
                        />
                        <span>{deviceState.color}</span>
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <Label>Pattern</Label>
                      <div className="flex space-x-2">
                        {['solid', 'blink', 'pulse', 'rainbow'].map(pattern => (
                          <Button 
                            key={pattern}
                            variant={deviceState.pattern === pattern ? "default" : "outline"}
                            onClick={() => sendCommand('set_pattern', { pattern })}
                          >
                            {pattern}
                          </Button>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
                
                {selectedDevice === 'adk-002' && (
                  <div className="space-y-6">
                    <div className="grid grid-cols-2 gap-4">
                      <Card>
                        <CardHeader>
                          <CardTitle>Temperature</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="text-4xl font-bold">{deviceState.temperature}°C</div>
                        </CardContent>
                      </Card>
                      
                      <Card>
                        <CardHeader>
                          <CardTitle>Humidity</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="text-4xl font-bold">{deviceState.humidity}%</div>
                        </CardContent>
                      </Card>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <Switch 
                        checked={deviceState.logging} 
                        onCheckedChange={(checked) => {
                          if (checked) {
                            sendCommand('start_logging', {});
                          } else {
                            sendCommand('stop_logging', {});
                          }
                        }}
                      />
                      <Label>Data Logging</Label>
                    </div>
                  </div>
                )}
                
                {selectedDevice === 'adk-003' && (
                  <div className="space-y-6">
                    <div className="space-y-2">
                      <Label>Vibration Intensity: {deviceState.vibration}%</Label>
                      <Slider 
                        value={[deviceState.vibration]} 
                        min={0} 
                        max={100} 
                        step={1}
                        onValueChange={(value) => sendCommand('set_vibration', { intensity: value[0] })}
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label>Joystick Position</Label>
                      <div className="relative h-48 w-48 border rounded-full mx-auto">
                        <div 
                          className="absolute w-6 h-6 bg-primary rounded-full transform -translate-x-1/2 -translate-y-1/2"
                          style={{ 
                            left: `${(deviceState.joystick_position.x + 1) * 50}%`, 
                            top: `${(deviceState.joystick_position.y + 1) * 50}%` 
                          }}
                        />
                      </div>
                      <div className="text-center mt-2">
                        X: {deviceState.joystick_position.x.toFixed(2)}, Y: {deviceState.joystick_position.y.toFixed(2)}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {error && (
        <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 mt-4" role="alert">
          <p>{error}</p>
          <p className="text-sm mt-2">Note: This is a simulated environment. No real hardware is required.</p>
        </div>
      )}
    </div>
  );
};

export default DeviceSimulator;
