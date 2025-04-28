import { Separator } from "../ui/separator";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";

const ADKIntroduction = () => {
  return (
    <div className="space-y-6">
      <section>
        <h2 className="text-2xl font-semibold mb-4">What is the Android Accessory Development Kit (ADK)?</h2>
        <p className="text-gray-700 dark:text-gray-300 mb-4">
          The Android Accessory Development Kit (ADK) is a reference implementation for hardware manufacturers 
          and hobbyists to create accessories for Android devices. It allows external USB hardware to interact 
          with Android-powered devices in a special accessory mode.
        </p>
        <p className="text-gray-700 dark:text-gray-300">
          The ADK is based on the Android Open Accessory (AOA) protocol, which allows Android devices to 
          communicate with external hardware accessories. When an Android device is connected to an accessory 
          that supports the AOA protocol, the Android device can enter "accessory mode" and the accessory acts 
          as the USB host, providing power and enumerating the Android device.
        </p>
      </section>
      
      <Separator />
      
      <section>
        <h2 className="text-2xl font-semibold mb-4">Key Features of ADK</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <CardHeader>
              <CardTitle>USB Accessory Mode</CardTitle>
            </CardHeader>
            <CardContent>
              <p>Allows Android devices to communicate with external hardware over USB, with the accessory acting as the USB host.</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>AOA Protocol</CardTitle>
            </CardHeader>
            <CardContent>
              <p>Standardized protocol for communication between Android devices and accessories, with versions AOAv1 and AOAv2.</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Hardware Integration</CardTitle>
            </CardHeader>
            <CardContent>
              <p>Enables integration with various hardware like sensors, controllers, displays, and other peripherals.</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Android API Support</CardTitle>
            </CardHeader>
            <CardContent>
              <p>Provides APIs for Android applications to discover, connect to, and communicate with accessories.</p>
            </CardContent>
          </Card>
        </div>
      </section>
      
      <Separator />
      
      <section>
        <h2 className="text-2xl font-semibold mb-4">How ADK Works</h2>
        <div className="space-y-4">
          <div>
            <h3 className="text-xl font-medium mb-2">1. Accessory Detection</h3>
            <p className="text-gray-700 dark:text-gray-300">
              When an Android device is connected to an accessory via USB, the accessory identifies itself as an 
              Android Open Accessory using vendor-specific USB control requests.
            </p>
          </div>
          
          <div>
            <h3 className="text-xl font-medium mb-2">2. Protocol Negotiation</h3>
            <p className="text-gray-700 dark:text-gray-300">
              The accessory and Android device negotiate the AOA protocol version to use. The accessory sends 
              identification strings to the Android device.
            </p>
          </div>
          
          <div>
            <h3 className="text-xl font-medium mb-2">3. Accessory Mode Activation</h3>
            <p className="text-gray-700 dark:text-gray-300">
              The Android device enters accessory mode, and the accessory becomes the USB host. The accessory 
              provides power to the Android device and enumerates it.
            </p>
          </div>
          
          <div>
            <h3 className="text-xl font-medium mb-2">4. Communication</h3>
            <p className="text-gray-700 dark:text-gray-300">
              The Android application and accessory communicate using bulk transfers over USB. The Android 
              application uses the USB accessory APIs to send and receive data.
            </p>
          </div>
        </div>
      </section>
      
      <Separator />
      
      <section>
        <h2 className="text-2xl font-semibold mb-4">ADK Versions</h2>
        <div className="space-y-4">
          <div>
            <h3 className="text-xl font-medium mb-2">AOAv1</h3>
            <p className="text-gray-700 dark:text-gray-300">
              The original version of the Android Open Accessory protocol, introduced in Android 3.1 (API level 12). 
              It supports basic accessory communication and is backported to Android 2.3.4 (API level 10) via the 
              Google APIs add-on library.
            </p>
          </div>
          
          <div>
            <h3 className="text-xl font-medium mb-2">AOAv2</h3>
            <p className="text-gray-700 dark:text-gray-300">
              Introduced in Android 4.1 (API level 16), AOAv2 adds support for audio output from the Android device 
              to the accessory and human interface device (HID) capabilities, allowing accessories to act as input 
              devices like keyboards or game controllers.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default ADKIntroduction;
