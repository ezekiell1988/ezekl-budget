/**
 * Modelos TypeScript para preguntas de examen
 * Coinciden con los modelos Pydantic del backend FastAPI
 */

/**
 * Modelo para una pregunta de examen
 */
export interface ExamQuestion {
  idExamQuestion: number;
  numberQuestion: number;
  startPage?: number;
  endPage?: number;
  shortQuestion: string;
  questionContext?: string;
  communityDiscussion?: string;
  correctAnswer?: string;
  explanation?: string;
  imageExplanation?: string;
  readed?: boolean;
}

/**
 * Respuesta de la API para lista de preguntas
 */
export interface ExamQuestionListResponse {
  total: number;
  data: ExamQuestion[];
}

/**
 * Parámetros para consultar preguntas de examen
 */
export interface ExamQuestionParams {
  search?: string;
  sort?: 'numberQuestion_asc' | 'numberQuestion_desc';
  page?: number;
  itemPerPage?: number;
}

/**
 * Configuración de PDF de examen
 */
export interface ExamPdf {
  id: number;
  filename: string;
  displayName: string;
  path: string;
}

/**
 * Respuesta genérica de éxito/error
 */
export interface ApiResponse {
  success: boolean;
  message: string;
}
