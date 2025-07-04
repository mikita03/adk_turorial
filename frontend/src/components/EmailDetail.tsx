import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Separator } from './ui/separator';
import { ScrollArea } from './ui/scroll-area';
import { Textarea } from './ui/textarea';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from './ui/dialog';
import { Mail, User, Calendar, Paperclip, Send, Edit, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { EmailSummary, EmailContent, ReplyDraft } from '../types/email';
import { emailAPI } from '../services/api';
import { wsService } from '../services/websocket';

interface EmailDetailProps {
  email: EmailSummary;
  onReplyCreated?: (draftId: string) => void;
}

export const EmailDetail: React.FC<EmailDetailProps> = ({ email, onReplyCreated }) => {
  const [emailContent, setEmailContent] = useState<EmailContent | null>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [replyDraft, setReplyDraft] = useState<ReplyDraft | null>(null);
  const [replyLoading, setReplyLoading] = useState(false);
  const [showReplyDialog, setShowReplyDialog] = useState(false);
  const [editedReply, setEditedReply] = useState('');
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    loadEmailDetail();
  }, [email.id]);

  useEffect(() => {
    wsService.onMessage('reply_generated', handleReplyGenerated);
    wsService.onMessage('processing_complete', handleProcessingComplete);
    wsService.onMessage('error', handleWebSocketError);

    return () => {
      wsService.offMessage('reply_generated');
      wsService.offMessage('processing_complete');
      wsService.offMessage('error');
    };
  }, []);

  const loadEmailDetail = async () => {
    try {
      setLoading(true);
      const response = await emailAPI.getEmailDetail(email.id);
      setEmailContent(response.email);
      setAnalysis(response.analysis);
    } catch (err) {
      console.error('Error loading email detail:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReplyGenerated = (message: any) => {
    if (message.email_id === email.id) {
      setReplyDraft(message.reply_result?.reply_draft);
      setEditedReply(message.reply_result?.reply_draft?.body || '');
      setReplyLoading(false);
      setShowReplyDialog(true);
    }
  };

  const handleProcessingComplete = (message: any) => {
    if (message.email_id === email.id) {
      setProcessing(false);
      loadEmailDetail();
    }
  };

  const handleWebSocketError = (message: any) => {
    console.error('WebSocket error:', message);
    setReplyLoading(false);
    setProcessing(false);
  };

  const generateReply = async () => {
    try {
      setReplyLoading(true);
      wsService.generateReply(email.id);
    } catch (err) {
      console.error('Error generating reply:', err);
      setReplyLoading(false);
    }
  };

  const processEmail = async () => {
    try {
      setProcessing(true);
      wsService.processEmail(email.id);
    } catch (err) {
      console.error('Error processing email:', err);
      setProcessing(false);
    }
  };

  const createDraft = async () => {
    try {
      if (!replyDraft) return;

      const response = await emailAPI.createReplyDraft(email.id);
      if (response.success && response.draft_id) {
        setShowReplyDialog(false);
        onReplyCreated?.(response.draft_id);
      }
    } catch (err) {
      console.error('Error creating draft:', err);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('ja-JP');
  };

  if (loading) {
    return (
      <Card className="h-full">
        <CardContent className="flex items-center justify-center h-64">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
            <p className="text-gray-500">メール詳細を読み込み中...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!emailContent) {
    return (
      <Card className="h-full">
        <CardContent className="flex items-center justify-center h-64">
          <div className="text-center">
            <AlertCircle className="h-8 w-8 text-red-500 mx-auto mb-4" />
            <p className="text-red-500">メールの読み込みに失敗しました</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card className="h-full">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <CardTitle className="flex items-center gap-2 mb-2">
                <Mail className="h-5 w-5" />
                {emailContent.subject}
              </CardTitle>
              <CardDescription className="space-y-1">
                <div className="flex items-center gap-2">
                  <User className="h-4 w-4" />
                  <span>{email.from_name} ({emailContent.from_email})</span>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  <span>{formatDate(emailContent.date)}</span>
                </div>
              </CardDescription>
            </div>
            <div className="flex flex-col gap-2">
              <div className="flex gap-2">
                <Badge
                  variant="outline"
                  className={
                    email.priority === 'urgent'
                      ? 'bg-red-100 text-red-800 border-red-200'
                      : email.priority === 'normal'
                      ? 'bg-blue-100 text-blue-800 border-blue-200'
                      : 'bg-green-100 text-green-800 border-green-200'
                  }
                >
                  {email.priority === 'urgent' && '緊急'}
                  {email.priority === 'normal' && '通常'}
                  {email.priority === 'fyi' && 'FYI'}
                </Badge>
                <Badge
                  variant="outline"
                  className={
                    email.category === 'reply_needed'
                      ? 'bg-orange-100 text-orange-800 border-orange-200'
                      : email.category === 'confirm_only'
                      ? 'bg-yellow-100 text-yellow-800 border-yellow-200'
                      : 'bg-gray-100 text-gray-800 border-gray-200'
                  }
                >
                  {email.category === 'reply_needed' && '要返信'}
                  {email.category === 'confirm_only' && '要確認'}
                  {email.category === 'info' && '情報共有'}
                </Badge>
              </div>
              {emailContent.attachments.length > 0 && (
                <Badge variant="outline" className="w-fit">
                  <Paperclip className="h-3 w-3 mr-1" />
                  添付 {emailContent.attachments.length}件
                </Badge>
              )}
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* AI Summary */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-medium text-blue-900 mb-2">AI要約</h3>
            <p className="text-blue-800 text-sm">{email.summary}</p>
            {email.important_entities.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                <span className="text-xs text-blue-700 mr-2">重要な情報:</span>
                {email.important_entities.map((entity, index) => (
                  <Badge key={index} variant="secondary" className="text-xs">
                    {entity}
                  </Badge>
                ))}
              </div>
            )}
          </div>

          <Separator />

          {/* Email Body */}
          <div>
            <h3 className="font-medium mb-2">メール本文</h3>
            <ScrollArea className="max-h-96 w-full border rounded-md p-4">
              <div className="whitespace-pre-wrap text-sm leading-relaxed">{emailContent.body}</div>
            </ScrollArea>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2 pt-4">
            <Button
              onClick={generateReply}
              disabled={replyLoading}
              className="flex-1"
            >
              {replyLoading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  返信案生成中...
                </>
              ) : (
                <>
                  <Send className="h-4 w-4 mr-2" />
                  返信案を生成
                </>
              )}
            </Button>
            <Button
              onClick={processEmail}
              disabled={processing}
              variant="outline"
            >
              {processing ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  処理中...
                </>
              ) : (
                <>
                  <Edit className="h-4 w-4 mr-2" />
                  再分析
                </>
              )}
            </Button>
          </div>

          {/* Analysis Results */}
          {analysis && (
            <div className="space-y-4">
              <Separator />
              <h3 className="font-medium">AI分析結果</h3>
              
              {/* Routing Decision */}
              {analysis.routing_decision && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-medium text-blue-900 mb-2">ルーティング判定</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="bg-blue-100 text-blue-800">
                        {analysis.routing_decision.priority}
                      </Badge>
                      <span className="text-blue-700">
                        使用エージェント: {analysis.routing_decision.agents_to_use?.join(', ')}
                      </span>
                    </div>
                    <p className="text-blue-800">{analysis.routing_decision.reasoning}</p>
                  </div>
                </div>
              )}

              {/* Agent Results */}
              {analysis.agent_results && Object.keys(analysis.agent_results).length > 0 && (
                <div className="space-y-3">
                  {Object.entries(analysis.agent_results).map(([agentName, result]: [string, any]) => (
                    <div key={agentName} className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                      <h4 className="font-medium text-gray-900 mb-2 capitalize">
                        {agentName === 'analyzer' && '分析エージェント'}
                        {agentName === 'responder' && '返信エージェント'}
                        {agentName === 'manager' && '管理エージェント'}
                      </h4>
                      
                      {result.success ? (
                        <div className="space-y-2 text-sm">
                          {result.analysis_details && (
                            <>
                              {result.analysis_details.key_points && (
                                <div>
                                  <span className="font-medium text-gray-700">重要ポイント:</span>
                                  <ul className="list-disc list-inside ml-2 text-gray-600">
                                    {result.analysis_details.key_points.map((point: string, idx: number) => (
                                      <li key={idx}>{point}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                              {result.analysis_details.action_required && (
                                <div>
                                  <span className="font-medium text-gray-700">必要なアクション:</span>
                                  <span className="ml-2 text-gray-600">{result.analysis_details.action_required}</span>
                                </div>
                              )}
                              {result.analysis_details.deadline && (
                                <div>
                                  <span className="font-medium text-gray-700">期限:</span>
                                  <span className="ml-2 text-gray-600">{result.analysis_details.deadline}</span>
                                </div>
                              )}
                            </>
                          )}
                        </div>
                      ) : (
                        <div className="flex items-center gap-2 text-red-600">
                          <AlertCircle className="h-4 w-4" />
                          <span className="text-sm">エラー: {result.error}</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Final Recommendation */}
              {analysis.final_recommendation && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h4 className="font-medium text-green-900 mb-2">最終推奨</h4>
                  <div className="space-y-2 text-sm">
                    <p className="text-green-800">{analysis.final_recommendation.summary}</p>
                    {analysis.final_recommendation.recommended_actions && (
                      <div className="flex flex-wrap gap-1">
                        {analysis.final_recommendation.recommended_actions.map((action: string, idx: number) => (
                          <Badge key={idx} variant="secondary" className="text-xs bg-green-100 text-green-800">
                            {action}
                          </Badge>
                        ))}
                      </div>
                    )}
                    {analysis.final_recommendation.next_steps && (
                      <p className="text-green-700 mt-2">
                        <span className="font-medium">次のステップ:</span> {analysis.final_recommendation.next_steps}
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Reply Dialog */}
      <Dialog open={showReplyDialog} onOpenChange={setShowReplyDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>返信案プレビュー</DialogTitle>
            <DialogDescription>
              AIが生成した返信案を確認・編集してください
            </DialogDescription>
          </DialogHeader>

          {replyDraft && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <label className="font-medium">宛先:</label>
                  <p className="text-gray-600">{replyDraft.to_email.join(', ')}</p>
                </div>
                <div>
                  <label className="font-medium">件名:</label>
                  <p className="text-gray-600">{replyDraft.subject}</p>
                </div>
              </div>

              <div>
                <label className="font-medium text-sm">返信内容:</label>
                <Textarea
                  value={editedReply}
                  onChange={(e) => setEditedReply(e.target.value)}
                  className="mt-1 min-h-[200px]"
                  placeholder="返信内容を入力してください..."
                />
              </div>

              <div className="flex items-center gap-2 text-xs text-gray-500">
                <CheckCircle className="h-4 w-4" />
                信頼度: {Math.round(replyDraft.confidence_score * 100)}%
                <span className="ml-2">理由: {replyDraft.reasoning}</span>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowReplyDialog(false)}>
              キャンセル
            </Button>
            <Button onClick={createDraft}>
              <Send className="h-4 w-4 mr-2" />
              下書きを作成
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};
