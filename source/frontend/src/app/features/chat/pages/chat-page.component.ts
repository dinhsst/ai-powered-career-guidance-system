import { CommonModule } from '@angular/common';
import { AfterViewChecked, Component, ElementRef, ViewChild, inject } from '@angular/core';
import { FormControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatToolbarModule } from '@angular/material/toolbar';
import { AuthService } from '../../../core/services/auth.service';
import { ChatRequest, ChatService } from '../../../core/services/chat.service';

interface ChatMessageView {
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
}

@Component({
  selector: 'app-chat-page',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterLink,
    MatButtonModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatToolbarModule
  ],
  templateUrl: './chat-page.component.html',
  styleUrl: './chat-page.component.scss'
})
export class ChatPageComponent {
  @ViewChild('messagesContainer') private messagesContainer?: ElementRef<HTMLDivElement>;

  private authService = inject(AuthService);
  private chatService = inject(ChatService);
  private router = inject(Router);

  sessionId?: string;
  isSending = false;
  errorMessage = '';

  readonly messageControl = new FormControl('', {
    nonNullable: true,
    validators: [Validators.required, Validators.maxLength(1000)]
  });

  messages: ChatMessageView[] = [
    {
      role: 'assistant',
      content: 'Xin chào! Hãy hỏi mình về ngành học, nghề nghiệp và lộ trình phù hợp với bạn.'
    }
  ];

  ngOnInit(): void {
    const bootstrap = this.chatService.popPendingBootstrap();
    if (!bootstrap?.message) {
      return;
    }

    this.sendChatMessage(bootstrap.message, bootstrap.user_context);
  }

  logout(): void {
    this.authService.logout();
    void this.router.navigate(['/login']);
  }

  onComposerKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  sendMessage(): void {
    if (this.messageControl.invalid || this.isSending) {
      this.messageControl.markAsTouched();
      return;
    }

    const message = this.messageControl.value.trim();
    if (!message) {
      return;
    }

    this.sendChatMessage(message);
    this.messageControl.setValue('');
  }

  private sendChatMessage(message: string, userContext?: ChatRequest['user_context']): void {
    if (this.isSending) {
      return;
    }

    this.errorMessage = '';
    this.isSending = true;
    this.messages.push({ role: 'user', content: message });

    this.chatService.sendMessage({ message, session_id: this.sessionId, user_context: userContext }).subscribe({
      next: (response) => {
        this.sessionId = response.session_id;
        this.messages.push({
          role: 'assistant',
          content: response.reply,
          sources: this.normalizeSources(response.sources)
        });
        this.isSending = false;
      },
      error: () => {
        this.errorMessage = 'Hiện chưa thể lấy phản hồi từ AI. Vui lòng thử lại sau.';
        this.isSending = false;
      }
    });
  }

  private normalizeSources(sources: unknown[]): string[] {
    return (sources ?? []).map((source) => {
      if (typeof source === 'string') {
        return source;
      }

      if (source && typeof source === 'object') {
        const record = source as Record<string, unknown>;
        const title = record['title'];
        const sourceName = record['source'];
        const url = record['url'];

        if (typeof title === 'string' && title.trim()) {
          return title;
        }
        if (typeof sourceName === 'string' && sourceName.trim()) {
          return sourceName;
        }
        if (typeof url === 'string' && url.trim()) {
          return url;
        }
      }

      return JSON.stringify(source);
    });
  }

  private scrollToBottom(): void {
    const element = this.messagesContainer?.nativeElement;
    if (!element) {
      return;
    }
    element.scrollTop = element.scrollHeight;
  }

  ngAfterViewChecked(): void {
    this.scrollToBottom();
  }

}
