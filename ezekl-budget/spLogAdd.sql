CREATE OR ALTER PROCEDURE spLogAdd
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  DECLARE @idLog INT;
  
  -- Crear log
  INSERT INTO tbLog (typeLog, log)
  SELECT typeLog, log
  FROM OPENJSON(@json) WITH (
    typeLog VARCHAR(50)
    , log NVARCHAR(MAX) AS JSON
  );

  -- Obtener el ID del log creado
  SET @idLog = SCOPE_IDENTITY();

  -- Preparar respuesta JSON
  SET @json = JSON_QUERY((
    SELECT @idLog idLog
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));
  
  SELECT JSON_QUERY(@json) json;
END
GO

-- Probar el procedimiento
EXEC spLogAdd @json = N'{
  "typeLog": "webhook",
  "log": {"evento": "test", "datos": {"nombre": "ejemplo"}}
}';