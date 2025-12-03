import { Component, OnInit, OnDestroy, ViewChild, ElementRef } from '@angular/core';
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
  chevronDown
} from 'ionicons/icons';
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
export class ExamQuestionPage implements OnInit, OnDestroy {
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
  hasMore = true;
  showAlert = false;
  alertMessage = '';
  showToast = false;
  toastMessage = '';

  // PDF.js
  private pdfDoc: any = null;
  private renderedPages: Set<number> = new Set();
  private pageObserver: IntersectionObserver | null = null;
  private readonly INITIAL_PAGES_TO_RENDER = 5; // Solo renderizar las primeras 5 páginas
  private readonly PAGES_PER_BATCH = 3; // Renderizar 3 páginas a la vez cuando se hace scroll

  // Lifecycle
  private destroy$ = new Subject<void>();

  constructor(
    private examQuestionService: ExamQuestionService,
    private router: Router
  ) {
    addIcons({
      refresh,
      documentText,
      chevronUp,
      chevronDown,
      checkmarkCircle,
      alertCircle,
      arrowBack,
      arrowForward,
      search,
    });
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
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
    this.examQuestionService.clearState();
    if (this.pageObserver) {
      this.pageObserver.disconnect();
    }
  }

  /**
   * Cuando se selecciona un PDF del dropdown
   */
  async onExamSelected(event: any) {
    const examId = event.detail.value;
    this.selectedExam = this.availablePdfs.find(pdf => pdf.id === examId) || null;

    if (this.selectedExam) {
      // Cargar el PDF
      this.loadPdf(this.selectedExam.path);

      // Cargar las primeras preguntas
      this.examQuestionService.refreshQuestions(this.selectedExam.id, {
        itemPerPage: 20,
        sort: 'numberQuestion_asc'
      }).pipe(takeUntil(this.destroy$)).subscribe({
        next: (response) => {
          this.totalQuestions = response.total;
          this.currentQuestionIndex = this.questions.length > 0 ? 0 : -1;
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

      // Configurar observer para detectar la página visible
      this.setupPageObserver();

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
    console.log('Container encontrado:', container);

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

    // Renderizar TODAS las páginas (no lazy loading)
    await this.renderPageRange(1, this.totalPages, containerWidth);

    // Configurar observer para detectar página visible
    this.setupPageObserver();
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
   * Configurar observer para detectar la página visible
   */
  setupPageObserver() {
    const options = {
      root: document.querySelector('.pdf-viewer'),
      rootMargin: '0px',
      threshold: 0.5
    };

    this.pageObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const pageNum = parseInt(entry.target.getAttribute('data-page-number') || '1');
          this.currentPdfPage = pageNum;
        }
      });
    }, options);

    // Observar todas las páginas
    const pages = document.querySelectorAll('.pdf-page-wrapper');
    pages.forEach(page => this.pageObserver?.observe(page));
  }

  /**
   * Ir a una página específica
   */
  async goToPage(page: number) {
    if (page < 1 || page > this.totalPages) return;

    const pageElement = document.getElementById(`pdf-page-${page}`);
    if (pageElement) {
      // Calcular la diferencia entre la página actual y la destino
      const pageDiff = Math.abs(page - this.currentPdfPage);

      // Si el salto es mayor a 10 páginas, hacer scroll instantáneo
      // Si es menor, usar smooth scroll
      const behavior = pageDiff > 10 ? 'auto' : 'smooth';

      pageElement.scrollIntoView({ behavior: behavior as ScrollBehavior, block: 'start' });
      this.currentPdfPage = page;
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
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });

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

    this.examQuestionService.refreshQuestions(this.selectedExam.id, {
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
   * Ir a la pregunta anterior
   */
  goToPreviousQuestion() {
    if (this.currentQuestionIndex > 0) {
      this.currentQuestionIndex--;
      this.scrollToCurrentQuestion();
    }
  }

  /**
   * Ir a la pregunta siguiente
   */
  goToNextQuestion() {
    if (this.currentQuestionIndex < this.questions.length - 1) {
      this.currentQuestionIndex++;
      this.scrollToCurrentQuestion();
    }
  }

  /**
   * Scroll a la pregunta actual
   */
  scrollToCurrentQuestion() {
    if (this.currentQuestionIndex >= 0 && this.currentQuestionIndex < this.questions.length) {
      const question = this.questions[this.currentQuestionIndex];
      this.scrollToQuestion(question.numberQuestion);

      // Si la pregunta tiene página, navegar al PDF
      if (question.startPage) {
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
      // La pregunta no está cargada aún
      this.showInfo(`Pregunta ${questionNumber} no encontrada. Cargando más preguntas...`);

      // Intentar cargar más preguntas hasta encontrarla
      this.loadQuestionByNumber(questionNumber);
    }
  }

  /**
   * Cargar preguntas hasta encontrar una específica
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
