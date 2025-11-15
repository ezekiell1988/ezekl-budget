CREATE OR ALTER PROCEDURE spCompanyAdd
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  DECLARE @idCompany INT;
  
  -- Crear compañía
  INSERT INTO tbCompany (codeCompany, nameCompany, descriptionCompany, active)
  SELECT codeCompany, nameCompany, descriptionCompany, 1 -- Por defecto activa
  FROM OPENJSON(@json) WITH (
    codeCompany VARCHAR(20),
    nameCompany NVARCHAR(100),
    descriptionCompany NVARCHAR(500)
  );

  -- idCompany
  SET @idCompany = SCOPE_IDENTITY();

  -- Preparar query
  SET @json = JSON_QUERY((
    SELECT @idCompany idCompany
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));
  
  SELECT JSON_QUERY(@json) json;
END
GO

-- Probar el procedimiento corregido
EXEC spCompanyAdd @json = N'{
  "codeCompany": "3-101-123456",
  "nameCompany": "IT Quest Solutions",
  "descriptionCompany": "Empresa de desarrollo de software"
}';