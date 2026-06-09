import { Routes } from '@angular/router';
import { AssessmentFormComponent } from './features/assessment/pages/assessment-form.component';
import { LoginComponent } from './features/auth/pages/login.component';
import { RegisterComponent } from './features/auth/pages/register.component';
import { ChatPageComponent } from './features/chat/pages/chat-page.component';
import { ResultsPageComponent } from './features/results/pages/results-page.component';
import { authGuard } from './core/guards/auth.guard';
import { guestGuard } from './core/guards/guest.guard';

export const routes: Routes = [
	{ path: '', pathMatch: 'full', redirectTo: 'login' },
	{ path: 'login', component: LoginComponent, canActivate: [guestGuard] },
	{ path: 'register', component: RegisterComponent, canActivate: [guestGuard] },
	{ path: 'assessment', component: AssessmentFormComponent, canActivate: [authGuard] },
	{ path: 'chat', component: ChatPageComponent, canActivate: [authGuard] },
	{ path: 'results', component: ResultsPageComponent, canActivate: [authGuard] },
	{ path: '**', redirectTo: 'login' }
];
