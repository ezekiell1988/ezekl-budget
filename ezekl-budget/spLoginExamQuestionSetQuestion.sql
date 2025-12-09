CREATE OR ALTER PROCEDURE spLoginExamQuestionSetQuestion
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  DECLARE @idLoginExamQuestion INT = (
    SELECT LEQ.idLoginExamQuestion
    FROM tbLoginExamQuestion LEQ
    INNER JOIN OPENJSON(@json) WITH (
      idCompany INT
      , idLogin INT
      , idExamQuestion INT
    ) J
    ON J.idLogin = LEQ.idLogin
    AND J.idExamQuestion = LEQ.idExamQuestion
  );

  IF @idLoginExamQuestion IS NULL
  BEGIN
    -- Crear pregunta del examen
    INSERT INTO tbLoginExamQuestion (
      idLogin, idExamQuestion
    ) VALUES (
      JSON_VALUE(@json, '$.idLogin')
      , JSON_VALUE(@json, '$.idExamQuestion')
    );
    -- Guardar id registro
    SET @idLoginExamQuestion = SCOPE_IDENTITY();
  END
  ELSE
  BEGIN
    -- Actualizar pregunta del examen
    UPDATE LEQ
    SET LEQ.idExamQuestion = ISNULL(JSON_VALUE(@json, '$.idExamQuestion'), LEQ.idExamQuestion)
    FROM tbLoginExamQuestion LEQ
    WHERE LEQ.idLoginExamQuestion = @idLoginExamQuestion;
  END

  -- Verificar si se actualizó algún registro
  IF @@ROWCOUNT = 0
  BEGIN
    IF @idLoginExamQuestion IS NULL
      RAISERROR(N'El parámetro idLoginExamQuestion es requerido y no puede ser NULL.', 16, 1);
    ELSE
      RAISERROR(N'No se encontró LoginExamQuestion con ID %d.', 16, 1, @idLoginExamQuestion);
    RETURN;
  END

  -- Operación exitosa (sin retorno de datos necesario)
END
GO

-- Probar el procedimiento
EXEC spLoginExamQuestionSetQuestion @json = N'{
  "idCompany": 1,
  "idLogin": 1,
  "idExamQuestion": 1
}';