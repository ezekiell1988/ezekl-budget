CREATE OR ALTER PROCEDURE spAccountingAccountEdit
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  
  -- Actualizar cuenta contable
  UPDATE AA
  SET AA.idAccountingAccountFather = ISNULL(J.idAccountingAccountFather, AA.idAccountingAccountFather)
  , AA.codeAccountingAccount = ISNULL(J.codeAccountingAccount, AA.codeAccountingAccount)
  , AA.nameAccountingAccount = ISNULL(J.nameAccountingAccount, AA.nameAccountingAccount)
  FROM tbAccountingAccount AA
  INNER JOIN OPENJSON(@json) WITH (
    idAccountingAccount INT,
    idAccountingAccountFather INT,
    codeAccountingAccount VARCHAR(20),
    nameAccountingAccount NVARCHAR(100)
  ) J
  ON J.idAccountingAccount = AA.idAccountingAccount
  WHERE J.idAccountingAccount IS NOT NULL; -- Validación integrada

  -- Verificar si se actualizó algún registro
  IF @@ROWCOUNT = 0
  BEGIN
    DECLARE @idAccountingAccount INT = JSON_VALUE(@json, '$.idAccountingAccount');
    IF @idAccountingAccount IS NULL
      RAISERROR(N'El parámetro idAccountingAccount es requerido y no puede ser NULL.', 16, 1);
    ELSE
      RAISERROR(N'No se encontró la cuenta contable con ID %d.', 16, 1, @idAccountingAccount);
    RETURN;
  END

  -- Operación exitosa (sin retorno de datos necesario)
END
GO

-- Ejemplo de uso:
-- EXEC spAccountingAccountEdit @json = N'{
--   "idAccountingAccount": 1,
--   "idAccountingAccountFather": 2,
--   "codeAccountingAccount": "1.1.001",
--   "nameAccountingAccount": "Caja General Actualizada"
-- }';
