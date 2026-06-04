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
}

export interface AssessmentResponse {
  recommendations: CareerRecommendation[];
  holland_code: string;
  mode: string;
}

@Injectable({ providedIn: 'root' })
export class AssessmentService {
  constructor(private api: ApiService) {}

  submit(request: AssessmentRequest): Observable<AssessmentResponse> {
    return this.api.post<AssessmentResponse>('/api/v1/assessment/submit', request);
  }
}
