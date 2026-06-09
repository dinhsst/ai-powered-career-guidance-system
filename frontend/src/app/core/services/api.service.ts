import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  get<T>(path: string): Observable<T> {
    return this.http.get<T>(`${this.baseUrl}${path}`, { headers: this.buildHeaders() });
  }

  post<T>(path: string, body: unknown): Observable<T> {
    if (body instanceof URLSearchParams) {
      return this.http.post<T>(
        `${this.baseUrl}${path}`,
        body.toString(),
        {
          headers: this.buildHeaders({
            'Content-Type': 'application/x-www-form-urlencoded'
          })
        }
      );
    }

    return this.http.post<T>(`${this.baseUrl}${path}`, body, { headers: this.buildHeaders() });
  }

  private buildHeaders(extraHeaders?: Record<string, string>): HttpHeaders {
    let headers = new HttpHeaders(extraHeaders ?? {});
    const token = localStorage.getItem('access_token');
    if (token) {
      headers = headers.set('Authorization', `Bearer ${token}`);
    }
    return headers;
  }
}
