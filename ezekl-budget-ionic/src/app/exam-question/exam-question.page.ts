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
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  IonInfiniteScroll,
  IonInfiniteScrollContent,
  IonSpinner,
  IonText,
  IonButton,
  IonIcon,
  IonSelect,
  IonSelectOption,
  IonRefresher,
  IonRefresherContent,
  IonAlert,
  IonToast,
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import {
  arrowBack,
  arrowForward,
  documentText,
  checkmarkCircle,
  search,
  alertCircle,
  refresh
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
    IonCardHeader,
    IonCardTitle,
    IonCardContent,
    IonInfiniteScroll,
    IonInfiniteScrollContent,
    IonSpinner,
    IonText,
    IonButton,
    IonIcon,
    IonSelect,
    IonSelectOption,
    IonRefresher,
    IonRefresherContent,
    IonAlert,
    IonToast,
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

  // Estados
  loading = false;
  hasMore = true;
  showAlert = false;
  alertMessage = '';
  showToast = false;
  toastMessage = '';

  // PDF.js
  private pdfDoc: any = null;
  private pageRendering = false;
  private pageNumPending: number | null = null;

  // Lifecycle
  private destroy$ = new Subject<void>();

  constructor(
    private examQuestionService: ExamQuestionService,
    private router: Router
  ) {
    addIcons({
      arrowBack,
      arrowForward,
      documentText,
      checkmarkCircle,
      search,
      alertCircle,
      refresh,
    });
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
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
    this.examQuestionService.clearState();
  }

  /**
   * Cuando se selecciona un PDF del dropdown
   */
  async onExamSelected(event: any) {
    const examId = event.detail.value;
    this.selectedExam = this.availablePdfs.find(pdf => pdf.id === examId) || null;

    if (this.selectedExam) {
      // Cargar el PDF
      await this.loadPdf(this.selectedExam.path);

      // Cargar las primeras preguntas
      this.examQuestionService.refreshQuestions(this.selectedExam.id, {
        itemPerPage: 20,
        sort: 'numberQuestion_asc'
      }).pipe(takeUntil(this.destroy$)).subscribe();
    }
  }

  /**
   * Cargar PDF usando PDF.js
   */
  async loadPdf(pdfPath: string) {
    try {
      // Verificar que PDF.js esté disponible
      if (typeof (window as any).pdfjsLib === 'undefined') {
        this.showError('PDF.js no está disponible. Por favor, recarga la página.');
        return;
      }

      const pdfjsLib = (window as any).pdfjsLib;

      // Cargar documento PDF
      const loadingTask = pdfjsLib.getDocument(pdfPath);
      this.pdfDoc = await loadingTask.promise;
      this.totalPages = this.pdfDoc.numPages;

      // Renderizar primera página
      await this.renderPage(1);

    } catch (error) {
      console.error('Error cargando PDF:', error);
      this.showError('Error al cargar el PDF. Verifica que el archivo existe.');
    }
  }

  /**
   * Renderizar una página del PDF
   */
  async renderPage(pageNum: number) {
    if (this.pageRendering) {
      this.pageNumPending = pageNum;
      return;
    }

    this.pageRendering = true;
    this.currentPdfPage = pageNum;

    try {
      const page = await this.pdfDoc.getPage(pageNum);
      const canvas = document.getElementById('pdf-canvas') as HTMLCanvasElement;

      if (!canvas) {
        this.pageRendering = false;
        return;
      }

      const context = canvas.getContext('2d');
      if (!context) {
        this.pageRendering = false;
        return;
      }

      // Calcular escala basada en el ancho del contenedor
      const containerWidth = this.pdfContainer?.nativeElement?.clientWidth || 800;
      const viewport = page.getViewport({ scale: 1 });
      const scale = containerWidth / viewport.width;
      const scaledViewport = page.getViewport({ scale });

      canvas.height = scaledViewport.height;
      canvas.width = scaledViewport.width;

      const renderContext = {
        canvasContext: context,
        viewport: scaledViewport,
      };

      await page.render(renderContext).promise;

      this.pageRendering = false;

      // Si hay una página pendiente, renderizarla
      if (this.pageNumPending !== null) {
        const pending = this.pageNumPending;
        this.pageNumPending = null;
        await this.renderPage(pending);
      }

      // Buscar pregunta asociada a esta página
      this.checkQuestionForCurrentPage();

    } catch (error) {
      console.error('Error renderizando página:', error);
      this.pageRendering = false;
    }
  }

  /**
   * Navegar a página anterior del PDF
   */
  async previousPage() {
    if (this.currentPdfPage <= 1) return;
    await this.renderPage(this.currentPdfPage - 1);
  }

  /**
   * Navegar a página siguiente del PDF
   */
  async nextPage() {
    if (this.currentPdfPage >= this.totalPages) return;
    await this.renderPage(this.currentPdfPage + 1);
  }

  /**
   * Ir a una página específica
   */
  async goToPage(page: number) {
    if (page < 1 || page > this.totalPages) return;
    await this.renderPage(page);
  }

  /**
   * Click en el canvas del PDF - buscar pregunta asociada
   */
  async onPdfClick() {
    const question = this.examQuestionService.findQuestionByPage(this.currentPdfPage);

    if (question) {
      this.scrollToQuestion(question.numberQuestion);
      this.showInfo(`Pregunta ${question.numberQuestion} encontrada`);
    } else {
      this.showInfo(`No hay pregunta asociada a la página ${this.currentPdfPage}`);
    }
  }

  /**
   * Verificar si hay pregunta para la página actual
   */
  checkQuestionForCurrentPage() {
    const question = this.examQuestionService.findQuestionByPage(this.currentPdfPage);
    // Opcionalmente, puedes resaltar la pregunta en la lista
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
    }).pipe(takeUntil(this.destroy$)).subscribe(() => {
      event.target.complete();
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
    }).pipe(takeUntil(this.destroy$)).subscribe(() => {
      event.target.complete();
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
}
