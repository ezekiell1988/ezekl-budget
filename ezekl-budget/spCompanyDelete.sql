CREATE OR ALTER PROCEDURE spCompanyDelete
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  DECLARE @idCompany INT = JSON_VALUE(@json, '$.idCompany');

  IF @idCompany IS NULL
  BEGIN
    RAISERROR(N'El parámetro idCompany es requerido y no puede ser NULL.', 16, 1);
    RETURN;
  END
  
  -- Soft delete: marcar compañía como inactiva
  UPDATE tbCompany 
  SET active = 0 
  WHERE idCompany = @idCompany 
    AND active = 1; -- Solo si está activa

  -- Verificar si se actualizó algún registro
  IF @@ROWCOUNT = 0
  BEGIN
    -- Verificar si la compañía existe pero ya está inactiva
    IF EXISTS (SELECT 1 FROM tbCompany WHERE idCompany = @idCompany AND active = 0)
      RAISERROR(N'La compañía con ID %d ya está eliminada (inactiva).', 16, 1, @idCompany);
    ELSE
      RAISERROR(N'No se encontró la compañía con ID %d.', 16, 1, @idCompany);
    RETURN;
  END

  -- Operación exitosa (sin retorno de datos necesario)
END
GO

-- Probar el procedimiento corregido
EXEC spCompanyDelete @json = N'{
  "idCompany": 1
}';