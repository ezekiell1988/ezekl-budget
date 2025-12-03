"""
Modelos Pydantic para preguntas de examen.
Define los esquemas de datos para la gestión de preguntas de examen.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class ExamQuestion(BaseModel):
    """Modelo para una pregunta de examen."""
    numberQuestion: int = Field(..., description="Número de la pregunta")
    startPage: Optional[int] = Field(None, description="Página de inicio")
    endPage: Optional[int] = Field(None, description="Página de fin")
    shortQuestion: str = Field(..., description="Pregunta corta")
    questionContext: Optional[str] = Field(None, description="Contexto de la pregunta")
    communityDiscussion: Optional[str] = Field(None, description="Discusión de la comunidad")
    correctAnswer: Optional[str] = Field(None, description="Respuesta correcta")
    explanation: Optional[str] = Field(None, description="Explicación de la respuesta")
    imageExplanation: Optional[str] = Field(None, description="Imagen de explicación (URL o base64)")


class ExamQuestionListRequest(BaseModel):
    """Modelo de request para listar preguntas de examen."""
    search: Optional[str] = Field(None, max_length=50, description="Término de búsqueda")
    sort: Optional[str] = Field("numberQuestion_asc", description="Campo y dirección de ordenamiento")
    page: Optional[int] = Field(1, ge=1, description="Número de página")
    itemPerPage: Optional[int] = Field(10, ge=1, le=100, description="Elementos por página")
    idExam: int = Field(..., description="ID del examen")


class ExamQuestionListResponse(BaseModel):
    """Modelo de respuesta para lista de preguntas de examen."""
    total: int = Field(..., description="Total de registros")
    data: List[ExamQuestion] = Field(..., description="Lista de preguntas")


class ExamQuestionErrorResponse(BaseModel):
    """Modelo de respuesta para errores."""
    detail: str = Field(..., description="Mensaje de error")
