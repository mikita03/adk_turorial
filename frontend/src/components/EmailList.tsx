import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { ScrollArea } from './ui/scroll-area';
import { Mail, Clock, User, Paperclip, AlertCircle, Info, CheckCircle, RefreshCw } from 'lucide-react';
import { EmailSummary } from '../types/email';
import { emailAPI } from '../services/api';

interface EmailListProps {
  onEmailSelect: (email: EmailSummary) => void;
  selectedEmailId?: string;
  onStatsUpdate?: (stats: {
    urgent: number;
    normal: number;
    fyi: number;
    replyNeeded: number;
  }) => void;
}

export const EmailList: React.FC<EmailListProps> = ({ onEmailSelect, selectedEmailId, onStatsUpdate }) => {
  const [emails, setEmails] = useState<EmailSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState({ total: 0, unread: 0 });

  useEffect(() => {
    loadEmails();
  }, []);

  const loadEmails = async (forceRefresh: boolean = false) => {
    try {
      if (forceRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      
      console.log('🔍 DEBUG: Starting email load request', { forceRefresh });
      const response = await emailAPI.getEmails(20, forceRefresh);
      console.log('🔍 DEBUG: Raw API response:', response);
      console.log('🔍 DEBUG: Response type:', typeof response);
      console.log('🔍 DEBUG: Response keys:', Object.keys(response || {}));
      
      if (!response) {
        throw new Error('API response is null or undefined');
      }
      
      if (!response.emails || !Array.isArray(response.emails)) {
        console.error('🔍 DEBUG: Invalid emails array:', response.emails);
        throw new Error(`Invalid emails array: ${typeof response.emails}`);
      }
      
      if (typeof response.total_count !== 'number') {
        console.error('🔍 DEBUG: Invalid total_count:', response.total_count);
        throw new Error(`Invalid total_count: ${typeof response.total_count}`);
      }
      
      if (typeof response.unread_count !== 'number') {
        console.error('🔍 DEBUG: Invalid unread_count:', response.unread_count);
        throw new Error(`Invalid unread_count: ${typeof response.unread_count}`);
      }
      
      console.log('🔍 DEBUG: Response validation passed, setting state');
      setEmails(response.emails);
      setStats({
        total: response.total_count,
        unread: response.unread_count,
      });
      
      if (onStatsUpdate) {
        onStatsUpdate({
          urgent: response.urgent_count,
          normal: response.normal_count,
          fyi: response.fyi_count,
          replyNeeded: response.reply_needed_count,
        });
      }
      console.log('🔍 DEBUG: State updated successfully');
      
    } catch (err: any) {
      console.error('🔍 DEBUG: Full error details:', err);
      console.error('🔍 DEBUG: Error name:', err?.name);
      console.error('🔍 DEBUG: Error message:', err?.message);
      console.error('🔍 DEBUG: Error stack:', err?.stack);
      
      if (err?.response) {
        console.error('🔍 DEBUG: HTTP response error:', err.response);
        console.error('🔍 DEBUG: Response status:', err.response.status);
        console.error('🔍 DEBUG: Response data:', err.response.data);
        setError(`メールの読み込みに失敗しました (HTTP ${err.response.status}): ${err.response.data?.detail || err.message}`);
      } else if (err?.request) {
        console.error('🔍 DEBUG: Network request error:', err.request);
        setError(`ネットワークエラー: ${err.message}`);
      } else {
        console.error('🔍 DEBUG: Other error:', err);
        setError(`エラー: ${err.message || 'Unknown error'}`);
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case 'normal':
        return <Info className="h-4 w-4 text-blue-500" />;
      case 'fyi':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      default:
        return <Info className="h-4 w-4 text-gray-500" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'normal':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'fyi':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'reply_needed':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'confirm_only':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'info':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) {
      return '今日';
    } else if (diffDays === 2) {
      return '昨日';
    } else if (diffDays <= 7) {
      return `${diffDays - 1}日前`;
    } else {
      return date.toLocaleDateString('ja-JP');
    }
  };

  if (loading) {
    return (
      <Card className="h-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Mail className="h-5 w-5" />
            メール一覧
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
              <p className="text-gray-500">メールを読み込み中...</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="h-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Mail className="h-5 w-5" />
            メール一覧
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <AlertCircle className="h-8 w-8 text-red-500 mx-auto mb-4" />
              <p className="text-red-500">{error}</p>
              <Button onClick={() => loadEmails()} className="mt-4">
                再試行
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="h-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Mail className="h-5 w-5" />
              メール一覧
            </CardTitle>
            <CardDescription>
              全{stats.total}件 • 要返信{stats.unread}件
            </CardDescription>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => loadEmails(true)}
            disabled={refreshing}
            className="flex items-center gap-2"
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
            {refreshing ? '更新中...' : '更新'}
          </Button>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <ScrollArea className="h-[600px]">
          <div className="space-y-2 p-4">
            {emails.map((email) => (
              <Card
                key={email.id}
                className={`cursor-pointer transition-colors hover:bg-gray-50 ${
                  selectedEmailId === email.id ? 'ring-2 ring-blue-500 bg-blue-50' : ''
                }`}
                onClick={() => onEmailSelect(email)}
              >
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <User className="h-4 w-4 text-gray-500" />
                      <span className="font-medium text-sm">{email.from_name}</span>
                      {email.has_attachment && (
                        <Paperclip className="h-4 w-4 text-gray-400" />
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      {getPriorityIcon(email.priority)}
                      <Clock className="h-4 w-4 text-gray-400" />
                      <span className="text-xs text-gray-500">
                        {formatDate(email.date)}
                      </span>
                    </div>
                  </div>

                  <h3 className="font-medium text-sm mb-2 line-clamp-1">
                    {email.subject}
                  </h3>

                  <p className="text-xs text-gray-600 mb-3 line-clamp-2">
                    {email.summary}
                  </p>

                  <div className="flex items-center gap-2 mb-2">
                    <Badge
                      variant="outline"
                      className={`text-xs ${getPriorityColor(email.priority)}`}
                    >
                      {email.priority === 'urgent' && '緊急'}
                      {email.priority === 'normal' && '通常'}
                      {email.priority === 'fyi' && 'FYI'}
                    </Badge>
                    <Badge
                      variant="outline"
                      className={`text-xs ${getCategoryColor(email.category)}`}
                    >
                      {email.category === 'reply_needed' && '要返信'}
                      {email.category === 'confirm_only' && '要確認'}
                      {email.category === 'info' && '情報共有'}
                    </Badge>
                  </div>

                  {email.important_entities.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {email.important_entities.slice(0, 3).map((entity, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {entity}
                        </Badge>
                      ))}
                      {email.important_entities.length > 3 && (
                        <Badge variant="secondary" className="text-xs">
                          +{email.important_entities.length - 3}
                        </Badge>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
};
