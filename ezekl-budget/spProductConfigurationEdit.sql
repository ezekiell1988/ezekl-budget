CREATE OR ALTER PROCEDURE spProductConfigurationEdit
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  DECLARE @idProduct INT = JSON_VALUE(@json, '$.idProduct');
  
  -- Crear producto
  UPDATE PC
  SET PC.isMainCategory = J.isMainCategory
  , PC.isCategory = J.isCategory
  , PC.isProduct = J.isProduct
  , PC.isIngredient = J.isIngredient
  , PC.isAdditional = J.isAdditional
  , PC.isCombo = J.isCombo
  , PC.isUniqueSelection = J.isUniqueSelection
  FROM tbProductConfiguration PC
  INNER JOIN OPENJSON(@json) WITH (
    idProduct INT
    , isMainCategory BIT
    , isCategory BIT
    , isProduct BIT
    , isIngredient BIT
    , isAdditional BIT
    , isCombo BIT
    , isUniqueSelection BIT
  ) J
  ON J.idProduct = PC.idProduct;

  -- Preparar query
  SET @json = JSON_QUERY((
    SELECT @idProduct idProduct
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));
  
  SELECT JSON_QUERY(@json) json;
END
GO

-- Probar el procedimiento corregido
EXEC spProductConfigurationEdit @json = N'{
  "idProduct": 1
  , "isMainCategory": false
  , "isCategory": false
  , "isProduct": false
  , "isIngredient": false
  , "isAdditional": false
  , "isCombo": false
  , "isUniqueSelection": false
}';

-- EXEC spTruncateTable @table = 'dbo.tbProductConfiguration';
-- EXEC spTruncateTable @table = 'dbo.tbProduct';