import { Component, OnInit, AfterViewInit, OnDestroy, ViewChild, ElementRef } from '@angular/core';
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
  IonList,
  IonItem,
  IonLabel,
  IonCard,
  IonCardContent,
  IonInfiniteScroll,
  IonInfiniteScrollContent,
  IonText,
  IonButton,
  IonIcon,
  IonSelect,
  IonSelectOption,
  IonRefresher,
  IonRefresherContent,
  IonAlert,
  IonToast,
  IonChip,
  IonSkeletonText,
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import {
  arrowBack,
  arrowForward,
  documentText,
  checkmarkCircle,
  search,
  alertCircle,
  refresh,
  chevronUp,
  chevronDown, timeOutline } from 'ionicons/icons';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { ExamQuestionService } from '../services';
import { ExamQuestion, ExamPdf } from '../models';

// Configuración de PDFs disponibles

const AVAILABLE_PDFS: ExamPdf[] = [
  { id: 1, filename: 'az-204.pdf', displayName: 'AZ-204: Developing Solutions for Microsoft Azure', path: '/assets/pdfs/az-204.pdf' },
  { id: 2, filename: 'dp-300.pdf', displayName: 'DP-300: Administering Microsoft Azure SQL Solutions', path: '/assets/pdfs/dp-300.pdf' },
];

@Component({
  selector: 'app-exam-question',
  templateUrl: './exam-question.page.html',
  styleUrls: ['./exam-question.page.scss'],
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
    IonList,
    IonItem,
    IonLabel,
    IonCard,
    IonCardContent,
    IonInfiniteScroll,
    IonInfiniteScrollContent,
    IonText,
    IonButton,
    IonIcon,
    IonSelect,
    IonSelectOption,
    IonRefresher,
    IonRefresherContent,
    IonAlert,
    IonToast,
    IonChip,
    IonSkeletonText,
  ],
})
export class ExamQuestionPage implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('pdfContainer') pdfContainer!: ElementRef<HTMLDivElement>;
  @ViewChild('questionsList') questionsList!: ElementRef<HTMLDivElement>;
  @ViewChild(IonInfiniteScroll) infiniteScroll?: IonInfiniteScroll;

  // Datos
  availablePdfs = AVAILABLE_PDFS;
  selectedExam: ExamPdf | null = null;
  questions: ExamQuestion[] = [];
  currentPdfPage: number = 1;
  totalPages: number = 0;
  currentQuestionIndex: number = -1;
  totalQuestions: number = 0;

  // Estados
  loading = false;
  loadingPdf = false;
  loadingSpecificQuestion = false; // Skeleton para carga de pregunta específica
  hasMore = true;
  showAlert = false;
  alertMessage = '';
  showToast = false;
  toastMessage = '';

  // Flags para prevenir bucles de restauración en iOS
  private isRestoringState = false;
  private hasRestoredState = false;

  // PDF.js
  private pdfDoc: any = null;
  private renderedPages: Set<number> = new Set();
  private pageObserver: IntersectionObserver | null = null;
  private readonly INITIAL_PAGES_TO_RENDER = 20; // Renderizar las primeras 20 páginas
  private readonly PAGES_PER_BATCH = 10; // Renderizar 10 páginas a la vez cuando se hace scroll
  private isRenderingBatch = false; // Flag para evitar renderizado múltiple
  private backgroundLoadingInterval: any = null; // Intervalo para carga en background

  // Lifecycle
  private destroy$ = new Subject<void>();

  constructor(
    private examQuestionService: ExamQuestionService,
    private router: Router
  ) {
    addIcons({refresh,documentText,chevronUp,chevronDown,timeOutline,checkmarkCircle,alertCircle,arrowBack,arrowForward,search,});
  }

  ngOnInit() {
    // Suscribirse a los cambios del servicio
    this.examQuestionService.questions
      .pipe(takeUntil(this.destroy$))
      .subscribe(questions => {
        this.questions = questions;
        // Actualizar índice de pregunta actual si hay preguntas
        if (questions.length > 0 && this.currentQuestionIndex < 0) {
          this.currentQuestionIndex = 0;
        }
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

  ngAfterViewInit() {
    // Restaurar estado después de que la vista se haya inicializado
    // Usar setTimeout para evitar ExpressionChangedAfterItHasBeenCheckedError
    // Solo restaurar si no se ha restaurado ya (previene bucles en iOS)
    if (!this.hasRestoredState) {
      setTimeout(() => {
        this.restoreStateExam();
      }, 0);
    }
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
    this.examQuestionService.clearState();
    if (this.pageObserver) {
      this.pageObserver.disconnect();
    }
    // Limpiar intervalo de carga en background
    if (this.backgroundLoadingInterval) {
      clearInterval(this.backgroundLoadingInterval);
      this.backgroundLoadingInterval = null;
    }
  }

  /**
   * Cuando se selecciona un PDF del dropdown
   */
  async onExamSelected(event: any) {
    const examId = event.detail.value;
    const previousExam = this.selectedExam;
    this.selectedExam = this.availablePdfs.find(pdf => pdf.id === examId) || null;

    if (this.selectedExam) {
      // Limpiar estado guardado del examen anterior
      if (previousExam && previousExam.id !== this.selectedExam.id) {
        localStorage.removeItem(`exam_state_${previousExam.id}`);
      }

      // Cargar el PDF
      this.loadPdf(this.selectedExam.path);

      // Cargar las primeras preguntas
      this.examQuestionService.refreshQuestions(this.selectedExam.id, {
        itemPerPage: 20,
        sort: 'numberQuestion_asc'
      }).pipe(takeUntil(this.destroy$)).subscribe({
        next: async () => {
          this.currentQuestionIndex = this.questions.length > 0 ? 0 : -1;

          // Restaurar estado si existe
          await this.restoreStatePosition();

          // Iniciar carga en background de preguntas
          this.startBackgroundQuestionsLoading();
        },
        error: (error) => {
          console.error('Error cargando preguntas:', error);
          this.showError('Error al cargar las preguntas');
        }
      });
    }
  }

  /**
   * Cargar PDF usando PDF.js
   */
  async loadPdf(pdfPath: string) {
    this.loadingPdf = true;

    try {
      // Verificar que PDF.js esté disponible
      if (typeof (window as any).pdfjsLib === 'undefined') {
        this.showError('PDF.js no está disponible. Por favor, recarga la página.');
        this.loadingPdf = false;
        return;
      }

      const pdfjsLib = (window as any).pdfjsLib;

      // Cargar documento PDF
      const loadingTask = pdfjsLib.getDocument(pdfPath);
      this.pdfDoc = await loadingTask.promise;
      this.totalPages = this.pdfDoc.numPages;

      // Esperar un tick para asegurar que el DOM esté listo
      await new Promise(resolve => setTimeout(resolve, 100));

      // Limpiar páginas renderizadas anteriores
      this.renderedPages.clear();

      // Renderizar todas las páginas
      await this.renderAllPages();

    } catch (error) {
      console.error('Error cargando PDF:', error);
      this.showError('Error al cargar el PDF. Verifica que el archivo existe.');
    } finally {
      this.loadingPdf = false;
    }
  }  /**
   * Renderizar todas las páginas del PDF
   */
  async renderAllPages() {
    const container = document.getElementById('pdf-container');

    if (!container) {
      console.error('No se encontró el contenedor pdf-container');
      this.showError('Error: contenedor PDF no encontrado');
      return;
    }

    // Limpiar contenedor
    container.innerHTML = '';

    // Calcular escala basada en el ancho del contenedor
    const containerWidth = this.pdfContainer?.nativeElement?.clientWidth || 800;

    // Crear placeholders para todas las páginas
    for (let pageNum = 1; pageNum <= this.totalPages; pageNum++) {
      const pageWrapper = document.createElement('div');
      pageWrapper.className = 'pdf-page-wrapper';
      pageWrapper.id = `pdf-page-${pageNum}`;
      pageWrapper.setAttribute('data-page-number', pageNum.toString());
      pageWrapper.setAttribute('data-rendered', 'false');

      // Crear label de número de página
      const pageLabel = document.createElement('div');
      pageLabel.className = 'pdf-page-label';
      pageLabel.textContent = `Página ${pageNum}`;

      // Crear placeholder con altura estimada
      const placeholder = document.createElement('div');
      placeholder.className = 'pdf-page-placeholder';
      placeholder.style.height = '1100px'; // Altura estimada de una página A4

      const placeholderContent = document.createElement('div');
      placeholderContent.className = 'pdf-placeholder-content';

      const spinner = document.createElement('div');
      spinner.className = 'placeholder-spinner';
      spinner.innerHTML = '⏳'; // Emoji temporal, se reemplazará al renderizar

      const text = document.createElement('p');
      text.textContent = `Cargando página ${pageNum}...`;

      placeholderContent.appendChild(spinner);
      placeholderContent.appendChild(text);
      placeholder.appendChild(placeholderContent);

      pageWrapper.appendChild(pageLabel);
      pageWrapper.appendChild(placeholder);
      container.appendChild(pageWrapper);

      // Agregar click listener
      pageWrapper.addEventListener('click', () => this.onPageClick(pageNum));
    }

    // Renderizar solo las primeras páginas inicialmente
    await this.renderPageRange(1, this.INITIAL_PAGES_TO_RENDER, containerWidth);

    // Configurar observer para lazy loading y detección de página visible
    this.setupPageObserver();

    // Iniciar carga en background de las páginas restantes
    this.startBackgroundPdfLoading();
  }

  /**
   * Renderizar un rango de páginas
   */
  async renderPageRange(startPage: number, endPage: number, containerWidth: number) {
    const maxPage = Math.min(endPage, this.totalPages);

    for (let pageNum = startPage; pageNum <= maxPage; pageNum++) {
      if (this.renderedPages.has(pageNum)) {
        continue;
      }

      try {
        const page = await this.pdfDoc.getPage(pageNum);
        const viewport = page.getViewport({ scale: 1 });
        const scale = (containerWidth * 0.95) / viewport.width;
        const scaledViewport = page.getViewport({ scale });

        const pageWrapper = document.getElementById(`pdf-page-${pageNum}`);
        if (!pageWrapper) {
          continue;
        }

        // Crear canvas
        const canvas = document.createElement('canvas');
        canvas.className = 'pdf-page-canvas';
        canvas.height = scaledViewport.height;
        canvas.width = scaledViewport.width;

        // Reemplazar placeholder con canvas
        const placeholder = pageWrapper.querySelector('.pdf-page-placeholder');
        if (placeholder) {
          placeholder.replaceWith(canvas);
        } else {
          pageWrapper.appendChild(canvas);
        }

        // Renderizar página
        const context = canvas.getContext('2d');
        if (context) {
          await page.render({
            canvasContext: context,
            viewport: scaledViewport,
          }).promise;

          this.renderedPages.add(pageNum);
          pageWrapper.setAttribute('data-rendered', 'true');
        }

      } catch (error) {
        console.error(`Error renderizando página ${pageNum}:`, error);
      }
    }
  }  /**
   * Configurar observer para lazy loading y detectar la página visible
   */
  setupPageObserver() {
    const options = {
      root: document.querySelector('.pdf-viewer'),
      rootMargin: '500px', // Cargar páginas 500px antes de que sean visibles
      threshold: 0.1
    };

    this.pageObserver = new IntersectionObserver((entries) => {
      entries.forEach(async entry => {
        const pageNum = parseInt(entry.target.getAttribute('data-page-number') || '1');
        const isRendered = entry.target.getAttribute('data-rendered') === 'true';

        // Actualizar página actual si es visible
        if (entry.isIntersecting && entry.intersectionRatio > 0.5) {
          this.currentPdfPage = pageNum;
        }

        // Lazy loading: renderizar página si entra en el viewport y no está renderizada
        if (entry.isIntersecting && !isRendered && !this.isRenderingBatch) {
          await this.renderNextBatch(pageNum);
        }
      });
    }, options);

    // Observar todas las páginas
    const pages = document.querySelectorAll('.pdf-page-wrapper');
    pages.forEach(page => this.pageObserver?.observe(page));
  }

  /**
   * Renderizar el siguiente lote de páginas
   */
  async renderNextBatch(startPage: number) {
    if (this.isRenderingBatch) return;

    this.isRenderingBatch = true;

    try {
      const containerWidth = this.pdfContainer?.nativeElement?.clientWidth || 800;
      const endPage = Math.min(startPage + this.PAGES_PER_BATCH - 1, this.totalPages);

      // Renderizar páginas que aún no se han renderizado en este rango
      await this.renderPageRange(startPage, endPage, containerWidth);
    } finally {
      this.isRenderingBatch = false;
    }
  }

  /**
   * Iniciar carga en background de todas las páginas restantes del PDF
   */
  private async startBackgroundPdfLoading() {
    // Esperar un poco antes de comenzar la carga en background
    await new Promise(resolve => setTimeout(resolve, 2000));

    const containerWidth = this.pdfContainer?.nativeElement?.clientWidth || 800;
    let currentPage = this.INITIAL_PAGES_TO_RENDER + 1;

    // Usar requestIdleCallback si está disponible, sino setTimeout
    const scheduleWork = (callback: () => void) => {
      if ('requestIdleCallback' in window) {
        (window as any).requestIdleCallback(callback, { timeout: 2000 });
      } else {
        setTimeout(callback, 100);
      }
    };

    const loadNextBatch = async () => {
      if (currentPage > this.totalPages) {
        return;
      }

      // Renderizar siguiente lote
      const endPage = Math.min(currentPage + this.PAGES_PER_BATCH - 1, this.totalPages);
      await this.renderPageRange(currentPage, endPage, containerWidth);

      currentPage = endPage + 1;

      // Programar siguiente lote
      if (currentPage <= this.totalPages) {
        scheduleWork(loadNextBatch);
      }
    };

    // Iniciar carga en background
    scheduleWork(loadNextBatch);
  }

  /**
   * Iniciar carga en background de todas las preguntas restantes
   */
  private startBackgroundQuestionsLoading() {
    if (!this.selectedExam) return;

    // Esperar un poco antes de comenzar la carga en background
    setTimeout(() => {
      this.loadAllQuestionsInBackground();
    }, 2000);
  }

  /**
   * Cargar todas las preguntas en background de forma progresiva
   */
  private async loadAllQuestionsInBackground() {
    if (!this.selectedExam || !this.hasMore) {
      return;
    }

    // Usar requestIdleCallback para no bloquear la UI
    const scheduleWork = (callback: () => void) => {
      if ('requestIdleCallback' in window) {
        (window as any).requestIdleCallback(callback, { timeout: 2000 });
      } else {
        setTimeout(callback, 500);
      }
    };

    const loadNext = () => {
      if (!this.selectedExam || !this.hasMore || this.loading) {
        return;
      }

      this.examQuestionService.loadNextPage(this.selectedExam.id, {
        itemPerPage: 20,
        sort: 'numberQuestion_asc'
      }).pipe(takeUntil(this.destroy$)).subscribe({
        next: () => {
          // Si hay más preguntas, programar siguiente carga
          if (this.hasMore) {
            scheduleWork(loadNext);
          }
        },
        error: (error) => {
          console.error('Error en carga background de preguntas:', error);
        }
      });
    };

    // Iniciar carga
    scheduleWork(loadNext);
  }

  /**
   * Ir a una página específica
   */
  async goToPage(page: number) {
    if (page < 1 || page > this.totalPages) return;

    const pageElement = document.getElementById(`pdf-page-${page}`);
    if (pageElement) {
      // Verificar si la página está renderizada
      const isRendered = pageElement.getAttribute('data-rendered') === 'true';

      // Si no está renderizada, renderizarla junto con páginas cercanas
      if (!isRendered) {
        const startPage = Math.max(1, page - 5);
        const endPage = Math.min(this.totalPages, page + 5);
        const containerWidth = this.pdfContainer?.nativeElement?.clientWidth || 800;
        await this.renderPageRange(startPage, endPage, containerWidth);
      }

      // Calcular la diferencia entre la página actual y la destino
      const pageDiff = Math.abs(page - this.currentPdfPage);

      // Si el salto es mayor a 10 páginas o estamos restaurando, hacer scroll instantáneo
      // Usar 'auto' siempre en iOS para evitar problemas de recarga
      const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
      const behavior = (pageDiff > 10 || this.isRestoringState || isIOS) ? 'auto' : 'smooth';

      try {
        pageElement.scrollIntoView({ behavior: behavior as ScrollBehavior, block: 'start' });
      } catch (e) {
        // Fallback para navegadores que no soporten scrollIntoView con opciones
        pageElement.scrollIntoView(true);
      }
      this.currentPdfPage = page;
      this.saveState();
    }
  }

  /**
   * Ir a la página anterior
   */
  goToPreviousPage() {
    if (this.currentPdfPage > 1) {
      this.goToPage(this.currentPdfPage - 1);
    }
  }

  /**
   * Ir a la página siguiente
   */
  goToNextPage() {
    if (this.currentPdfPage < this.totalPages) {
      this.goToPage(this.currentPdfPage + 1);
    }
  }

  /**
   * Manejar cambio en el input de página
   */
  onPageInputChange(event: any) {
    const pageNumber = parseInt(event.target.value);
    if (!isNaN(pageNumber)) {
      this.goToPage(pageNumber);
    }
  }

  /**
   * Click en una página del PDF - buscar pregunta asociada
   */
  async onPageClick(pageNum: number) {
    // Buscar pregunta que comience en esta página primero
    let question = this.questions.find(q => q.startPage === pageNum);

    // Si no hay pregunta que comience aquí, buscar pregunta que contenga esta página
    // pero priorizar la que tenga startPage más cercano
    if (!question) {
      const questionsInPage = this.questions.filter(q =>
        q.startPage && q.endPage &&
        pageNum >= q.startPage && pageNum <= q.endPage
      );

      if (questionsInPage.length > 0) {
        // Ordenar por proximidad del startPage a la página actual
        // Preferir preguntas cuyo startPage sea más cercano a pageNum
        questionsInPage.sort((a, b) => {
          const diffA = Math.abs((a.startPage || 0) - pageNum);
          const diffB = Math.abs((b.startPage || 0) - pageNum);
          return diffA - diffB;
        });
        question = questionsInPage[0];
      }
    }

    if (question) {
      this.scrollToQuestion(question.numberQuestion);
      this.showInfo(`Pregunta ${question.numberQuestion} encontrada en página ${pageNum}`);
    } else {
      this.showInfo(`No hay pregunta asociada a la página ${pageNum}`);
    }
  }

  /**
   * Click en una pregunta - navegar al PDF
   */
  async onQuestionClick(question: ExamQuestion) {
    this.currentQuestionIndex = this.questions.findIndex(q => q.numberQuestion === question.numberQuestion);
    this.saveState();

    if (question.startPage) {
      await this.goToPage(question.startPage);
      this.showInfo(`Navegando a la página ${question.startPage}`);
    } else {
      this.showInfo('Esta pregunta no tiene página asociada');
    }
  }

  /**
   * Scroll a una pregunta específica en la lista
   */
  scrollToQuestion(questionNumber: number) {
    const element = document.getElementById(`question-${questionNumber}`);
    if (element) {
      // Usar 'auto' en lugar de 'smooth' para evitar problemas en iOS
      // que pueden causar recargas de página
      try {
        element.scrollIntoView({ behavior: 'auto', block: 'center' });
      } catch (e) {
        // Fallback para navegadores que no soporten scrollIntoView con opciones
        element.scrollIntoView(true);
      }

      // Resaltar temporalmente
      element.classList.add('highlight');
      setTimeout(() => {
        element.classList.remove('highlight');
      }, 2000);
    }
  }

  /**
   * Infinite scroll - cargar más preguntas
   */
  async onIonInfinite(event: any) {
    if (!this.selectedExam) {
      event.target.complete();
      return;
    }

    this.examQuestionService.loadNextPage(this.selectedExam.id, {
      itemPerPage: 20,
      sort: 'numberQuestion_asc'
    }).pipe(takeUntil(this.destroy$)).subscribe({
      next: () => {
        event.target.complete();
      },
      error: () => {
        event.target.complete();
      }
    });
  }

  /**
   * Pull to refresh
   */
  async handleRefresh(event: any) {
    if (!this.selectedExam) {
      event.target.complete();
      return;
    }

    // Prevenir refresh durante restauración
    if (this.isRestoringState) {
      event.target.complete();
      return;
    }

    // Limpiar estado guardado en localStorage
    localStorage.removeItem(`exam_state_${this.selectedExam.id}`);

    // Resetear flags de restauración para permitir nueva restauración si es necesario
    this.hasRestoredState = false;
    this.isRestoringState = false;

    // Resetear estado local
    this.questions = [];
    this.currentQuestionIndex = -1;
    this.hasMore = true;

    this.examQuestionService.refreshQuestions(this.selectedExam.id, {
      itemPerPage: 20,
      sort: 'numberQuestion_asc'
    }).pipe(takeUntil(this.destroy$)).subscribe({
      next: () => {
        event.target.complete();
        this.showInfo('Datos actualizados');
      },
      error: () => {
        event.target.complete();
        this.showError('Error al actualizar los datos');
      }
    });
  }

  /**
   * Mostrar error
   */
  showError(message: string) {
    this.alertMessage = message;
    this.showAlert = true;
  }

  /**
   * Mostrar información
   */
  showInfo(message: string) {
    this.toastMessage = message;
    this.showToast = true;
  }

  /**
   * Cerrar alert
   */
  closeAlert() {
    this.showAlert = false;
  }

  /**
   * Cerrar toast
   */
  closeToast() {
    this.showToast = false;
  }

  /**
   * Volver atrás
   */
  goBack() {
    this.router.navigate(['/']);
  }

  /**
   * Guardar estado actual en localStorage
   */
  private saveState() {
    // No guardar estado mientras se está restaurando (previene bucles en iOS)
    if (!this.selectedExam || this.isRestoringState) return;

    // Guardar el número de pregunta en lugar del índice
    const currentQuestion = this.questions[this.currentQuestionIndex];

    const state = {
      examId: this.selectedExam.id,
      pdfPage: this.currentPdfPage,
      questionNumber: currentQuestion?.numberQuestion || null,
      timestamp: Date.now()
    };

    localStorage.setItem(`exam_state_${this.selectedExam.id}`, JSON.stringify(state));
  }

  /**
   * Restaurar estado guardado desde localStorage
   */
  private async restoreStateExam() {
    // Prevenir restauración múltiple (especialmente importante en iOS)
    if (this.hasRestoredState || this.isRestoringState) {
      console.log('⚠️ Restauración ya en progreso o completada, saltando...');
      return;
    }

    this.isRestoringState = true;
    this.hasRestoredState = true;

    // Buscar el último examen usado
    for (const pdf of this.availablePdfs) {
      const savedState = localStorage.getItem(`exam_state_${pdf.id}`);
      if (savedState) {
        try {
          const state = JSON.parse(savedState);

          // Solo restaurar si el timestamp es menor a 24 horas
          const hoursSinceLastVisit = (Date.now() - state.timestamp) / (1000 * 60 * 60);
          if (hoursSinceLastVisit > 24) {
            localStorage.removeItem(`exam_state_${pdf.id}`);
            continue;
          }

          // Restaurar el examen
          this.selectedExam = pdf;

          // Cargar el PDF
          await this.loadPdf(this.selectedExam.path);

          // Cargar las primeras preguntas
          this.examQuestionService.refreshQuestions(this.selectedExam.id, {
            itemPerPage: 20,
            sort: 'numberQuestion_asc'
          }).pipe(takeUntil(this.destroy$)).subscribe({
            next: async () => {
              // Restaurar posición
              await this.restoreStatePosition();

              // Iniciar carga en background
              this.startBackgroundQuestionsLoading();
            }
          });

          // Solo restaurar el primer examen encontrado
          break;
        } catch (error) {
          console.error('Error al restaurar estado del examen:', error);
          localStorage.removeItem(`exam_state_${pdf.id}`);
        }
      }
    }

    // Marcar restauración como completada
    this.isRestoringState = false;
  }

  /**
   * Restaurar posición (página PDF y pregunta)
   */
  private async restoreStatePosition() {
    if (!this.selectedExam) return;

    const savedState = localStorage.getItem(`exam_state_${this.selectedExam.id}`);
    if (!savedState) return;

    // Marcar que estamos restaurando para no guardar durante el proceso
    const wasRestoring = this.isRestoringState;
    this.isRestoringState = true;

    try {
      const state = JSON.parse(savedState);

      // Verificar que sea el mismo examen
      if (state.examId !== this.selectedExam.id) {
        this.isRestoringState = wasRestoring;
        return;
      }

      // Esperar a que se carguen las preguntas iniciales
      await new Promise(resolve => setTimeout(resolve, 500));

      // Restaurar página del PDF
      if (state.pdfPage && state.pdfPage > 0 && state.pdfPage <= this.totalPages) {
        await this.goToPage(state.pdfPage);
      }

      // Restaurar pregunta seleccionada por número de pregunta
      if (state.questionNumber) {
        // Buscar la pregunta en las cargadas
        const questionIndex = this.questions.findIndex(q => q.numberQuestion === state.questionNumber);

        if (questionIndex >= 0) {
          // La pregunta ya está cargada
          this.currentQuestionIndex = questionIndex;
          this.scrollToCurrentQuestion();
          console.log(`✅ Estado restaurado: Pregunta ${state.questionNumber} en página ${state.pdfPage}`);
        } else {
          // La pregunta no está cargada, mostrar skeleton y cargarla
          console.log(`📥 Pregunta ${state.questionNumber} no está cargada, cargando...`);
          this.loadingSpecificQuestion = true;

          await this.loadQuestionByNumber(state.questionNumber);

          // Después de cargar, buscar de nuevo y hacer scroll
          await new Promise(resolve => setTimeout(resolve, 300)); // Esperar a que el DOM se actualice

          const newIndex = this.questions.findIndex(q => q.numberQuestion === state.questionNumber);
          if (newIndex >= 0) {
            this.currentQuestionIndex = newIndex;
            this.loadingSpecificQuestion = false;

            // Esperar a que se quite el skeleton antes de hacer scroll
            await new Promise(resolve => setTimeout(resolve, 100));
            this.scrollToCurrentQuestion();
            console.log(`✅ Estado restaurado: Pregunta ${state.questionNumber} cargada y navegada`);
          } else {
            this.loadingSpecificQuestion = false;
            console.warn(`⚠️ No se pudo encontrar la pregunta ${state.questionNumber} después de cargar`);
          }
        }
      }
    } catch (error) {
      console.error('Error al restaurar posición:', error);
    } finally {
      // Siempre marcar que terminamos de restaurar después de un pequeño delay
      // para asegurar que todos los scrolls hayan terminado
      setTimeout(() => {
        this.isRestoringState = false;
      }, 1000);
    }
  }

  /**
   * Ir a la pregunta anterior
   */
  goToPreviousQuestion() {
    if (this.currentQuestionIndex > 0) {
      this.currentQuestionIndex--;
      this.scrollToCurrentQuestion();
      this.saveState();
    }
  }

  /**
   * Ir a la pregunta siguiente
   */
  goToNextQuestion() {
    if (this.currentQuestionIndex < this.questions.length - 1) {
      this.currentQuestionIndex++;
      this.scrollToCurrentQuestion();
      this.saveState();
    }
  }

  /**
   * Scroll a la pregunta actual
   * @param navigateToPdf - Si es true, también navega al PDF (default: true)
   */
  scrollToCurrentQuestion(navigateToPdf: boolean = true) {
    if (this.currentQuestionIndex >= 0 && this.currentQuestionIndex < this.questions.length) {
      const question = this.questions[this.currentQuestionIndex];
      this.scrollToQuestion(question.numberQuestion);

      // Si la pregunta tiene página, navegar al PDF (solo si no estamos restaurando o se indica explícitamente)
      if (navigateToPdf && question.startPage && !this.isRestoringState) {
        this.goToPage(question.startPage);
      }
    }
  }

  /**
   * Manejar cambio en el input de pregunta
   */
  onQuestionInputChange(event: any) {
    const questionNumber = parseInt(event.target.value);
    if (isNaN(questionNumber) || questionNumber < 1) {
      return;
    }

    // Buscar la pregunta por número
    const index = this.questions.findIndex(q => q.numberQuestion === questionNumber);

    if (index !== -1) {
      // La pregunta está cargada, navegar a ella
      this.currentQuestionIndex = index;
      this.scrollToCurrentQuestion();
    } else {
      // La pregunta no está cargada aún, mostrar skeleton
      this.loadingSpecificQuestion = true;

      // Intentar cargar más preguntas hasta encontrarla
      this.loadQuestionByNumber(questionNumber).then(() => {
        // Después de cargar, buscar de nuevo y hacer scroll
        setTimeout(() => {
          const newIndex = this.questions.findIndex(q => q.numberQuestion === questionNumber);
          if (newIndex >= 0) {
            this.currentQuestionIndex = newIndex;
            this.loadingSpecificQuestion = false;

            // Esperar a que se quite el skeleton antes de hacer scroll
            setTimeout(() => {
              this.scrollToCurrentQuestion();
            }, 100);
          } else {
            this.loadingSpecificQuestion = false;
            this.showError(`No se pudo cargar la pregunta ${questionNumber}`);
          }
        }, 300);
      });
    }
  }

  /**
   * Cargar preguntas hasta encontrar una específica
   * NOTA: El servicio mantiene las preguntas ordenadas por numberQuestion
   * y elimina duplicados automáticamente, por lo que el orden siempre es correcto.
   */
  async loadQuestionByNumber(questionNumber: number) {
    if (!this.selectedExam) return;

    // Si el número de pregunta está fuera del rango total, mostrar error
    if (questionNumber > this.totalQuestions) {
      this.showError(`La pregunta ${questionNumber} no existe. Hay ${this.totalQuestions} preguntas en total.`);
      return;
    }

    // Cargar todas las preguntas hasta el número deseado
    // Calcular cuántas páginas necesitamos cargar
    const itemsPerPage = 20;
    const pageNeeded = Math.ceil(questionNumber / itemsPerPage);
    const currentPage = Math.ceil(this.questions.length / itemsPerPage);

    if (pageNeeded > currentPage && this.hasMore) {
      // Necesitamos cargar más páginas
      this.loading = true;

      try {
        // Cargar múltiples páginas si es necesario
        for (let page = currentPage + 1; page <= pageNeeded; page++) {
          await this.examQuestionService.loadNextPage(this.selectedExam.id, {
            itemPerPage: itemsPerPage,
            sort: 'numberQuestion_asc'
          }).toPromise();

          // Verificar si ya encontramos la pregunta
          const index = this.questions.findIndex(q => q.numberQuestion === questionNumber);
          if (index !== -1) {
            this.currentQuestionIndex = index;
            this.scrollToCurrentQuestion();
            return;
          }
        }
      } catch (error) {
        this.showError('Error al cargar más preguntas');
      } finally {
        this.loading = false;
      }
    }

    // Verificar una vez más si la pregunta está ahora
    const index = this.questions.findIndex(q => q.numberQuestion === questionNumber);
    if (index !== -1) {
      this.currentQuestionIndex = index;
      this.scrollToCurrentQuestion();
    } else {
      this.showError(`No se pudo encontrar la pregunta ${questionNumber}`);
    }
  }
}
