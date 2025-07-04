import axios from 'axios';
import { EmailSummary, EmailContent, ReplyDraft } from '../types/email';

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface EmailListResponse {
  emails: EmailSummary[];
  total_count: number;
  unread_count: number;
  urgent_count: number;
  reply_needed_count: number;
  normal_count: number;
  fyi_count: number;
  cache_status: string;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  auth_url?: string;
}

export const authAPI = {
  getGoogleAuthUrl: async (): Promise<AuthResponse> => {
    const response = await api.get('/auth/google');
    return response.data;
  },

  checkAuthStatus: async (): Promise<{ authenticated: boolean; message: string }> => {
    const response = await api.get('/auth/status');
    return response.data;
  },

  handleAuthCallback: async (code: string): Promise<AuthResponse> => {
    const response = await api.post('/auth/callback', { code });
    return response.data;
  },
};

export const emailAPI = {
  getEmails: async (limit: number = 20, forceRefresh: boolean = false): Promise<EmailListResponse> => {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (forceRefresh) {
      params.append('force_refresh', 'true');
    }
    const response = await api.get(`/emails/?${params.toString()}`);
    return response.data;
  },

  getEmailDetail: async (emailId: string): Promise<{ email: EmailContent; analysis: any }> => {
    const response = await api.get(`/emails/${emailId}`);
    return response.data;
  },

  processEmail: async (emailId: string): Promise<any> => {
    const response = await api.post(`/emails/${emailId}/process`, {
      email_id: emailId,
      force_reprocess: false,
    });
    return response.data;
  },

  createReplyDraft: async (emailId: string): Promise<{ success: boolean; draft_id?: string; reply_draft?: ReplyDraft }> => {
    const response = await api.post(`/emails/${emailId}/reply`);
    return response.data;
  },
};

export const configAPI = {
  getConfig: async (): Promise<{ google_client_id: string; backend_url: string; frontend_url: string }> => {
    const response = await api.get('/config');
    return response.data;
  },
};

export default api;
