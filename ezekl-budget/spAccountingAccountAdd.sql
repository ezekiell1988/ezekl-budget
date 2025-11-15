CREATE OR ALTER PROCEDURE spAccountingAccountAdd
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  DECLARE @idAccountingAccount INT;
  
  -- Crear cuenta contable
  INSERT INTO tbAccountingAccount (idAccountingAccountFather, codeAccountingAccount, nameAccountingAccount)
  SELECT idAccountingAccountFather, codeAccountingAccount, nameAccountingAccount
  FROM OPENJSON(@json) WITH (
    idAccountingAccountFather INT,
    codeAccountingAccount VARCHAR(20),
    nameAccountingAccount NVARCHAR(100)
  );

  -- idAccountingAccount
  SET @idAccountingAccount = SCOPE_IDENTITY();

  -- Preparar query
  SET @json = JSON_QUERY((
    SELECT @idAccountingAccount idAccountingAccount
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));
  
  SELECT JSON_QUERY(@json) json;
END
GO

-- Ejemplo de uso:
EXEC spAccountingAccountAdd @json = N'{
  "idAccountingAccountFather": 10,
  "codeAccountingAccount": "001-001-001-001",
  "nameAccountingAccount": "Caja General 3"
}';
