CREATE OR ALTER PROCEDURE spLoginExamQuestionSetToQuestion
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  DECLARE @idLogin INT = JSON_VALUE(@json, '$.idLogin');
  DECLARE @idExam INT = JSON_VALUE(@json, '$.idExam');
  DECLARE @numberQuestion INT = JSON_VALUE(@json, '$.numberQuestion');

  -- Obtener todas las preguntas del examen hasta el número especificado
  ; WITH examQuestions AS (
    SELECT EQ.idExamQuestion, Q.numberQuestion
    FROM tbExamQuestion EQ
    INNER JOIN tbQuestion Q
    ON Q.idQuestion = EQ.idQuestion
    WHERE EQ.idExam = @idExam
    AND Q.numberQuestion <= @numberQuestion
  ), examQuestionsAction AS (
    SELECT 
      EQ.idExamQuestion,
      EQ.numberQuestion,
      LEQ.idLoginExamQuestion,
      CAST(CASE WHEN LEQ.idLoginExamQuestion IS NULL THEN 0 ELSE 1 END AS BIT) AS [exist]
    FROM examQuestions EQ
    LEFT JOIN tbLoginExamQuestion LEQ
    ON LEQ.idExamQuestion = EQ.idExamQuestion
    AND LEQ.idLogin = @idLogin
  )
  -- Insertar nuevos registros (donde exist = 0)
  INSERT INTO tbLoginExamQuestion (idLogin, idExamQuestion)
  SELECT @idLogin, idExamQuestion
  FROM examQuestionsAction
  WHERE [exist] = 0;

  -- Eliminar registros que están de más (preguntas > numberQuestion para este examen y usuario)
  DELETE LEQ
  FROM tbLoginExamQuestion LEQ
  INNER JOIN tbExamQuestion EQ
  ON EQ.idExamQuestion = LEQ.idExamQuestion
  INNER JOIN tbQuestion Q
  ON Q.idQuestion = EQ.idQuestion
  WHERE LEQ.idLogin = @idLogin
  AND EQ.idExam = @idExam
  AND Q.numberQuestion > @numberQuestion;

  -- Retornar resumen de la operación
END
GO

-- Probar el procedimiento
-- EXEC spLoginExamQuestionSetToQuestion @json = N'{
--   "idLogin": 1,
--   "idExam": 1,
--   "numberQuestion": 200
-- }';