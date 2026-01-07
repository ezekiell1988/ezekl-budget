"""
Endpoints para gestión de preguntas de examen.
Proporciona funcionalidad para consultar preguntas de examen con autenticación.
"""

import json
import logging
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from typing import Optional, Dict
from app.database.connection import execute_sp
from app.utils.auth import get_current_user
from app.models.auth import CurrentUser
from app.models.exam_question import (
    ExamQuestionListResponse,
    ExamQuestionErrorResponse,
    SetQuestionRequest,
    SetQuestionResponse,
    SetToQuestionRequest,
    SetToQuestionResponse
)

# Configurar logging
logger = logging.getLogger(__name__)

# Router para endpoints de preguntas de examen
router = APIRouter(prefix="/exam-questions", tags=["Preguntas de Examen"])


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
    current_user: CurrentUser = Depends(get_current_user)
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
    logger.info(f"Usuario {current_user.get('user', {}).get('emailLogin')} consultando preguntas del examen {idExam}")
    
    try:
        # Obtener idLogin del usuario autenticado
        user_data = current_user.get('user', {})
        id_login = user_data.get('idLogin')
        
        if not id_login:
            logger.error(f"Usuario sin idLogin: {current_user}")
            raise HTTPException(
                status_code=401,
                detail="Token de usuario inválido: falta información del usuario"
            )
        
        # Construir el objeto de request para el SP
        request_data = {
            "search": search,
            "sort": sort,
            "page": page,
            "itemPerPage": itemPerPage,
            "idExam": idExam,
            "idLogin": id_login
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


@router.post(
    "/set-question",
    response_model=SetQuestionResponse,
    summary="Marcar pregunta como vista/completada",
    description="""Marca una pregunta de examen como vista o completada por el usuario autenticado.
    
    Este endpoint registra el progreso del usuario en un examen específico:
    
    **Funcionalidades:**
    - Crea o actualiza el registro de progreso del usuario
    - Asocia automáticamente con el usuario autenticado (desde JWT)
    - Idempotente: múltiples llamadas con los mismos datos no crean duplicados
    
    **Autenticación:**
    - Requiere token JWT válido en el header Authorization
    - Header: `Authorization: Bearer {token}`
    - El idLogin se obtiene automáticamente del token
    - El idCompany se obtiene automáticamente del token
    
    **Body (JSON):**
    - `idExamQuestion`: ID de la pregunta del examen a marcar
    
    **Respuesta:**
    - `success`: true si la operación fue exitosa
    - `message`: Mensaje descriptivo de la operación
    
    **Ejemplo de uso:**
    ```json
    POST /exam-questions/set-question
    {
      "idExamQuestion": 42
    }
    ```
    """,
    responses={
        200: {
            "description": "Pregunta marcada exitosamente",
            "model": SetQuestionResponse
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
async def set_question(
    request: SetQuestionRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Marca una pregunta como vista/completada por el usuario autenticado.
    
    Args:
        request: Datos de la pregunta a marcar
        current_user: Usuario autenticado (inyectado por Depends)
    
    Returns:
        SetQuestionResponse: Confirmación de la operación
        
    Raises:
        HTTPException: Si hay error en la operación o en la base de datos
    """
    logger.info(f"Usuario {current_user.get('user', {}).get('emailLogin')} marcando pregunta {request.idExamQuestion}")
    
    try:
        # Obtener idLogin y idCompany del usuario autenticado
        user_data = current_user.get('user', {})
        id_login = user_data.get('idLogin')
        id_company = user_data.get('idCompany')
        
        if not id_login:
            logger.error(f"Usuario sin idLogin: {current_user}")
            raise HTTPException(
                status_code=401,
                detail="Token de usuario inválido: falta información del usuario"
            )
        
        # Construir el JSON para el SP
        request_data = {
            "idLogin": id_login,
            "idExamQuestion": request.idExamQuestion
        }
        
        # Ejecutar el stored procedure
        result = await execute_sp("spLoginExamQuestionSetQuestion", request_data)
        
        logger.info(f"Pregunta {request.idExamQuestion} marcada exitosamente para usuario {id_login}")
        
        return SetQuestionResponse(
            success=True,
            message="Pregunta marcada exitosamente"
        )
        
    except HTTPException:
        # Re-lanzar HTTPException sin modificar
        raise
    except Exception as e:
        logger.error(f"Error al marcar pregunta: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al marcar pregunta: {str(e)}"
        )


@router.post(
    "/set-to-question",
    response_model=SetToQuestionResponse,
    summary="Marcar preguntas hasta un número específico",
    description="""Marca todas las preguntas desde la 1 hasta el número especificado como leídas/completadas.
    
    Este endpoint sincroniza el progreso del usuario en un examen:
    
    **Funcionalidades:**
    - Marca como leídas todas las preguntas desde 1 hasta `numberQuestion`
    - Elimina marcas de preguntas posteriores a `numberQuestion` (si existen)
    - Asocia automáticamente con el usuario autenticado (desde JWT)
    - Idempotente: múltiples llamadas producen el mismo resultado
    
    **Casos de uso:**
    - Marcar progreso al navegar por preguntas
    - Sincronizar estado cuando el usuario vuelve atrás
    - Actualizar progreso en lote
    
    **Autenticación:**
    - Requiere token JWT válido en el header Authorization
    - Header: `Authorization: Bearer {token}`
    - El idLogin se obtiene automáticamente del token
    
    **Body (JSON):**
    - `idExam`: ID del examen
    - `numberQuestion`: Número hasta donde marcar (ejemplo: 50 marca preguntas 1-50)
    
    **Respuesta:**
    - `success`: true si la operación fue exitosa
    - `message`: Mensaje descriptivo de la operación
    - `recordsInserted`: Cantidad de preguntas nuevas marcadas
    - `recordsDeleted`: Cantidad de marcas eliminadas (preguntas posteriores)
    - `totalChanges`: Total de cambios realizados
    
    **Ejemplo de uso:**
    ```json
    POST /exam-questions/set-to-question
    {
      "idExam": 1,
      "numberQuestion": 50
    }
    ```
    
    **Ejemplo de respuesta:**
    ```json
    {
      "success": true,
      "message": "Progreso actualizado: 15 preguntas marcadas, 5 desmarcadas",
      "recordsInserted": 15,
      "recordsDeleted": 5,
      "totalChanges": 20
    }
    ```
    """,
    responses={
        200: {
            "description": "Progreso actualizado exitosamente",
            "model": SetToQuestionResponse
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
async def set_to_question(
    request: SetToQuestionRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Marca preguntas hasta un número específico como leídas/completadas.
    
    Args:
        request: Datos del examen y número de pregunta
        current_user: Usuario autenticado (inyectado por Depends)
    
    Returns:
        SetToQuestionResponse: Resultado de la operación con estadísticas
        
    Raises:
        HTTPException: Si hay error en la operación o en la base de datos
    """
    logger.info(
        f"Usuario {current_user.get('user', {}).get('emailLogin')} marcando hasta pregunta {request.numberQuestion} "
        f"del examen {request.idExam}"
    )
    
    try:
        # Obtener idLogin del usuario autenticado
        user_data = current_user.get('user', {})
        id_login = user_data.get('idLogin')
        
        if not id_login:
            logger.error(f"Usuario sin idLogin: {current_user}")
            raise HTTPException(
                status_code=401,
                detail="Token de usuario inválido: falta información del usuario"
            )
        
        # Construir el JSON para el SP
        request_data = {
            "idLogin": id_login,
            "idExam": request.idExam,
            "numberQuestion": request.numberQuestion
        }
        
        # Ejecutar el stored procedure
        await execute_sp("spLoginExamQuestionSetToQuestion", request_data)
        
        logger.info(
            f"Progreso actualizado hasta pregunta {request.numberQuestion} del examen {request.idExam} "
            f"para usuario {id_login}"
        )
        
        return SetToQuestionResponse(
            success=True,
            message=f"Progreso actualizado hasta la pregunta {request.numberQuestion}"
        )
        
    except HTTPException:
        # Re-lanzar HTTPException sin modificar
        raise
    except Exception as e:
        logger.error(f"Error al marcar preguntas hasta {request.numberQuestion}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar progreso: {str(e)}"
        )
