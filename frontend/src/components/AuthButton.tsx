import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Mail, CheckCircle, AlertCircle, ExternalLink } from 'lucide-react';
import { authAPI } from '../services/api';

interface AuthButtonProps {
  onAuthSuccess: () => void;
}

export const AuthButton: React.FC<AuthButtonProps> = ({ onAuthSuccess }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [authLoading, setAuthLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    checkAuthStatus();
    
    const urlParams = new URLSearchParams(window.location.search);
    const authResult = urlParams.get('auth');
    const authCode = urlParams.get('code');
    
    if (authResult === 'success') {
      setIsAuthenticated(true);
      onAuthSuccess();
      window.history.replaceState({}, document.title, window.location.pathname);
    } else if (authResult === 'error') {
      setError('認証に失敗しました');
      window.history.replaceState({}, document.title, window.location.pathname);
    } else if (authCode) {
      handleAuthCode(authCode);
    }
  }, [onAuthSuccess]);

  const checkAuthStatus = async () => {
    try {
      const response = await authAPI.checkAuthStatus();
      setIsAuthenticated(response.authenticated);
      if (response.authenticated) {
        onAuthSuccess();
      }
    } catch (err) {
      console.error('Error checking auth status:', err);
      setError('認証状態の確認に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const handleAuthCode = async (code: string) => {
    try {
      setAuthLoading(true);
      const response = await authAPI.handleAuthCallback(code);
      if (response.success) {
        setIsAuthenticated(true);
        onAuthSuccess();
        window.history.replaceState({}, document.title, window.location.pathname);
      } else {
        setError('認証に失敗しました');
      }
    } catch (err) {
      console.error('Error handling auth code:', err);
      setError('認証処理中にエラーが発生しました');
    } finally {
      setAuthLoading(false);
    }
  };

  const handleGoogleAuth = async () => {
    try {
      setAuthLoading(true);
      setError(null);
      
      const response = await authAPI.getGoogleAuthUrl();
      if (response.success && response.auth_url) {
        window.location.href = response.auth_url;
      } else {
        setError('認証URLの取得に失敗しました');
      }
    } catch (err) {
      console.error('Error initiating Google auth:', err);
      setError('認証の開始に失敗しました');
    } finally {
      setAuthLoading(false);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center p-6">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-900"></div>
          <span className="ml-2">認証状態を確認中...</span>
        </CardContent>
      </Card>
    );
  }

  if (isAuthenticated) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-500" />
            Gmail認証完了
          </CardTitle>
          <CardDescription>
            Gmailアカウントに正常に接続されています
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Badge variant="outline" className="bg-green-100 text-green-800 border-green-200">
            <Mail className="h-4 w-4 mr-1" />
            認証済み
          </Badge>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Mail className="h-5 w-5" />
          Gmail秘書エージェント
        </CardTitle>
        <CardDescription>
          Gmailアカウントに接続してメール管理を開始してください
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {error && (
          <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-md">
            <AlertCircle className="h-4 w-4 text-red-500" />
            <span className="text-red-700 text-sm">{error}</span>
          </div>
        )}
        
        <div className="space-y-3">
          <div className="text-sm text-gray-600">
            <p>このアプリケーションは以下の機能を提供します：</p>
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li>メールの自動要約・分類</li>
              <li>AI による返信案の生成</li>
              <li>添付ファイルの自動整理</li>
              <li>学習機能による継続的な改善</li>
            </ul>
          </div>
          
          <Button 
            onClick={handleGoogleAuth} 
            disabled={authLoading}
            className="w-full"
            size="lg"
          >
            {authLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                認証中...
              </>
            ) : (
              <>
                <ExternalLink className="h-4 w-4 mr-2" />
                Googleアカウントで認証
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};
