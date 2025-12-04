import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import {
  IonContent,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonButtons,
  IonBackButton,
  IonButton,
  IonIcon,
  IonSelect,
  IonSelectOption,
  IonCard,
  IonCardContent,
  IonText,
  IonChip,
  IonLabel,
  IonSkeletonText,
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import {
  refresh,
  checkmarkCircle,
  checkmarkCircleOutline,
  chevronUp,
  chevronDown,
  bookmarkOutline,
  bookmark, alertCircle } from 'ionicons/icons';
import { Subject, takeUntil } from 'rxjs';
import { ExamQuestionService } from '../services/exam-question.service';
import { ExamQuestion, ExamPdf } from '../models';

// Configuración de PDFs disponibles
const AVAILABLE_PDFS: ExamPdf[] = [
  { id: 1, filename: 'az-204.pdf', displayName: 'AZ-204: Developing Solutions for Microsoft Azure', path: '/assets/pdfs/az-204.pdf' },
  { id: 2, filename: 'dp-300.pdf', displayName: 'DP-300: Administering Microsoft Azure SQL Solutions', path: '/assets/pdfs/dp-300.pdf' },
];

interface ReviewState {
  examId: number;
  currentQuestion: number;
  completedQuestions: number[];
  timestamp: number;
}

@Component({
  selector: 'app-exam-review',
  templateUrl: './exam-review.page.html',
  styleUrls: ['./exam-review.page.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    IonContent,
    IonHeader,
    IonToolbar,
    IonTitle,
    IonButtons,
    IonBackButton,
    IonButton,
    IonIcon,
    IonSelect,
    IonSelectOption,
    IonCard,
    IonCardContent,
    IonText,
    IonChip,
    IonLabel,
    IonSkeletonText,
  ],
})
export class ExamReviewPage implements OnInit, OnDestroy {
  // Datos
  availablePdfs = AVAILABLE_PDFS;
  selectedExam: ExamPdf | null = null;
  questions: ExamQuestion[] = [];
  totalQuestions: number = 0;
  currentQuestionNumber: number = 0;
  completedQuestions: Set<number> = new Set();

  // Estados
  loading = false;
  initialLoadComplete = false;
  hasMore = true;

  // Lifecycle
  private destroy$ = new Subject<void>();
  private readonly STORAGE_KEY = 'exam-review-state';

  constructor(
    private examQuestionService: ExamQuestionService,
    private router: Router
  ) {
    addIcons({refresh,bookmarkOutline,bookmark,checkmarkCircle,alertCircle,chevronUp,chevronDown,checkmarkCircleOutline,});
  }

  ngOnInit() {
    // Suscribirse a los cambios del servicio
    this.examQuestionService.questions
      .pipe(takeUntil(this.destroy$))
      .subscribe(questions => {
        this.questions = questions;
      });

    this.examQuestionService.loading
      .pipe(takeUntil(this.destroy$))
      .subscribe(loading => {
        this.loading = loading;
      });

    this.examQuestionService.hasMore
      .pipe(takeUntil(this.destroy$))
      .subscribe(hasMore => {
        this.hasMore = hasMore;
      });

    this.examQuestionService.totalItems
      .pipe(takeUntil(this.destroy$))
      .subscribe(total => {
        this.totalQuestions = total;
      });

    // Restaurar estado
    this.restoreState();
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
    this.examQuestionService.clearState();
  }

  /**
   * Cuando se selecciona un examen del dropdown
   */
  async onExamSelected(event: any) {
    const examId = event.detail.value;
    this.selectedExam = this.availablePdfs.find(pdf => pdf.id === examId) || null;

    if (this.selectedExam) {
      // Limpiar estado anterior
      this.questions = [];
      this.initialLoadComplete = false;
      this.examQuestionService.clearState();

      // Cargar preguntas completadas para este examen
      this.loadCompletedQuestions(examId);

      // Cargar todas las preguntas
      await this.loadAllQuestions(examId);
    }
  }

  /**
   * Cargar todas las preguntas
   */
  private async loadAllQuestions(examId: number) {
    this.loading = true;

    try {
      // Cargar en lotes de 100
      while (this.hasMore) {
        await this.examQuestionService.loadQuestions(examId, {
          sort: 'numberQuestion_asc',
          itemPerPage: 100
        }, this.questions.length > 0).toPromise();
      }

      this.initialLoadComplete = true;

      // Restaurar posición si existe
      this.scrollToCurrentQuestion();
    } catch (error) {
      console.error('Error cargando preguntas:', error);
    } finally {
      this.loading = false;
    }
  }

  /**
   * Marcar/desmarcar pregunta como completada
   */
  toggleComplete(question: ExamQuestion) {
    if (this.completedQuestions.has(question.numberQuestion)) {
      this.completedQuestions.delete(question.numberQuestion);
    } else {
      this.completedQuestions.add(question.numberQuestion);
    }

    this.currentQuestionNumber = question.numberQuestion;
    this.saveState();
  }

  /**
   * Verificar si una pregunta está completada
   */
  isCompleted(questionNumber: number): boolean {
    return this.completedQuestions.has(questionNumber);
  }

  /**
   * Ir a pregunta anterior
   */
  goToPreviousQuestion() {
    const idx = this.questions.findIndex(q => q.numberQuestion === this.currentQuestionNumber);
    if (idx > 0) {
      this.currentQuestionNumber = this.questions[idx - 1].numberQuestion;
      this.scrollToCurrentQuestion();
      this.saveState();
    }
  }

  /**
   * Ir a pregunta siguiente
   */
  goToNextQuestion() {
    const idx = this.questions.findIndex(q => q.numberQuestion === this.currentQuestionNumber);
    if (idx < this.questions.length - 1) {
      this.currentQuestionNumber = this.questions[idx + 1].numberQuestion;
      this.scrollToCurrentQuestion();
      this.saveState();
    }
  }

  /**
   * Scroll a la pregunta actual
   */
  private scrollToCurrentQuestion() {
    if (this.currentQuestionNumber > 0) {
      setTimeout(() => {
        const element = document.getElementById(`review-question-${this.currentQuestionNumber}`);
        if (element) {
          element.scrollIntoView({ behavior: 'instant', block: 'center' });
        }
      }, 100);
    }
  }

  /**
   * Guardar estado en localStorage
   */
  private saveState() {
    if (!this.selectedExam) return;

    const state: ReviewState = {
      examId: this.selectedExam.id,
      currentQuestion: this.currentQuestionNumber,
      completedQuestions: Array.from(this.completedQuestions),
      timestamp: Date.now()
    };

    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(state));
  }

  /**
   * Restaurar estado desde localStorage
   */
  private restoreState() {
    try {
      const saved = localStorage.getItem(this.STORAGE_KEY);
      if (!saved) return;

      const state: ReviewState = JSON.parse(saved);

      // Verificar que no haya expirado (24 horas)
      const ONE_DAY = 24 * 60 * 60 * 1000;
      if (Date.now() - state.timestamp > ONE_DAY) {
        localStorage.removeItem(this.STORAGE_KEY);
        return;
      }

      // Restaurar examen seleccionado
      this.selectedExam = this.availablePdfs.find(pdf => pdf.id === state.examId) || null;

      if (this.selectedExam) {
        this.currentQuestionNumber = state.currentQuestion;
        this.completedQuestions = new Set(state.completedQuestions);

        // Cargar preguntas
        setTimeout(() => {
          this.loadAllQuestions(this.selectedExam!.id);
        }, 100);
      }
    } catch (error) {
      console.error('Error restaurando estado:', error);
    }
  }

  /**
   * Cargar preguntas completadas para un examen
   */
  private loadCompletedQuestions(examId: number) {
    try {
      const saved = localStorage.getItem(this.STORAGE_KEY);
      if (!saved) return;

      const state: ReviewState = JSON.parse(saved);
      if (state.examId === examId) {
        this.completedQuestions = new Set(state.completedQuestions);
        this.currentQuestionNumber = state.currentQuestion;
      } else {
        this.completedQuestions = new Set();
        this.currentQuestionNumber = 0;
      }
    } catch {
      this.completedQuestions = new Set();
    }
  }

  /**
   * Refresh manual
   */
  async handleRefresh(event: any) {
    if (this.selectedExam) {
      this.examQuestionService.clearState();
      this.questions = [];
      this.initialLoadComplete = false;
      await this.loadAllQuestions(this.selectedExam.id);
    }
    event.target.complete();
  }

  /**
   * Contador de progreso
   */
  get progressText(): string {
    return `${this.completedQuestions.size} / ${this.totalQuestions} completadas`;
  }

  /**
   * Porcentaje de progreso
   */
  get progressPercent(): number {
    if (this.totalQuestions === 0) return 0;
    return Math.round((this.completedQuestions.size / this.totalQuestions) * 100);
  }
}
