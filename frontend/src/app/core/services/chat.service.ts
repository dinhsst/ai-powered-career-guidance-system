import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

export interface ChatRequest {
  message: string;
  session_id?: string;
  user_context?: {
    holland_code?: string;
    financial_level?: number;
    top_subjects?: string[];
  };
}

export interface ChatResponse {
  reply: string;
  sources: unknown[];
  mode: string;
  session_id: string;
}

export interface ChatBootstrapPayload {
  message: string;
  user_context?: ChatRequest['user_context'];
}

@Injectable({ providedIn: 'root' })
export class ChatService {
  private readonly pendingBootstrapStorageKey = 'pending_chat_bootstrap';

  constructor(private api: ApiService) {}

  sendMessage(request: ChatRequest): Observable<ChatResponse> {
    return this.api.post<ChatResponse>('/api/v1/chat/message', request);
  }

  setPendingBootstrap(payload: ChatBootstrapPayload): void {
    try {
      sessionStorage.setItem(this.pendingBootstrapStorageKey, JSON.stringify(payload));
    } catch {
      // Ignore storage failures.
    }
  }

  popPendingBootstrap(): ChatBootstrapPayload | null {
    try {
      const raw = sessionStorage.getItem(this.pendingBootstrapStorageKey);
      if (!raw) {
        return null;
      }
      sessionStorage.removeItem(this.pendingBootstrapStorageKey);
      return JSON.parse(raw) as ChatBootstrapPayload;
    } catch {
      return null;
    }
  }
}
