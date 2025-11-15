CREATE OR ALTER PROCEDURE spCompanyEdit
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  
  -- Actualizar compañía
  UPDATE C
  SET C.codeCompany = ISNULL(J.codeCompany, C.codeCompany)
  , C.nameCompany = ISNULL(J.nameCompany, C.nameCompany)
  , C.descriptionCompany = ISNULL(J.descriptionCompany, C.descriptionCompany)
  FROM tbCompany C
  INNER JOIN OPENJSON(@json) WITH (
    idCompany INT,
    codeCompany VARCHAR(20),
    nameCompany NVARCHAR(100),
    descriptionCompany NVARCHAR(500)
  ) J
  ON J.idCompany = C.idCompany
  WHERE J.idCompany IS NOT NULL; -- Validación integrada

  -- Verificar si se actualizó algún registro
  IF @@ROWCOUNT = 0
  BEGIN
    DECLARE @idCompany INT = JSON_VALUE(@json, '$.idCompany');
    IF @idCompany IS NULL
      RAISERROR(N'El parámetro idCompany es requerido y no puede ser NULL.', 16, 1);
    ELSE
      RAISERROR(N'No se encontró la compañía con ID %d.', 16, 1, @idCompany);
    RETURN;
  END

  -- Operación exitosa (sin retorno de datos necesario)
END
GO

-- Probar el procedimiento corregido
EXEC spCompanyEdit @json = N'{
  "idCompany": 1,
  "codeCompany": "3-101-123456",
  "nameCompany": "IT Quest Solutions S.A.",
  "descriptionCompany": "Empresa de desarrollo de software y consultoría"
}';