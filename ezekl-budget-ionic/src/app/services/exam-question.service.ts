import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { tap, catchError, map } from 'rxjs/operators';
import { of } from 'rxjs';
import {
  ExamQuestion,
  ExamQuestionListResponse,
  ExamQuestionParams
} from '../models';

/**
 * Servicio para gestionar preguntas de examen
 */
@Injectable({
  providedIn: 'root'
})
export class ExamQuestionService {
  private readonly API_BASE = '/api/v1/exam-questions';

  // Estado de la lista actual
  private questions$ = new BehaviorSubject<ExamQuestion[]>([]);
  private loading$ = new BehaviorSubject<boolean>(false);
  private error$ = new BehaviorSubject<string | null>(null);
  private currentPage$ = new BehaviorSubject<number>(1);
  private totalItems$ = new BehaviorSubject<number>(0);
  private hasMore$ = new BehaviorSubject<boolean>(true);

  constructor(private http: HttpClient) {}

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

    return this.http.get<ExamQuestionListResponse>(`${this.API_BASE}/${idExam}/questions.json`, { params: httpParams })
      .pipe(
        tap(response => {
          this.loading$.next(false);
          this.totalItems$.next(response.total);
        }),
        catchError(error => {
          this.loading$.next(false);
          this.error$.next(error.message || 'Error al cargar preguntas');
          return of({ total: 0, data: [] });
        })
      );
  }

  /**
   * Carga preguntas con infinite scroll
   */
  loadQuestions(idExam: number, params: ExamQuestionParams = {}, append: boolean = false): Observable<ExamQuestion[]> {
    const page = append ? this.currentPage$.value + 1 : 1;

    return this.getExamQuestions(idExam, { ...params, page }).pipe(
      tap(response => {
        let updatedQuestions: ExamQuestion[];

        if (append) {
          // Combinar preguntas existentes con las nuevas, eliminando duplicados
          const currentQuestions = this.questions$.value;
          const existingNumbers = new Set(currentQuestions.map(q => q.numberQuestion));

          // Agregar solo preguntas que no existen
          const newUniqueQuestions = response.data.filter(q => !existingNumbers.has(q.numberQuestion));
          updatedQuestions = [...currentQuestions, ...newUniqueQuestions];

          // Ordenar por numberQuestion
          updatedQuestions.sort((a, b) => a.numberQuestion - b.numberQuestion);
        } else {
          // Si no es append, reemplazar todas las preguntas
          updatedQuestions = response.data;
        }

        this.questions$.next(updatedQuestions);
        this.currentPage$.next(page);

        // Verificar si hay más páginas
        const totalPages = Math.ceil(response.total / (params.itemPerPage || 10));
        this.hasMore$.next(page < totalPages);
      }),
      map(response => response.data),
      catchError(error => {
        this.error$.next(error.message || 'Error al cargar preguntas');
        return of([]);
      })
    );
  }

  /**
   * Refresca la lista de preguntas
   */
  refreshQuestions(idExam: number, params: ExamQuestionParams = {}): Observable<ExamQuestion[]> {
    this.clearState();
    return this.loadQuestions(idExam, params, false);
  }

  /**
   * Carga la siguiente página
   */
  loadNextPage(idExam: number, params: ExamQuestionParams = {}): Observable<ExamQuestion[]> {
    if (!this.hasMore$.value || this.loading$.value) {
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
    this.questions$.next([]);
    this.currentPage$.next(1);
    this.totalItems$.next(0);
    this.hasMore$.next(true);
    this.loading$.next(false);
    this.error$.next(null);
  }
}
