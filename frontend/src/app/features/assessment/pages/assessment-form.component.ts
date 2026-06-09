import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatToolbarModule } from '@angular/material/toolbar';
import { AuthService } from '../../../core/services/auth.service';
import { AssessmentRequest, AssessmentResponse, AssessmentService } from '../../../core/services/assessment.service';

@Component({
  selector: 'app-assessment-form',
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
    MatSelectModule,
    MatToolbarModule
  ],
  templateUrl: './assessment-form.component.html',
  styleUrl: './assessment-form.component.scss'
})
export class AssessmentFormComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private assessmentService = inject(AssessmentService);
  private router = inject(Router);

  isSubmitting = false;
  errorMessage = '';
  result: AssessmentResponse | null = null;

  readonly educationLevels = [
    { value: 'university', label: 'Đại học' },
    { value: 'college', label: 'Cao đẳng' },
    { value: 'vocational', label: 'Trung cấp/Nghề' }
  ];

  readonly form = this.fb.group({
    subject_scores: this.fb.group({
      toan: this.fb.nonNullable.control(7, [Validators.required, Validators.min(0), Validators.max(10)]),
      ngu_van: this.fb.nonNullable.control(7, [Validators.required, Validators.min(0), Validators.max(10)]),
      tieng_anh: this.fb.nonNullable.control(7, [Validators.required, Validators.min(0), Validators.max(10)]),
      vat_ly: this.fb.control<number | null>(null, [Validators.min(0), Validators.max(10)]),
      hoa_hoc: this.fb.control<number | null>(null, [Validators.min(0), Validators.max(10)]),
      sinh_hoc: this.fb.control<number | null>(null, [Validators.min(0), Validators.max(10)])
    }),
    holland_scores: this.fb.group({
      realistic: this.fb.nonNullable.control(0.5, [Validators.required, Validators.min(0), Validators.max(1)]),
      investigative: this.fb.nonNullable.control(0.5, [Validators.required, Validators.min(0), Validators.max(1)]),
      artistic: this.fb.nonNullable.control(0.5, [Validators.required, Validators.min(0), Validators.max(1)]),
      social: this.fb.nonNullable.control(0.5, [Validators.required, Validators.min(0), Validators.max(1)]),
      enterprising: this.fb.nonNullable.control(0.5, [Validators.required, Validators.min(0), Validators.max(1)]),
      conventional: this.fb.nonNullable.control(0.5, [Validators.required, Validators.min(0), Validators.max(1)])
    }),
    financial_level: this.fb.nonNullable.control<1 | 2 | 3>(2, [Validators.required]),
    target_education_level: this.fb.nonNullable.control('university')
  });

  logout(): void {
    this.authService.logout();
    void this.router.navigate(['/login']);
  }

  submitAssessment(): void {
    if (this.form.invalid || this.isSubmitting) {
      this.form.markAllAsTouched();
      return;
    }

    this.isSubmitting = true;
    this.errorMessage = '';

    const raw = this.form.getRawValue();
    const payload: AssessmentRequest = {
      subject_scores: {
        toan: raw.subject_scores.toan,
        ngu_van: raw.subject_scores.ngu_van,
        tieng_anh: raw.subject_scores.tieng_anh,
        vat_ly: raw.subject_scores.vat_ly ?? undefined,
        hoa_hoc: raw.subject_scores.hoa_hoc ?? undefined,
        sinh_hoc: raw.subject_scores.sinh_hoc ?? undefined
      },
      holland_scores: raw.holland_scores,
      financial_level: raw.financial_level,
      target_education_level: raw.target_education_level
    };

    this.assessmentService.saveLatestRequest(payload);

    this.assessmentService.submit(payload).subscribe({
      next: (res) => {
        this.result = res;
        this.assessmentService.saveLatestResult(res);
        this.isSubmitting = false;
        void this.router.navigate(['/results']);
      },
      error: () => {
        this.errorMessage = 'Không thể gửi bài đánh giá. Vui lòng thử lại.';
        this.isSubmitting = false;
      }
    });
  }

}
