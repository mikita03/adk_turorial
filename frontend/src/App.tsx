import { useState, useEffect } from 'react';
import { AuthButton } from './components/AuthButton';
import { EmailList } from './components/EmailList';
import { EmailDetail } from './components/EmailDetail';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Badge } from './components/ui/badge';
import { Mail, Bot, Activity, CheckCircle } from 'lucide-react';
import { EmailSummary } from './types/email';
import { wsService } from './services/websocket';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [selectedEmail, setSelectedEmail] = useState<EmailSummary | null>(null);
  const [wsConnected, setWsConnected] = useState(false);
  const [stats, setStats] = useState({
    urgent: 0,
    normal: 0,
    fyi: 0,
    replyNeeded: 0
  });

  useEffect(() => {
    if (isAuthenticated) {
      connectWebSocket();
    }
  }, [isAuthenticated]);

  const connectWebSocket = async () => {
    try {
      await wsService.connect();
      setWsConnected(true);
      
      const pingInterval = setInterval(() => {
        if (wsService) {
          wsService.ping();
        }
      }, 30000);

      return () => {
        clearInterval(pingInterval);
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      setWsConnected(false);
    }
  };

  const handleAuthSuccess = () => {
    setIsAuthenticated(true);
  };

  const handleEmailSelect = (email: EmailSummary) => {
    setSelectedEmail(email);
  };

  const handleReplyCreated = (draftId: string) => {
    console.log('Reply draft created:', draftId);
  };

  const handleStatsUpdate = (newStats: {
    urgent: number;
    normal: number;
    fyi: number;
    replyNeeded: number;
  }) => {
    setStats(newStats);
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <div className="flex items-center justify-center mb-4">
              <Bot className="h-12 w-12 text-blue-600" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Gmail秘書エージェント
            </h1>
            <p className="text-gray-600">
              AIがあなたのメール管理をサポートします
            </p>
          </div>
          <AuthButton onAuthSuccess={handleAuthSuccess} />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Bot className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-xl font-semibold text-gray-900">
                Gmail秘書エージェント
              </h1>
              <p className="text-sm text-gray-500">
                AI-powered email management system
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Activity className={`h-4 w-4 ${wsConnected ? 'text-green-500' : 'text-red-500'}`} />
              <span className="text-sm text-gray-600">
                {wsConnected ? 'リアルタイム接続中' : '接続エラー'}
              </span>
            </div>
            <Badge variant="outline" className="bg-green-100 text-green-800 border-green-200">
              <CheckCircle className="h-3 w-3 mr-1" />
              認証済み
            </Badge>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-6">
        {/* Stats Dashboard */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">緊急メール</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{stats.urgent}</div>
              <p className="text-xs text-gray-500">要即対応</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">要返信</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">{stats.replyNeeded}</div>
              <p className="text-xs text-gray-500">返信が必要</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">通常メール</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">{stats.normal}</div>
              <p className="text-xs text-gray-500">確認推奨</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">FYI</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{stats.fyi}</div>
              <p className="text-xs text-gray-500">情報共有</p>
            </CardContent>
          </Card>
        </div>

        {/* Email Management Interface */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Email List */}
          <div className="space-y-4">
            <EmailList
              onEmailSelect={handleEmailSelect}
              selectedEmailId={selectedEmail?.id}
              onStatsUpdate={handleStatsUpdate}
            />
          </div>

          {/* Email Detail */}
          <div className="space-y-4">
            {selectedEmail ? (
              <EmailDetail
                email={selectedEmail}
                onReplyCreated={handleReplyCreated}
              />
            ) : (
              <Card className="h-full">
                <CardContent className="flex items-center justify-center h-64">
                  <div className="text-center">
                    <Mail className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      メールを選択してください
                    </h3>
                    <p className="text-gray-500">
                      左側のリストからメールを選択すると詳細が表示されます
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
