CREATE OR ALTER PROCEDURE spAccountingAccountDelete
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  DECLARE @idAccountingAccount INT = JSON_VALUE(@json, '$.idAccountingAccount');

  IF @idAccountingAccount IS NULL
  BEGIN
    RAISERROR(N'El parámetro idAccountingAccount es requerido y no puede ser NULL.', 16, 1);
    RETURN;
  END

  -- Verificar si la cuenta tiene cuentas hijas
  IF EXISTS (SELECT 1 FROM tbAccountingAccount WHERE idAccountingAccountFather = @idAccountingAccount)
  BEGIN
    RAISERROR(N'No se puede eliminar la cuenta contable con ID %d porque tiene cuentas dependientes.', 16, 1, @idAccountingAccount);
    RETURN;
  END
  
  -- Eliminar cuenta contable
  DELETE FROM tbAccountingAccount 
  WHERE idAccountingAccount = @idAccountingAccount;

  -- Verificar si se eliminó algún registro
  IF @@ROWCOUNT = 0
  BEGIN
    RAISERROR(N'No se encontró la cuenta contable con ID %d.', 16, 1, @idAccountingAccount);
    RETURN;
  END

  -- Operación exitosa (sin retorno de datos necesario)
END
GO

-- Ejemplo de uso:
-- EXEC spAccountingAccountDelete @json = N'{
--   "idAccountingAccount": 1
-- }';
