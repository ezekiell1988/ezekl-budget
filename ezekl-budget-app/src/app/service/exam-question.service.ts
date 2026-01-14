import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { BehaviorSubject, Observable, of } from 'rxjs';
import { tap, catchError, map } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { LoggerService } from './logger.service';
import {
  ExamQuestion,
  ExamQuestionListResponse,
  ExamQuestionParams,
  ApiResponse
} from '../shared/models';

/**
 * Servicio para gestionar preguntas de examen
 * Siguiendo buenas prácticas de Angular 20+
 */
@Injectable({
  providedIn: 'root'
})
export class ExamQuestionService {
  private readonly API_BASE = `${environment.apiUrl}exam-questions`;
  private readonly http = inject(HttpClient);
  private readonly logger = inject(LoggerService).getLogger('ExamQuestionService');

  // Estado de la lista actual
  private questions$ = new BehaviorSubject<ExamQuestion[]>([]);
  private loading$ = new BehaviorSubject<boolean>(false);
  private error$ = new BehaviorSubject<string | null>(null);
  private currentPage$ = new BehaviorSubject<number>(1);
  private totalItems$ = new BehaviorSubject<number>(0);
  private hasMore$ = new BehaviorSubject<boolean>(true);

  // Observables públicos
  get questions(): Observable<ExamQuestion[]> {
    return this.questions$.asObservable();
  }

  get loading(): Observable<boolean> {
    return this.loading$.asObservable();
  }

  get error(): Observable<string | null> {
    return this.error$.asObservable();
  }

  get hasMore(): Observable<boolean> {
    return this.hasMore$.asObservable();
  }

  get totalItems(): Observable<number> {
    return this.totalItems$.asObservable();
  }

  /**
   * Obtiene preguntas de un examen específico
   */
  getExamQuestions(idExam: number, params: ExamQuestionParams = {}): Observable<ExamQuestionListResponse> {
    this.loading$.next(true);
    this.error$.next(null);

    let httpParams = new HttpParams();
    if (params.search) httpParams = httpParams.set('search', params.search);
    if (params.sort) httpParams = httpParams.set('sort', params.sort);
    if (params.page) httpParams = httpParams.set('page', params.page.toString());
    if (params.itemPerPage) httpParams = httpParams.set('itemPerPage', params.itemPerPage.toString());

    this.logger.debug(`Cargando preguntas del examen ${idExam}`, params);

    return this.http.get<ExamQuestionListResponse>(
      `${this.API_BASE}/${idExam}/questions.json`,
      { params: httpParams }
    ).pipe(
      tap(response => {
        this.loading$.next(false);
        this.totalItems$.next(response.total);
        this.logger.debug(`Preguntas cargadas: ${response.data.length} de ${response.total}`);
      }),
      catchError(error => {
        this.loading$.next(false);
        const errorMessage = error.message || 'Error al cargar preguntas';
        this.error$.next(errorMessage);
        this.logger.error('Error al cargar preguntas:', error);
        return of({ total: 0, data: [] });
      })
    );
  }

  /**
   * Carga preguntas con infinite scroll
   */
  loadQuestions(
    idExam: number, 
    params: ExamQuestionParams = {}, 
    append: boolean = false
  ): Observable<ExamQuestion[]> {
    const page = append ? this.currentPage$.value + 1 : 1;

    return this.getExamQuestions(idExam, { ...params, page }).pipe(
      tap(response => {
        let updatedQuestions: ExamQuestion[];

        if (append) {
          // Combinar preguntas existentes con las nuevas, eliminando duplicados
          const currentQuestions = this.questions$.value;
          const existingNumbers = new Set(currentQuestions.map(q => q.numberQuestion));

          // Agregar solo preguntas que no existen
          const newUniqueQuestions = response.data.filter(
            q => !existingNumbers.has(q.numberQuestion)
          );
          updatedQuestions = [...currentQuestions, ...newUniqueQuestions];

          // Ordenar por numberQuestion
          updatedQuestions.sort((a, b) => a.numberQuestion - b.numberQuestion);
          
          this.logger.debug(`Agregadas ${newUniqueQuestions.length} preguntas nuevas`);
        } else {
          // Si no es append, reemplazar todas las preguntas
          updatedQuestions = response.data;
          this.logger.debug('Preguntas reemplazadas completamente');
        }

        this.questions$.next(updatedQuestions);
        this.currentPage$.next(page);

        // Verificar si hay más páginas
        const totalPages = Math.ceil(response.total / (params.itemPerPage || 10));
        this.hasMore$.next(page < totalPages);
      }),
      map(response => response.data),
      catchError(error => {
        const errorMessage = error.message || 'Error al cargar preguntas';
        this.error$.next(errorMessage);
        this.logger.error('Error al cargar preguntas:', error);
        return of([]);
      })
    );
  }

  /**
   * Refresca la lista de preguntas
   */
  refreshQuestions(idExam: number, params: ExamQuestionParams = {}): Observable<ExamQuestion[]> {
    this.logger.debug('Refrescando lista de preguntas');
    this.clearState();
    return this.loadQuestions(idExam, params, false);
  }

  /**
   * Carga la siguiente página
   */
  loadNextPage(idExam: number, params: ExamQuestionParams = {}): Observable<ExamQuestion[]> {
    if (!this.hasMore$.value) {
      this.logger.debug('No hay más páginas para cargar');
      return of([]);
    }
    
    if (this.loading$.value) {
      this.logger.debug('Ya hay una carga en progreso');
      return of([]);
    }
    
    return this.loadQuestions(idExam, params, true);
  }

  /**
   * Busca una pregunta por número
   */
  findQuestionByNumber(questionNumber: number): ExamQuestion | undefined {
    return this.questions$.value.find(q => q.numberQuestion === questionNumber);
  }

  /**
   * Busca una pregunta por página del PDF
   */
  findQuestionByPage(page: number): ExamQuestion | undefined {
    return this.questions$.value.find(q =>
      q.startPage && q.endPage && page >= q.startPage && page <= q.endPage
    );
  }

  /**
   * Limpia el estado
   */
  clearState(): void {
    this.logger.debug('Limpiando estado del servicio');
    this.questions$.next([]);
    this.currentPage$.next(1);
    this.totalItems$.next(0);
    this.hasMore$.next(true);
    this.loading$.next(false);
    this.error$.next(null);
  }

  /**
   * Marca una pregunta como vista/completada
   */
  setQuestion(idExamQuestion: number): Observable<ApiResponse> {
    this.logger.debug(`Marcando pregunta ${idExamQuestion} como leída`);
    
    return this.http.post<ApiResponse>(
      `${this.API_BASE}/set-question`,
      { idExamQuestion }
    ).pipe(
      tap(response => {
        this.logger.debug('Pregunta marcada exitosamente:', response.message);
      }),
      catchError(error => {
        this.logger.error('Error al marcar pregunta:', error);
        throw error;
      })
    );
  }

  /**
   * Marca preguntas hasta un número específico
   */
  setToQuestion(idExam: number, numberQuestion: number): Observable<ApiResponse> {
    this.logger.debug(`Marcando preguntas hasta la #${numberQuestion} del examen ${idExam}`);
    
    return this.http.post<ApiResponse>(
      `${this.API_BASE}/set-to-question`,
      { idExam, numberQuestion }
    ).pipe(
      tap(response => {
        this.logger.debug('Preguntas marcadas exitosamente:', response.message);
      }),
      catchError(error => {
        this.logger.error('Error al marcar preguntas hasta número:', error);
        throw error;
      })
    );
  }

  /**
   * Obtiene el estado actual de las preguntas (para debugging)
   */
  getState(): {
    questionsCount: number;
    currentPage: number;
    totalItems: number;
    hasMore: boolean;
    loading: boolean;
    error: string | null;
  } {
    return {
      questionsCount: this.questions$.value.length,
      currentPage: this.currentPage$.value,
      totalItems: this.totalItems$.value,
      hasMore: this.hasMore$.value,
      loading: this.loading$.value,
      error: this.error$.value
    };
  }
}
