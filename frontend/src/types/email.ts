export interface EmailSummary {
  id: string;
  from_email: string;
  from_name: string;
  subject: string;
  date: string;
  summary: string;
  priority: 'urgent' | 'normal' | 'fyi';
  category: 'reply_needed' | 'confirm_only' | 'info';
  has_attachment: boolean;
  important_entities: string[];
}

export interface EmailContent {
  id: string;
  from_email: string;
  to_email: string[];
  cc_email: string[];
  subject: string;
  body: string;
  html_body?: string;
  date: string;
  attachments: any[];
}

export interface ReplyDraft {
  to_email: string[];
  cc_email: string[];
  subject: string;
  body: string;
  confidence_score: number;
  reasoning: string;
}

export interface AgentResponse {
  agent_name: string;
  task_type: string;
  success: boolean;
  result: any;
  error_message?: string;
  processing_time: number;
}

export interface WebSocketMessage {
  type: string;
  email_id?: string;
  timestamp: string;
  [key: string]: any;
}
