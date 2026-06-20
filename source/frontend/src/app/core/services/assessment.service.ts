import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

export interface AssessmentRequest {
  subject_scores: {
    toan: number; ngu_van: number; tieng_anh: number;
    vat_ly?: number; hoa_hoc?: number; sinh_hoc?: number;
  };
  holland_scores: {
    realistic: number; investigative: number; artistic: number;
    social: number; enterprising: number; conventional: number;
  };
  financial_level: 1 | 2 | 3;
  target_education_level?: string;
}

export interface CareerRecommendation {
  career_code: string;
  career_name: string;
  confidence: number;
  explanation: string;
  shap_factors?: Record<string, number> | null;
}

export interface AssessmentResponse {
  recommendations: CareerRecommendation[];
  holland_code: string;
  mode: string;
}

@Injectable({ providedIn: 'root' })
export class AssessmentService {
  private readonly latestRequestStorageKey = 'latest_assessment_request';
  private readonly latestResultStorageKey = 'latest_assessment_result';

  constructor(private api: ApiService) {}

  submit(request: AssessmentRequest): Observable<AssessmentResponse> {
    return this.api.post<AssessmentResponse>('/api/v1/assessment/submit', request);
  }

  saveLatestRequest(request: AssessmentRequest): void {
    try {
      localStorage.setItem(this.latestRequestStorageKey, JSON.stringify(request));
    } catch {
      // Ignore storage failures (e.g. private mode restrictions).
    }
  }

  getLatestRequest(): AssessmentRequest | null {
    try {
      const raw = localStorage.getItem(this.latestRequestStorageKey);
      if (!raw) {
        return null;
      }
      return JSON.parse(raw) as AssessmentRequest;
    } catch {
      return null;
    }
  }

  saveLatestResult(result: AssessmentResponse): void {
    try {
      localStorage.setItem(this.latestResultStorageKey, JSON.stringify(result));
    } catch {
      // Ignore storage failures (e.g. private mode restrictions).
    }
  }

  getLatestResult(): AssessmentResponse | null {
    try {
      const raw = localStorage.getItem(this.latestResultStorageKey);
      if (!raw) {
        return null;
      }
      return JSON.parse(raw) as AssessmentResponse;
    } catch {
      return null;
    }
  }

  clearLatestResult(): void {
    try {
      localStorage.removeItem(this.latestResultStorageKey);
    } catch {
      // Ignore storage failures.
    }
  }

  clearLatestRequest(): void {
    try {
      localStorage.removeItem(this.latestRequestStorageKey);
    } catch {
      // Ignore storage failures.
    }
  }
}
