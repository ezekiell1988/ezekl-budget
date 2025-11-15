CREATE OR ALTER PROCEDURE spTypeAdd
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  DECLARE @idType INT;
  
  -- Crear tipo
  INSERT INTO tbType (nameType) VALUES (JSON_VALUE(@json, '$.nameType'));

  -- idType
  SET @idType = SCOPE_IDENTITY();

  -- Crear cuentas
  INSERT INTO tbTypeAccountingAccount (idType, idAccountingAccount, effect, [percent])
  SELECT @idType, idAccountingAccount, effect, [percent]
  FROM OPENJSON(@json, '$.accounts') WITH (
    idAccountingAccount INT
    , effect INT
    , [percent] DECIMAL(18,4)
  );

  -- Preparar query
  SET @json = JSON_QUERY((
    SELECT @idType idType
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));
  
  SELECT JSON_QUERY(@json) json;
END
GO

-- Probar el procedimiento corregido
EXEC spTypeAdd @json = N'{
  "nameType": "Factura de Gastos",
  "accounts": [
    {
      "idAccountingAccount": 5,
      "effect": 1,
      "percent": 100
    }
  ]
}';