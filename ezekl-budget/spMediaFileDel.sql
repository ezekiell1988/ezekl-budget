CREATE OR ALTER PROCEDURE spMediaFileDel
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  DECLARE @idMediaFile INT = JSON_VALUE(@json, '$.idMediaFile');
  DECLARE @idCompany INT = JSON_VALUE(@json, '$.idCompany');
  DECLARE @pathMediaFile NVARCHAR(500);

  -- Validar que el archivo existe y pertenece a la compañía
  IF NOT EXISTS (
    SELECT 1
    FROM tbCompanyMediaFile
    WHERE idMediaFile = @idMediaFile
    AND idCompany = @idCompany
  )
  BEGIN
    RAISERROR(N'Error: El archivo no existe.', 16, 1);
    RETURN;
  END

  -- Obtener pathMediaFile antes de eliminar
  SELECT @pathMediaFile = pathMediaFile
  FROM tbMediaFile
  WHERE idMediaFile = @idMediaFile;

  -- Eliminar el archivo de la BD (cascada elimina relaciones)
  DELETE FROM tbMediaFile
  WHERE idMediaFile = @idMediaFile;

  -- Preparar respuesta con path para eliminar del servidor
  SET @json = JSON_QUERY((
    SELECT @idMediaFile idMediaFile
    , @pathMediaFile pathMediaFile
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));
  
  SELECT JSON_QUERY(@json) json;
END
GO
EXEC spMediaFileDel @json = N'{
  "idCompany": 1
  , "idMediaFile": 1
}';
