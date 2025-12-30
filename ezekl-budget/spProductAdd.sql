CREATE OR ALTER PROCEDURE spProductAdd
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  DECLARE @idProduct INT;
  
  -- Crear producto
  INSERT INTO tbProduct (nameProduct, descriptionProduct, idProductFather)
  SELECT *
  FROM OPENJSON(@json) WITH (
    nameProduct NVARCHAR(100)
    , descriptionProduct NVARCHAR(500)
    , idProductFather INT
  );

  -- idProduct
  SET @idProduct = SCOPE_IDENTITY();

  -- Crear cuentas
  INSERT INTO tbProductAccountingAccount (idProduct, idAccountingAccount, effect, [percent])
  SELECT @idProduct, idAccountingAccount, effect, [percent]
  FROM OPENJSON(@json, '$.accounts') WITH (
    idAccountingAccount INT
    , effect INT
    , [percent] DECIMAL(18,4)
  );

  -- Preparar query
  SET @json = JSON_QUERY((
    SELECT @idProduct idProduct
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));
  
  SELECT JSON_QUERY(@json) json;
END
GO
-- 23 Promociones
-- 25 Tamaño TV
-- Probar el procedimiento corregido
EXEC spProductAdd @json = N'{
  "nameProduct": "TV nueva 60\"",
  "idProductFather": 24,
  "descriptionProduct": "TV nueva 60 pulgadas"
}';

-- EXEC spTruncateTable @table = 'dbo.tbProductDeliveryTypePrice';
-- EXEC spTruncateTable @table = 'dbo.tbProductDeliveryType';
-- EXEC spTruncateTable @table = 'dbo.tbProductAccountingAccount';
-- EXEC spTruncateTable @table = 'dbo.tbProduct';