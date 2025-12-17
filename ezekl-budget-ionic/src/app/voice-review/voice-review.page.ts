import { Component, OnInit, OnDestroy, ChangeDetectorRef } from '@angular/core';
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
  IonProgressBar,
  IonBadge,
  AlertController,
  ToastController,
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import {
  refresh,
  micOutline,
  mic,
  checkmark,
  checkmarkCircle,
  alertCircle,
  ellipsisVertical,
  chevronUp,
  chevronDown,
  navigate,
  checkmarkDone,
  checkmarkCircleOutline,
  arrowBack,
  radioButtonOn,
  play,
  pause,
  stop,
  volumeHigh,
  list,
  playBack,
  playForward,
  playSkipForward,
  playSkipForwardOutline,
} from 'ionicons/icons';
import { Subject, takeUntil } from 'rxjs';
import { ExamQuestionService } from '../services/exam-question.service';
import { ExamQuestion } from '../models/exam-question.models';

interface ExamPdf {
  id: number;
  filename: string;
  displayName: string;
  path: string;
}

// Configuración de PDFs disponibles
const AVAILABLE_PDFS: ExamPdf[] = [
  { id: 1, filename: 'az-204.pdf', displayName: 'AZ-204: Developing Solutions for Microsoft Azure', path: '/assets/pdfs/az-204.pdf' },
  { id: 2, filename: 'dp-300.pdf', displayName: 'DP-300: Administering Microsoft Azure SQL Solutions', path: '/assets/pdfs/dp-300.pdf' },
];

@Component({
  selector: 'app-voice-review',
  templateUrl: './voice-review.page.html',
  styleUrls: ['./voice-review.page.scss'],
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
    IonProgressBar,
    IonBadge,
  ],
})
export class VoiceReviewPage implements OnInit, OnDestroy {
  // Datos
  availablePdfs = AVAILABLE_PDFS;
  selectedExam: ExamPdf | null = null;
  questions: ExamQuestion[] = [];
  totalQuestions: number = 0;
  currentQuestionNumber: number = 0;
  currentQuestion: ExamQuestion | null = null;

  // Estados
  loading = false;
  initialLoadComplete = false;
  hasMore = true;
  autoReadNext = true; // Lectura automática de siguiente pregunta

  // Voice/Speech
  isSpeaking = false;
  speechSynthesis: SpeechSynthesis | null = null;
  currentUtterance: SpeechSynthesisUtterance | null = null;

  // Lifecycle
  private destroy$ = new Subject<void>();

  constructor(
    private examQuestionService: ExamQuestionService,
    private router: Router,
    private alertController: AlertController,
    private toastController: ToastController,
    private cdr: ChangeDetectorRef
  ) {
    addIcons({
      arrowBack,
      refresh,
      micOutline,
      mic,
      checkmarkCircle,
      playBack,
      stop,
      playForward,
      navigate,
      volumeHigh,
      list,
      alertCircle,
      ellipsisVertical,
      checkmarkDone,
      chevronUp,
      chevronDown,
      checkmark,
      checkmarkCircleOutline,
      radioButtonOn,
      play,
      pause,
      playSkipForward,
      playSkipForwardOutline,
    });

    // Verificar si el navegador soporta Speech Synthesis
    if ('speechSynthesis' in window) {
      this.speechSynthesis = window.speechSynthesis;
    }
  }

  ngOnInit() {
    // Suscribirse a los cambios del servicio
    this.examQuestionService.questions
      .pipe(takeUntil(this.destroy$))
      .subscribe(questions => {
        this.questions = questions;
        this.updateCurrentQuestion();
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

    // Detener cualquier reproducción de voz
    this.stopSpeech();
  }

  /**
   * Actualizar la pregunta actual
   */
  private updateCurrentQuestion() {
    if (this.currentQuestionNumber > 0) {
      this.currentQuestion = this.questions.find(q => q.numberQuestion === this.currentQuestionNumber) || null;
    }
  }

  /**
   * Regresar al selector de examen
   */
  goBackToSelector() {
    this.stopSpeech();
    this.selectedExam = null;
    this.questions = [];
    this.initialLoadComplete = false;
    this.currentQuestionNumber = 0;
    this.currentQuestion = null;
    this.examQuestionService.clearState();
  }

  /**
   * Cuando se selecciona un examen del dropdown
   */
  async onExamSelected(event: any) {
    const examId = event.detail.value;
    this.selectedExam = this.availablePdfs.find(pdf => pdf.id === examId) || null;

    if (this.selectedExam) {
      // Detener voz si está activa
      this.stopSpeech();

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
   * Marcar pregunta individual como leída (sin detener reproducción)
   */
  toggleComplete(question: ExamQuestion) {
    if (!this.selectedExam || !question) return;

    const wasCompleted = question.readed || false;

    // Si ya estaba marcada, no hacer nada
    if (wasCompleted) {
      return;
    }

    // Actualizar localmente
    question.readed = true;

    // Llamar al backend
    this.examQuestionService.setQuestion(question.idExamQuestion).subscribe({
      next: (response) => {
        console.log('Pregunta marcada en el servidor:', response.message);
      },
      error: (error) => {
        console.error('Error al marcar pregunta en el servidor:', error);
        question.readed = false;
      }
    });
  }

  /**
   * Marcar pregunta manualmente (con clic en el botón)
   */
  toggleCompleteManual(question: ExamQuestion) {
    if (!question) return;
    this.toggleComplete(question);
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
      this.updateCurrentQuestion();
      this.scrollToCurrentQuestion();
    }
  }

  /**
   * Ir a pregunta siguiente
   */
  goToNextQuestion() {
    const idx = this.questions.findIndex(q => q.numberQuestion === this.currentQuestionNumber);
    if (idx < this.questions.length - 1) {
      this.currentQuestionNumber = this.questions[idx + 1].numberQuestion;
      this.updateCurrentQuestion();
      this.scrollToCurrentQuestion();
    }
  }

  /**
   * Ir a pregunta anterior y comenzar a leer
   */
  goToPreviousQuestionAndRead() {
    this.stopSpeech();
    this.goToPreviousQuestion();
    setTimeout(() => {
      this.startSpeech();
    }, 300);
  }

  /**
   * Ir a pregunta siguiente y comenzar a leer
   */
  goToNextQuestionAndRead() {
    this.stopSpeech();
    this.goToNextQuestion();
    setTimeout(() => {
      this.startSpeech();
    }, 300);
  }

  /**
   * Seleccionar la última pregunta leída automáticamente
   */
  private selectLastReadQuestion() {
    let lastReadIndex = -1;
    for (let i = this.questions.length - 1; i >= 0; i--) {
      if (this.questions[i].readed) {
        lastReadIndex = i;
        break;
      }
    }

    if (lastReadIndex >= 0 && lastReadIndex < this.questions.length - 1) {
      this.currentQuestionNumber = this.questions[lastReadIndex + 1].numberQuestion;
    } else if (lastReadIndex === this.questions.length - 1) {
      this.currentQuestionNumber = this.questions[lastReadIndex].numberQuestion;
    } else {
      this.currentQuestionNumber = this.questions[0]?.numberQuestion || 1;
    }

    this.updateCurrentQuestion();
    this.scrollToCurrentQuestion();
  }

  /**
   * Refresh manual
   */
  async handleRefresh(event: any) {
    this.stopSpeech();

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
            const questionNumber = parseInt(data.questionNumber, 10);
            if (questionNumber >= 1 && questionNumber <= this.totalQuestions) {
              this.goToQuestion(questionNumber);
            }
          }
        }
      ]
    });

    await alert.present();
  }

  /**
   * Abrir diálogo para ir a una pregunta específica y comenzar a leer
   */
  async openGoToDialogAndRead() {
    const alert = await this.alertController.create({
      header: 'Ir a pregunta y leer',
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
          text: 'Ir y Leer',
          handler: (data) => {
            const questionNumber = parseInt(data.questionNumber, 10);
            if (questionNumber >= 1 && questionNumber <= this.totalQuestions) {
              this.stopSpeech();
              this.goToQuestion(questionNumber);
              setTimeout(() => {
                this.startSpeech();
              }, 500);
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
      this.stopSpeech();
      this.currentQuestionNumber = questionNumber;
      this.updateCurrentQuestion();
      this.scrollToCurrentQuestion();
    }
  }

  /**
   * Toggle lectura automática
   */
  toggleAutoRead() {
    this.autoReadNext = !this.autoReadNext;
    this.showToast(
      `Lectura automática ${this.autoReadNext ? 'activada' : 'desactivada'}`,
      this.autoReadNext ? 'success' : 'warning'
    );
  }

  /**
   * Avanzar automáticamente a la siguiente pregunta y comenzar lectura
   */
  private autoAdvanceToNextQuestion() {
    const idx = this.questions.findIndex(q => q.numberQuestion === this.currentQuestionNumber);

    if (idx < this.questions.length - 1) {
      // Marcar pregunta actual como leída
      if (this.currentQuestion && !this.currentQuestion.readed) {
        this.toggleComplete(this.currentQuestion);
      }

      // Avanzar a la siguiente
      setTimeout(() => {
        this.currentQuestionNumber = this.questions[idx + 1].numberQuestion;
        this.updateCurrentQuestion();

        // Scroll hacia la pregunta en la lista
        this.scrollToCurrentQuestion();

        // Pequeña pausa antes de iniciar la siguiente lectura
        setTimeout(() => {
          if (this.autoReadNext) {
            this.startSpeech();
          }
        }, 1000);
      }, 500);
    } else {
      // Llegamos al final
      this.showToast('Has completado todas las preguntas', 'success');
    }
  }

  /**
   * Scroll hacia la pregunta actual en la lista
   */
  private scrollToCurrentQuestion() {
    if (this.currentQuestionNumber > 0) {
      setTimeout(() => {
        const element = document.getElementById(`voice-question-${this.currentQuestionNumber}`);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }, 100);
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
            if (!this.selectedExam) return;

            this.examQuestionService.setToQuestion(
              this.selectedExam.id,
              this.currentQuestionNumber
            ).subscribe({
              next: async (response) => {
                // Actualizar localmente
                for (let i = 0; i < this.questions.length; i++) {
                  if (this.questions[i].numberQuestion <= this.currentQuestionNumber) {
                    this.questions[i].readed = true;
                  }
                }

                const toast = await this.toastController.create({
                  message: response.message,
                  duration: 2000,
                  color: 'success',
                  position: 'bottom'
                });
                await toast.present();
              },
              error: async (error) => {
                console.error('Error marcando preguntas:', error);
                const toast = await this.toastController.create({
                  message: 'Error al marcar preguntas',
                  duration: 2000,
                  color: 'danger',
                  position: 'bottom'
                });
                await toast.present();
              }
            });
          }
        }
      ]
    });

    await alert.present();
  }

  // ========================================
  // FUNCIONES DE VOZ / SPEECH SYNTHESIS
  // ========================================

  /**
   * Toggle reproducir/pausar
   */
  toggleSpeech() {
    if (!this.speechSynthesis) {
      this.showToast('Tu navegador no soporta lectura de voz', 'warning');
      return;
    }

    // Verificar si hay algo reproduciéndose actualmente
    const isCurrentlySpeaking = this.speechSynthesis.speaking && !this.speechSynthesis.paused;

    if (isCurrentlySpeaking) {
      this.pauseSpeech();
    } else {
      this.startSpeech();
    }
  }

  /**
   * Iniciar lectura de voz
   */
  private startSpeech() {
    if (!this.speechSynthesis || !this.currentQuestion) return;

    // Si ya hay una utterance pausada, continuar
    if (this.currentUtterance && this.speechSynthesis.paused) {
      this.speechSynthesis.resume();
      this.isSpeaking = true;
      this.cdr.detectChanges();
      return;
    }

    // Si ya está hablando, no hacer nada
    if (this.speechSynthesis.speaking && !this.speechSynthesis.paused) {
      return;
    }

    // Crear nuevo utterance
    const textToSpeak = this.buildTextToSpeak();

    this.currentUtterance = new SpeechSynthesisUtterance(textToSpeak);

    // Configurar voz en español
    const voices = this.speechSynthesis.getVoices();
    const spanishVoice = voices.find(voice =>
      voice.lang.startsWith('es') || voice.lang.startsWith('ES')
    );

    if (spanishVoice) {
      this.currentUtterance.voice = spanishVoice;
    }

    this.currentUtterance.lang = 'es-ES';
    this.currentUtterance.rate = 0.9; // Velocidad (0.1 - 10)
    this.currentUtterance.pitch = 1; // Tono (0 - 2)
    this.currentUtterance.volume = 1; // Volumen (0 - 1)

    // Establecer isSpeaking inmediatamente antes de los event listeners
    this.isSpeaking = true;
    this.cdr.detectChanges();

    // Event listeners
    this.currentUtterance.onstart = () => {
      this.isSpeaking = true;
      this.cdr.detectChanges();
    };

    this.currentUtterance.onend = () => {
      this.isSpeaking = false;
      this.currentUtterance = null;
      this.cdr.detectChanges();

      // Avanzar automáticamente a la siguiente pregunta
      if (this.autoReadNext) {
        this.autoAdvanceToNextQuestion();
      }
    };

    this.currentUtterance.onerror = (event) => {
      console.error('Error en speech synthesis:', event);
      this.isSpeaking = false;
      this.currentUtterance = null;
      this.cdr.detectChanges();
      this.showToast('Error al reproducir voz', 'danger');
    };

    // Iniciar
    this.speechSynthesis.speak(this.currentUtterance);
  }

  /**
   * Pausar lectura de voz
   */
  private pauseSpeech() {
    if (!this.speechSynthesis) return;

    if (this.speechSynthesis.speaking) {
      this.speechSynthesis.pause();
      this.isSpeaking = false;
      this.cdr.detectChanges();
    }
  }

  /**
   * Detener lectura de voz
   */
  stopSpeech() {
    if (!this.speechSynthesis) return;

    this.speechSynthesis.cancel();
    this.isSpeaking = false;
    this.currentUtterance = null;
    this.cdr.detectChanges();
  }

  /**
   * Construir texto para leer
   */
  private buildTextToSpeak(): string {
    if (!this.currentQuestion) return '';

    let text = `Pregunta ${this.currentQuestion.numberQuestion}. `;
    text += this.currentQuestion.shortQuestion;

    if (this.currentQuestion.correctAnswer) {
      text += '. Respuesta correcta: ';
      text += this.currentQuestion.correctAnswer;
    }

    return text;
  }

  /**
   * Mostrar toast
   */
  private async showToast(message: string, color: 'success' | 'warning' | 'danger' = 'success') {
    const toast = await this.toastController.create({
      message,
      duration: 2000,
      color,
      position: 'bottom'
    });
    await toast.present();
  }
}
