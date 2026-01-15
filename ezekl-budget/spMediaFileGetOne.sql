CREATE OR ALTER PROCEDURE spMediaFileGetOne
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  DECLARE @idMediaFile INT = JSON_VALUE(@json, '$.idMediaFile');
  DECLARE @idCompany INT = JSON_VALUE(@json, '$.idCompany');

  -- Validar que el producto existe y pertenece a la compañía
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

  -- Preparar query
  SET @json = JSON_QUERY((
    SELECT MF.idMediaFile, MF.nameMediaFile, MF.pathMediaFile
    , MF.sizeMediaFile, MF.mimetype, MF.mediaType, MF.createAt
    FROM tbMediaFile MF
    WHERE MF.idMediaFile = @idMediaFile
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER, INCLUDE_NULL_VALUES
  ));
  
  SELECT JSON_QUERY(@json) json;
END
GO

-- Probar el procedimiento corregido
EXEC spMediaFileGetOne @json = N'{
  "idCompany": 1
  , "idMediaFile": 1
}';