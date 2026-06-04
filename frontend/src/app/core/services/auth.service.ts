import { Injectable } from '@angular/core';
import { Observable, tap } from 'rxjs';
import { ApiService } from './api.service';

export interface LoginRequest { username: string; password: string; }
export interface RegisterRequest { email: string; password: string; full_name: string; }
export interface TokenResponse { access_token: string; token_type: string; }

@Injectable({ providedIn: 'root' })
export class AuthService {
  constructor(private api: ApiService) {}

  login(req: LoginRequest): Observable<TokenResponse> {
    const form = new URLSearchParams();
    form.set('username', req.username);
    form.set('password', req.password);
    return this.api.post<TokenResponse>('/api/v1/auth/login', form).pipe(
      tap(res => localStorage.setItem('access_token', res.access_token))
    );
  }

  register(req: RegisterRequest): Observable<unknown> {
    return this.api.post('/api/v1/auth/register', req);
  }

  logout(): void {
    localStorage.removeItem('access_token');
  }

  isLoggedIn(): boolean {
    return !!localStorage.getItem('access_token');
  }
}
