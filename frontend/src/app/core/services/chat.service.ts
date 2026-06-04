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

@Injectable({ providedIn: 'root' })
export class ChatService {
  constructor(private api: ApiService) {}

  sendMessage(request: ChatRequest): Observable<ChatResponse> {
    return this.api.post<ChatResponse>('/api/v1/chat/message', request);
  }
}
