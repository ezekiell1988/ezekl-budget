"""
Endpoints para gestión de preguntas de examen.
Proporciona funcionalidad para consultar preguntas de examen con autenticación.
"""

import json
import logging
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from typing import Optional, Dict
from app.database.connection import execute_sp
from app.api.routes.auth import get_current_user
from app.models.exam_question import (
    ExamQuestion,
    ExamQuestionListRequest,
    ExamQuestionListResponse,
    ExamQuestionErrorResponse
)

# Configurar logging
logger = logging.getLogger(__name__)

# Router para endpoints de preguntas de examen
router = APIRouter()


@router.get(
    "/{idExam}/questions.json",
    response_model=ExamQuestionListResponse,
    summary="Obtener preguntas de examen paginadas",
    description="""Obtiene una lista paginada de preguntas de examen.
    
    Este endpoint permite consultar las preguntas de un examen específico con las siguientes características:
    
    **Funcionalidades:**
    - Paginación configurable (página y elementos por página)
    - Búsqueda por texto en preguntas (búsqueda parcial, case-insensitive)
    - Ordenamiento por número de pregunta (ascendente o descendente)
    - Filtrado por examen específico
    
    **Parámetros de ordenamiento disponibles:**
    - `numberQuestion_asc`: Por número de pregunta ascendente (default)
    - `numberQuestion_desc`: Por número de pregunta descendente
    
    **Autenticación:**
    - Requiere token JWT válido en el header Authorization
    - Header: `Authorization: Bearer {token}`
    
    **Paginación:**
    - `page`: Número de página (inicia en 1, default: 1)
    - `itemPerPage`: Elementos por página (1-100, default: 10)
    
    **Respuesta:**
    - `total`: Total de registros que coinciden con el filtro
    - `data`: Array de preguntas para la página solicitada
    
    **Ejemplos de uso:**
    - Obtener primeras 10 preguntas: `GET /exam-questions?idExam=1`
    - Buscar pregunta específica: `GET /exam-questions?idExam=1&search=Azure`
    - Página 2 con 25 elementos: `GET /exam-questions?idExam=1&page=2&itemPerPage=25`
    - Ordenar descendente: `GET /exam-questions?idExam=1&sort=numberQuestion_desc`
    """,
    responses={
        200: {
            "description": "Lista de preguntas obtenida exitosamente",
            "model": ExamQuestionListResponse
        },
        401: {
            "description": "Token de autorización requerido, inválido o expirado"
        },
        500: {
            "description": "Error interno del servidor",
            "model": ExamQuestionErrorResponse
        }
    }
)
async def get_exam_questions(
    idExam: int = Path(
        ...,
        description="ID del examen del cual obtener las preguntas",
        example=1
    ),
    search: Optional[str] = Query(
        None,
        description="Término de búsqueda para filtrar preguntas",
        max_length=50
    ),
    sort: Optional[str] = Query(
        "numberQuestion_asc",
        description="Campo y dirección de ordenamiento",
        regex="^(numberQuestion_asc|numberQuestion_desc)$",
        example="numberQuestion_asc"
    ),
    page: Optional[int] = Query(
        1,
        ge=1,
        description="Número de página (inicia en 1)",
        example=1
    ),
    itemPerPage: Optional[int] = Query(
        10,
        ge=1,
        le=100,
        description="Número de elementos por página (máximo 100)",
        example=10
    ),
    current_user: Dict = Depends(get_current_user)
):
    """
    Obtiene una lista paginada de preguntas de un examen específico.
    
    Args:
        idExam: ID del examen
        search: Término de búsqueda (opcional)
        sort: Campo de ordenamiento (opcional)
        page: Número de página (opcional)
        itemPerPage: Elementos por página (opcional)
        current_user: Usuario autenticado (inyectado por Depends)
    
    Returns:
        ExamQuestionListResponse: Lista paginada de preguntas
        
    Raises:
        HTTPException: Si hay error en la consulta o en la base de datos
    """
    logger.info(f"Usuario {current_user.get('email')} consultando preguntas del examen {idExam}")
    
    try:
        # Construir el objeto de request para el SP
        request_data = {
            "search": search,
            "sort": sort,
            "page": page,
            "itemPerPage": itemPerPage,
            "idExam": idExam
        }
        
        # Ejecutar el stored procedure
        result = await execute_sp("spExamQuestionGet", request_data)
        
        # Verificar que el resultado tenga datos
        if not result:
            logger.warning(f"No se encontraron resultados para el examen {idExam}")
            return ExamQuestionListResponse(total=0, data=[])
        
        # El SP retorna un diccionario con el JSON ya parseado
        # Si viene como string, parsearlo
        if isinstance(result, str):
            parsed_result = json.loads(result)
        elif isinstance(result, dict):
            # Si el resultado tiene una clave 'json', extraerla
            if 'json' in result:
                json_data = result['json']
                parsed_result = json.loads(json_data) if isinstance(json_data, str) else json_data
            else:
                parsed_result = result
        else:
            parsed_result = result
        
        # Extraer total y data
        total = parsed_result.get("total", 0)
        data = parsed_result.get("data", [])
        
        logger.info(f"Se encontraron {total} preguntas para el examen {idExam}, retornando página {page}")
        
        return ExamQuestionListResponse(
            total=total,
            data=data
        )
        
    except json.JSONDecodeError as e:
        logger.error(f"Error al parsear JSON: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar la respuesta de la base de datos: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error al obtener preguntas del examen: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener preguntas del examen: {str(e)}"
        )
