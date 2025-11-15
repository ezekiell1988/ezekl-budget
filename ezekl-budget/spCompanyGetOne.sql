CREATE OR ALTER PROCEDURE spCompanyGetOne
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;

  -- Extraer valores del JSON
  DECLARE @idCompany INT = JSON_VALUE(@json, '$.idCompany');
  
  -- Query principal
  SET @json = JSON_QUERY((
    SELECT 
      C.idCompany,
      C.codeCompany,
      C.nameCompany,
      C.descriptionCompany,
      C.active
    FROM tbCompany C
    WHERE C.idCompany = @idCompany
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));
  
  -- Retornar resultado
  SELECT JSON_QUERY(@json) json;
END
GO

-- Ejemplo de uso:
EXEC spCompanyGetOne @json = N'{
  "idCompany": 1
}';