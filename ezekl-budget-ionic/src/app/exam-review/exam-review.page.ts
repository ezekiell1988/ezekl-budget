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
  IonCardHeader,
  IonCardContent,
  IonText,
  IonChip,
  IonLabel,
  IonSkeletonText,
  IonGrid,
  IonRow,
  IonCol,
  IonFab,
  IonFabButton,
  IonFabList,
  IonBadge,
  AlertController,
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import {
  refresh,
  checkmarkCircle,
  checkmarkCircleOutline,
  chevronUp,
  chevronDown,
  bookmarkOutline,
  bookmark,
  alertCircle,
  navigate,
  checkmarkDone,
  checkmark,
  arrowBack,
  ellipsisVertical } from 'ionicons/icons';
import { Subject, takeUntil } from 'rxjs';
import { ExamQuestionService } from '../services/exam-question.service';
import { ExamQuestion, ExamPdf } from '../models';

// Configuración de PDFs disponibles
const AVAILABLE_PDFS: ExamPdf[] = [
  { id: 1, filename: 'az-204.pdf', displayName: 'AZ-204: Developing Solutions for Microsoft Azure', path: '/assets/pdfs/az-204.pdf' },
  { id: 2, filename: 'dp-300.pdf', displayName: 'DP-300: Administering Microsoft Azure SQL Solutions', path: '/assets/pdfs/dp-300.pdf' },
];

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
    IonCardHeader,
    IonCardContent,
    IonText,
    IonChip,
    IonLabel,
    IonSkeletonText,
    IonGrid,
    IonRow,
    IonCol,
    IonFab,
    IonFabButton,
    IonFabList,
    IonBadge,
  ],
})
export class ExamReviewPage implements OnInit, OnDestroy {
  // Datos
  availablePdfs = AVAILABLE_PDFS;
  selectedExam: ExamPdf | null = null;
  questions: ExamQuestion[] = [];
  totalQuestions: number = 0;
  currentQuestionNumber: number = 0;

  // Estados
  loading = false;
  initialLoadComplete = false;
  hasMore = true;

  // Lifecycle
  private destroy$ = new Subject<void>();

  constructor(
    private examQuestionService: ExamQuestionService,
    private router: Router,
    private alertController: AlertController
  ) {
    addIcons({refresh,bookmarkOutline,bookmark,checkmark,checkmarkCircle,alertCircle,ellipsisVertical,chevronUp,chevronDown,navigate,checkmarkDone,checkmarkCircleOutline,arrowBack});
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
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
    this.examQuestionService.clearState();
  }

  /**
   * Regresar al selector de examen
   */
  goBackToSelector() {
    this.selectedExam = null;
    this.questions = [];
    this.initialLoadComplete = false;
    this.currentQuestionNumber = 0;
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

      // Seleccionar la última pregunta leída
      this.selectLastReadQuestion();
    } catch (error) {
      console.error('Error cargando preguntas:', error);
    } finally {
      this.loading = false;
    }
  }

  /**
   * Marcar pregunta individual como leída
   */
  toggleComplete(question: ExamQuestion) {
    if (!this.selectedExam) return;

    const wasCompleted = question.readed || false;

    // Si ya estaba marcada, no hacer nada (no se puede desmarcar individualmente)
    if (wasCompleted) {
      this.currentQuestionNumber = question.numberQuestion;
      return;
    }

    // Actualizar localmente de inmediato para UI responsiva
    question.readed = true;
    this.currentQuestionNumber = question.numberQuestion;

    // Llamar al backend para marcar como leída
    this.examQuestionService.setQuestion(question.idExamQuestion).subscribe({
      next: (response) => {
        console.log('Pregunta marcada en el servidor:', response.message);
      },
      error: (error) => {
        console.error('Error al marcar pregunta en el servidor:', error);
        // Revertir el cambio local si falla
        question.readed = false;
      }
    });

    this.saveState();
  }

  /**
   * Verificar si una pregunta está completada
   */
  isCompleted(questionNumber: number): boolean {
    const question = this.questions.find(q => q.numberQuestion === questionNumber);
    return question?.readed || false;
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
   * Guardar estado en localStorage (solo para la pregunta actual)
   */
  private saveState() {
    // Ya no usamos localStorage, este método se mantiene para compatibilidad
    // pero no hace nada. La posición se determina desde el backend.
  }

  /**
   * Seleccionar la última pregunta leída automáticamente
   */
  private selectLastReadQuestion() {
    // Buscar la última pregunta que está marcada como leída
    let lastReadIndex = -1;
    for (let i = this.questions.length - 1; i >= 0; i--) {
      if (this.questions[i].readed) {
        lastReadIndex = i;
        break;
      }
    }

    // Si hay preguntas leídas, seleccionar la última + 1 (la siguiente sin leer)
    // Si no hay ninguna leída, seleccionar la primera
    if (lastReadIndex >= 0 && lastReadIndex < this.questions.length - 1) {
      this.currentQuestionNumber = this.questions[lastReadIndex + 1].numberQuestion;
    } else if (lastReadIndex === this.questions.length - 1) {
      // Si todas están leídas, seleccionar la última
      this.currentQuestionNumber = this.questions[lastReadIndex].numberQuestion;
    } else {
      // Si ninguna está leída, seleccionar la primera
      this.currentQuestionNumber = this.questions[0]?.numberQuestion || 1;
    }

    this.scrollToCurrentQuestion();
    this.saveState();
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
    const completed = this.questions.filter(q => q.readed).length;
    return `${completed} / ${this.totalQuestions} completadas`;
  }

  /**
   * Porcentaje de progreso
   */
  get progressPercent(): number {
    if (this.totalQuestions === 0) return 0;
    const completed = this.questions.filter(q => q.readed).length;
    return Math.round((completed / this.totalQuestions) * 100);
  }

  /**
   * Abrir diálogo para ir a una pregunta específica
   */
  async openGoToDialog() {
    const alert = await this.alertController.create({
      header: 'Ir a pregunta',
      inputs: [
        {
          name: 'questionNumber',
          type: 'number',
          placeholder: `1 - ${this.totalQuestions}`,
          min: 1,
          max: this.totalQuestions,
          value: this.currentQuestionNumber || 1
        }
      ],
      buttons: [
        {
          text: 'Cancelar',
          role: 'cancel'
        },
        {
          text: 'Ir',
          handler: (data) => {
            const num = parseInt(data.questionNumber, 10);
            if (num >= 1 && num <= this.totalQuestions) {
              this.goToQuestion(num);
            }
          }
        }
      ]
    });

    await alert.present();
  }

  /**
   * Ir a una pregunta específica por número
   */
  goToQuestion(questionNumber: number) {
    const question = this.questions.find(q => q.numberQuestion === questionNumber);
    if (question) {
      this.currentQuestionNumber = questionNumber;
      this.scrollToCurrentQuestion();
      this.saveState();
    }
  }

  /**
   * Marcar todas las preguntas hasta la actual como completadas
   */
  async markAllPreviousComplete() {
    if (this.currentQuestionNumber <= 0 || !this.selectedExam) return;

    const alert = await this.alertController.create({
      header: 'Marcar hasta aquí',
      message: `¿Marcar las preguntas 1 a ${this.currentQuestionNumber} como completadas?`,
      buttons: [
        {
          text: 'Cancelar',
          role: 'cancel'
        },
        {
          text: 'Marcar todas',
          handler: () => {
            // Marcar localmente primero para UI responsiva
            this.questions.forEach(q => {
              q.readed = q.numberQuestion <= this.currentQuestionNumber;
            });

            // Llamar al backend
            this.examQuestionService.setToQuestion(
              this.selectedExam!.id,
              this.currentQuestionNumber
            ).subscribe({
              next: (response) => {
                console.log('Progreso actualizado:', response.message);
              },
              error: (error) => {
                console.error('Error al actualizar progreso:', error);
                // Recargar preguntas para sincronizar con el servidor
                this.loadAllQuestions(this.selectedExam!.id);
              }
            });

            this.saveState();
          }
        }
      ]
    });

    await alert.present();
  }
}
