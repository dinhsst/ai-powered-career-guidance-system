import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { Router } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatToolbarModule } from '@angular/material/toolbar';
import { AuthService } from '../../../core/services/auth.service';
import { AssessmentRequest, AssessmentResponse, AssessmentService } from '../../../core/services/assessment.service';
import { ChatService } from '../../../core/services/chat.service';

interface XaiFactorView {
  key: string;
  label: string;
  value: number;
  widthPercent: number;
  isPositive: boolean;
}

@Component({
  selector: 'app-results-page',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatCardModule, MatToolbarModule],
  templateUrl: './results-page.component.html',
  styleUrl: './results-page.component.scss'
})
export class ResultsPageComponent implements OnInit {
  private authService = inject(AuthService);
  private assessmentService = inject(AssessmentService);
  private chatService = inject(ChatService);
  private router = inject(Router);

  result: AssessmentResponse | null = null;
  latestAssessmentRequest: AssessmentRequest | null = null;
  xaiFactors: XaiFactorView[] = [];

  ngOnInit(): void {
    this.result = this.assessmentService.getLatestResult();
    this.latestAssessmentRequest = this.assessmentService.getLatestRequest();
    this.xaiFactors = this.buildXaiFactors();
  }

  logout(): void {
    this.authService.logout();
    void this.router.navigate(['/login']);
  }

  goToAssessment(): void {
    void this.router.navigate(['/assessment']);
  }

  goToChat(): void {
    if (this.result && this.latestAssessmentRequest) {
      const topSubjects = this.getTopSubjects(this.latestAssessmentRequest.subject_scores);
      this.chatService.setPendingBootstrap({
        message:
          'Dựa trên kết quả đánh giá của tôi, hãy phân tích điểm mạnh, điểm cần cải thiện và đề xuất nghề nghiệp.',
        user_context: {
          holland_code: this.result.holland_code,
          financial_level: this.latestAssessmentRequest.financial_level,
          top_subjects: topSubjects
        }
      });
    }

    void this.router.navigate(['/chat']);
  }

  private getTopSubjects(subjectScores: AssessmentRequest['subject_scores']): string[] {
    const entries: Array<{ key: string; value: number }> = [
      { key: 'Toán', value: subjectScores.toan },
      { key: 'Ngữ văn', value: subjectScores.ngu_van },
      { key: 'Tiếng Anh', value: subjectScores.tieng_anh }
    ];

    if (typeof subjectScores.vat_ly === 'number') {
      entries.push({ key: 'Vật lý', value: subjectScores.vat_ly });
    }
    if (typeof subjectScores.hoa_hoc === 'number') {
      entries.push({ key: 'Hóa học', value: subjectScores.hoa_hoc });
    }
    if (typeof subjectScores.sinh_hoc === 'number') {
      entries.push({ key: 'Sinh học', value: subjectScores.sinh_hoc });
    }

    return entries
      .sort((a, b) => b.value - a.value)
      .slice(0, 3)
      .map((item) => item.key);
  }

  private buildXaiFactors(): XaiFactorView[] {
    const topRecommendation = this.result?.recommendations?.[0];
    const factors = topRecommendation?.shap_factors ?? this.buildFallbackFactors(topRecommendation?.career_code);
    if (!factors) {
      return [];
    }

    const rows = Object.entries(factors)
      .filter(([, value]) => typeof value === 'number' && Number.isFinite(value))
      .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
      .slice(0, 8);

    const maxAbs = rows.length ? Math.max(...rows.map(([, value]) => Math.abs(value))) : 1;

    return rows.map(([key, value]) => ({
      key,
      label: this.factorLabel(key),
      value,
      widthPercent: Math.max((Math.abs(value) / maxAbs) * 100, 6),
      isPositive: value >= 0,
    }));
  }

  private buildFallbackFactors(careerCode: string | undefined): Record<string, number> | null {
    const request = this.latestAssessmentRequest;
    if (!request || !careerCode) {
      return null;
    }

    const subject = request.subject_scores;
    const scienceScore = Math.max(subject.vat_ly ?? 0, subject.hoa_hoc ?? 0);
    const normalized = {
      realistic: request.holland_scores.realistic,
      investigative: request.holland_scores.investigative,
      artistic: request.holland_scores.artistic,
      social: request.holland_scores.social,
      enterprising: request.holland_scores.enterprising,
      conventional: request.holland_scores.conventional,
      math_score: subject.toan / 10,
      science_score: scienceScore / 10,
      literature_score: subject.ngu_van / 10,
      financial_level: request.financial_level / 3,
    };

    const weights: Record<string, Partial<Record<keyof typeof normalized, number>>> = {
      CNTT: { investigative: 0.4, realistic: 0.3, math_score: 0.3 },
      Kinh_te: { enterprising: 0.4, conventional: 0.3, math_score: 0.3 },
      Su_pham: { social: 0.5, artistic: 0.3, literature_score: 0.2 },
      Y_khoa: { investigative: 0.4, social: 0.4, science_score: 0.2 },
      Nghe_thuat: { artistic: 0.6, social: 0.2, literature_score: 0.2 },
    };

    const selected = weights[careerCode];
    if (!selected) {
      return null;
    }

    const factors: Record<string, number> = {};
    for (const [feature, weight] of Object.entries(selected)) {
      const value = normalized[feature as keyof typeof normalized] ?? 0;
      factors[feature] = Number((value * (weight ?? 0)).toFixed(4));
    }

    return factors;
  }

  private factorLabel(featureName: string): string {
    const map: Record<string, string> = {
      realistic: 'Realistic (R)',
      investigative: 'Investigative (I)',
      artistic: 'Artistic (A)',
      social: 'Social (S)',
      enterprising: 'Enterprising (E)',
      conventional: 'Conventional (C)',
      math_score: 'Điểm Toán',
      science_score: 'Điểm KHTN',
      literature_score: 'Điểm Ngữ văn',
      financial_level: 'Điều kiện tài chính',
    };

    return map[featureName] ?? featureName;
  }

}
