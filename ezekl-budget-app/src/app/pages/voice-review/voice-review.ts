import { Component, inject, OnInit, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { addIcons } from 'ionicons';
import { Subject, takeUntil } from 'rxjs';
import { 
  AppSettings, 
  LoggerService,
  ExamQuestionService
} from '../../service';
import {
  ExamQuestion,
  ExamPdf
} from '../../shared/models';
import { HeaderComponent, FooterComponent, PanelComponent } from '../../components';
import { 
  walletOutline,
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
  bookOutline
} from 'ionicons/icons';
import {
  IonContent,
  IonHeader,
  IonToolbar,
  IonButtons,
  IonTitle,
  IonBackButton,
  IonCard,
  IonCardHeader,
  IonCardContent,
  IonLabel,
  IonIcon,
  IonButton,
  IonBadge,
  IonSelect,
  IonSelectOption,
  IonChip,
  IonText,
  IonSkeletonText,
  IonGrid,
  IonRow,
  IonCol,
  IonFab,
  IonFabButton,
  IonFabList,
  IonProgressBar,
  AlertController,
  ToastController
} from '@ionic/angular/standalone';
import { ResponsiveComponent } from '../../shared';

// Configuración de PDFs disponibles
const AVAILABLE_PDFS: ExamPdf[] = [
  { id: 1, filename: 'az-204.pdf', displayName: 'AZ-204: Developing Solutions for Microsoft Azure', path: '/assets/pdfs/az-204.pdf' },
  { id: 2, filename: 'dp-300.pdf', displayName: 'DP-300: Administering Microsoft Azure SQL Solutions', path: '/assets/pdfs/dp-300.pdf' },
];

@Component({
  selector: 'voice-review',
  templateUrl: './voice-review.html',
  styleUrls: ['./voice-review.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    HeaderComponent,
    FooterComponent,
    PanelComponent,
    IonContent,
    IonToolbar,
    IonButtons,
    IonButton,
    IonIcon,
    IonCard,
    IonCardHeader,
    IonCardContent,
    IonLabel,
    IonIcon,
    IonButton,
    IonSelect,
    IonSelectOption,
    IonChip,
    IonText,
    IonSkeletonText,
    IonGrid,
    IonRow,
    IonCol,
    IonFab,
    IonFabButton,
    IonFabList,
    IonProgressBar
]
})
export class VoiceReviewPage extends ResponsiveComponent implements OnInit, OnDestroy {
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

  private readonly logger = inject(LoggerService).getLogger('VoiceReviewPage');
  private readonly examQuestionService = inject(ExamQuestionService);
  private readonly router = inject(Router);
  private readonly alertController = inject(AlertController);
  private readonly toastController = inject(ToastController);
  private readonly cdr = inject(ChangeDetectorRef);

  constructor(public appSettings: AppSettings) {
    super();
    
    // Registrar íconos de Ionic
    addIcons({
      walletOutline,
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
      bookOutline
    });

    // Verificar si el navegador soporta Speech Synthesis
    if ('speechSynthesis' in window) {
      this.speechSynthesis = window.speechSynthesis;
    }
  }

  // Retorna el título de la página para el header móvil
  getPageTitle(): string {
    return this.selectedExam ? this.selectedExam.displayName : 'Repaso con Voz';
  }

  ngOnInit() {
    this.logger.debug('VoiceReviewPage ngOnInit');
    
    // Debug: Verificar estado del dark mode
    this.logger.debug('===== DARK MODE DEBUG =====');
    this.logger.debug('appDarkMode:', this.appSettings.appDarkMode);
    this.logger.debug('html has .ion-palette-dark:', document.documentElement.classList.contains('ion-palette-dark'));
    this.logger.debug('Computed --ion-background-color:', getComputedStyle(document.documentElement).getPropertyValue('--ion-background-color'));
    this.logger.debug('============================');
    
    // Suscribirse a los cambios del servicio
    this.examQuestionService.questions
      .pipe(takeUntil(this.destroy$))
      .subscribe(questions => {
        this.logger.debug('Questions updated from service:', questions.length);
        this.questions = questions;
        this.updateCurrentQuestion();
      });

    this.examQuestionService.loading
      .pipe(takeUntil(this.destroy$))
      .subscribe(loading => {
        this.logger.debug('Loading state changed:', loading);
        this.loading = loading;
      });

    this.examQuestionService.hasMore
      .pipe(takeUntil(this.destroy$))
      .subscribe(hasMore => {
        this.logger.debug('HasMore changed:', hasMore);
        this.hasMore = hasMore;
      });

    this.examQuestionService.totalItems
      .pipe(takeUntil(this.destroy$))
      .subscribe(total => {
        this.logger.debug('TotalItems changed:', total);
        this.totalQuestions = total;
      });
  }

  override ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
    this.examQuestionService.clearState();

    // Detener cualquier reproducción de voz
    this.stopSpeech();
  }

  // ========================================
  // MÉTODOS DE DATOS Y NAVEGACIÓN
  // ========================================

  /**
   * Actualizar la pregunta actual
   */
  private updateCurrentQuestion() {
    this.logger.debug('updateCurrentQuestion called, currentQuestionNumber:', this.currentQuestionNumber);
    
    if (this.currentQuestionNumber > 0) {
      this.currentQuestion = this.questions.find(q => q.numberQuestion === this.currentQuestionNumber) || null;
      this.logger.debug('currentQuestion found:', !!this.currentQuestion);
    } else if (this.questions.length > 0) {
      // Fallback: si no hay número actual pero hay preguntas, seleccionar la primera
      this.currentQuestionNumber = this.questions[0].numberQuestion;
      this.currentQuestion = this.questions[0];
      this.logger.debug('Fallback: selected first question:', this.currentQuestionNumber);
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
    // Manejar tanto eventos de Ionic (event.detail.value) como HTML estándar (event.target.value)
    const examId = event.detail?.value || event.target?.value;
    
    this.logger.debug('Examen seleccionado:', examId);
    
    if (!examId) {
      this.logger.debug('No se seleccionó ningún examen');
      return;
    }

    const selectedPdf = this.availablePdfs.find(pdf => pdf.id == examId); // Usar == para conversión de tipo
    this.selectedExam = selectedPdf || null;

    this.logger.debug('PDF encontrado:', this.selectedExam);

    if (this.selectedExam) {
      // Detener voz si está activa
      this.stopSpeech();

      // Limpiar estado anterior
      this.questions = [];
      this.initialLoadComplete = false;
      this.examQuestionService.clearState();

      // Cargar todas las preguntas
      await this.loadAllQuestions(Number(examId));
    }
  }

  /**
   * Método específico para manejar la selección en desktop (HTML select)
   */
  async onExamSelectedDesktop(event: any) {
    const examId = event.target.value;
    
    this.logger.debug('Examen seleccionado (desktop):', examId);
    
    if (!examId) {
      this.logger.debug('No se seleccionó ningún examen');
      return;
    }

    const selectedPdf = this.availablePdfs.find(pdf => pdf.id == examId); // Usar == para conversión de tipo
    this.selectedExam = selectedPdf || null;

    this.logger.debug('PDF encontrado (desktop):', this.selectedExam);

    if (this.selectedExam) {
      // Detener voz si está activa
      this.stopSpeech();

      // Limpiar estado anterior
      this.questions = [];
      this.initialLoadComplete = false;
      this.examQuestionService.clearState();

      // Cargar todas las preguntas
      await this.loadAllQuestions(Number(examId));
    }
  }

  /**
   * Truncar texto para mostrar en la tabla
   */
  truncateText(text: string, maxLength: number): string {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  }

  /**
   * Método público para recargar preguntas desde el template
   */
  async reloadQuestions() {
    if (this.selectedExam) {
      // Mantener initialLoadComplete en true para que no se oculte la tabla
      // Solo limpiar las preguntas y el estado del servicio
      const previousQuestions = [...this.questions];
      this.questions = [];
      this.examQuestionService.clearState();
      
      try {
        await this.loadAllQuestions(this.selectedExam.id);
      } catch (error) {
        // Si falla, restaurar las preguntas anteriores
        this.questions = previousQuestions;
      }
    }
  }

  /**
   * Cargar todas las preguntas
   */
  async loadAllQuestions(examId: number) {
    this.loading = true;
    this.logger.debug('Iniciando carga de preguntas para examId:', examId);

    try {
      // Cargar en lotes de 100
      let loadedCount = 0;
      while (this.hasMore) {
        this.logger.debug(`Cargando lote ${Math.floor(loadedCount / 100) + 1}...`);
        
        await this.examQuestionService.loadQuestions(examId, {
          sort: 'numberQuestion_asc',
          itemPerPage: 100
        }, this.questions.length > 0).toPromise();
        
        loadedCount = this.questions.length;
        this.logger.debug(`Preguntas cargadas hasta ahora: ${loadedCount}`);
      }

      this.logger.debug(`Carga completada. Total de preguntas: ${this.questions.length}`);
      this.initialLoadComplete = true;

      // Seleccionar la última pregunta leída
      this.selectLastReadQuestion();
      
      // Forzar detección de cambios
      this.cdr.detectChanges();
      
    } catch (error) {
      this.logger.error('Error cargando preguntas:', error);
      await this.showToast('Error al cargar las preguntas del examen', 'danger');
      
      // En lugar de resetear completamente, marcar como completado para mostrar la interfaz
      // pero sin preguntas, así el usuario puede intentar de nuevo
      this.initialLoadComplete = true;
      this.questions = []; // Asegurar que la lista esté vacía
      
      // NO resetear selectedExam para mantener la interfaz visible
      // this.selectedExam = null;  // COMENTADO para mantener la interfaz
      
    } finally {
      this.loading = false;
      this.cdr.detectChanges();
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
        this.logger.debug('Pregunta marcada en el servidor:', response.message);
      },
      error: (error) => {
        this.logger.error('Error al marcar pregunta en el servidor:', error);
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
    this.logger.debug('selectLastReadQuestion called, questions length:', this.questions.length);
    
    if (this.questions.length === 0) {
      this.logger.warn('No questions available');
      return;
    }

    let lastReadIndex = -1;
    for (let i = this.questions.length - 1; i >= 0; i--) {
      if (this.questions[i].readed) {
        lastReadIndex = i;
        break;
      }
    }

    this.logger.debug('lastReadIndex:', lastReadIndex);

    if (lastReadIndex >= 0 && lastReadIndex < this.questions.length - 1) {
      this.currentQuestionNumber = this.questions[lastReadIndex + 1].numberQuestion;
    } else if (lastReadIndex === this.questions.length - 1) {
      this.currentQuestionNumber = this.questions[lastReadIndex].numberQuestion;
    } else {
      this.currentQuestionNumber = this.questions[0]?.numberQuestion || 1;
    }

    this.logger.debug('Selected currentQuestionNumber:', this.currentQuestionNumber);

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
    event?.target?.complete();
  }

  /**
   * Contador de progreso
   */
  get progressText(): string {
    const completed = this.completedCount;
    return `${completed} / ${this.totalQuestions} completadas`;
  }

  /**
   * Porcentaje de progreso
   */
  get progressPercent(): number {
    if (this.totalQuestions === 0) return 0;
    const completed = this.completedCount;
    return Math.round((completed / this.totalQuestions) * 100);
  }

  /**
   * Contador de preguntas completadas
   */
  get completedCount(): number {
    return this.questions.filter(q => q.readed).length;
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
   * Ir a una pregunta específica y comenzar a leer automáticamente
   */
  goToQuestionAndRead(questionNumber: number) {
    const question = this.questions.find(q => q.numberQuestion === questionNumber);
    if (question) {
      this.stopSpeech();
      this.currentQuestionNumber = questionNumber;
      this.updateCurrentQuestion();
      this.scrollToCurrentQuestion();
      
      // Esperar un momento para que se actualice la vista y luego comenzar a leer
      setTimeout(() => {
        this.startSpeech();
      }, 300);
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
  scrollToCurrentQuestion() {
    if (this.currentQuestionNumber > 0) {
      setTimeout(() => {
        const element = document.getElementById(`voice-question-${this.currentQuestionNumber}`);
        if (element) {
          // Si está en una tabla, también hacer scroll del contenedor de la tabla
          const tableContainer = element.closest('.table-responsive');
          
          if (tableContainer) {
            // Para la versión desktop (tabla)
            const rect = element.getBoundingClientRect();
            const containerRect = tableContainer.getBoundingClientRect();
            
            if (rect.top < containerRect.top || rect.bottom > containerRect.bottom) {
              element.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
          } else {
            // Para la versión móvil (cards)
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
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

                await this.showToast(response.message, 'success');
              },
              error: async (error) => {
                this.logger.error('Error marcando preguntas:', error);
                await this.showToast('Error al marcar preguntas', 'danger');
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
    this.logger.debug('toggleSpeech called');
    this.logger.debug('speechSynthesis available:', !!this.speechSynthesis);
    this.logger.debug('selectedExam:', this.selectedExam);
    this.logger.debug('initialLoadComplete:', this.initialLoadComplete);
    this.logger.debug('currentQuestion:', this.currentQuestion);
    this.logger.debug('questions.length:', this.questions.length);
    
    if (!this.speechSynthesis) {
      this.logger.warn('Speech synthesis not available');
      this.showToast('Tu navegador no soporta lectura de voz', 'warning');
      return;
    }

    if (this.questions.length === 0) {
      this.logger.warn('No questions available');
      this.showToast('No hay preguntas cargadas para leer', 'warning');
      return;
    }

    if (!this.currentQuestion) {
      this.logger.warn('No current question available, attempting to select first question');
      if (this.questions.length > 0) {
        this.currentQuestionNumber = this.questions[0].numberQuestion;
        this.updateCurrentQuestion();
      }
      
      if (!this.currentQuestion) {
        this.showToast('Selecciona una pregunta para comenzar', 'warning');
        return;
      }
    }

    // Verificar si hay algo reproduciéndose actualmente o pausado
    const isSpeaking = this.speechSynthesis.speaking && !this.speechSynthesis.paused;
    const isPaused = this.speechSynthesis.paused;
    this.logger.debug('isSpeaking:', isSpeaking, 'isPaused:', isPaused);

    if (isSpeaking) {
      // Está hablando activamente, pausar
      this.pauseSpeech();
    } else if (isPaused) {
      // Está pausado, reanudar
      this.resumeSpeech();
    } else {
      // No está hablando ni pausado, iniciar nuevo
      this.startSpeech();
    }
  }

  /**
   * Reanudar lectura de voz pausada
   */
  private resumeSpeech() {
    if (!this.speechSynthesis) return;

    if (this.speechSynthesis.paused) {
      this.logger.debug('Resuming speech');
      this.speechSynthesis.resume();
      this.isSpeaking = true;
      this.cdr.detectChanges();
    }
  }

  /**
   * Iniciar lectura de voz
   */
  private startSpeech() {
    if (!this.speechSynthesis || !this.currentQuestion) return;

    // Si ya está hablando, no hacer nada
    if (this.speechSynthesis.speaking) {
      this.logger.debug('Already speaking, ignoring startSpeech');
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
      this.logger.error('Error en speech synthesis:', event);
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

    if (this.speechSynthesis.speaking && !this.speechSynthesis.paused) {
      this.logger.debug('Pausing speech');
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
