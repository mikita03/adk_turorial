import { Tabs, TabsContent, TabsList, TabsTrigger } from "../ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import ADKIntroduction from './ADKIntroduction';
import DeviceSimulator from './DeviceSimulator';
import CodeExamples from './CodeExamples';

const ADKTutorial = () => {
  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-6">Android Accessory Development Kit (ADK) Tutorial</h1>
      
      <Tabs defaultValue="introduction" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="introduction">Introduction</TabsTrigger>
          <TabsTrigger value="simulator">Device Simulator</TabsTrigger>
          <TabsTrigger value="code-examples">Code Examples</TabsTrigger>
        </TabsList>
        
        <TabsContent value="introduction">
          <Card>
            <CardHeader>
              <CardTitle>Introduction to ADK</CardTitle>
              <CardDescription>
                Learn about the Android Accessory Development Kit and how it works
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ADKIntroduction />
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="simulator">
          <Card>
            <CardHeader>
              <CardTitle>ADK Device Simulator</CardTitle>
              <CardDescription>
                Interact with simulated ADK devices to understand how they work
              </CardDescription>
            </CardHeader>
            <CardContent>
              <DeviceSimulator />
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="code-examples">
          <Card>
            <CardHeader>
              <CardTitle>ADK Code Examples</CardTitle>
              <CardDescription>
                View code examples for implementing ADK in your projects
              </CardDescription>
            </CardHeader>
            <CardContent>
              <CodeExamples />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ADKTutorial;
