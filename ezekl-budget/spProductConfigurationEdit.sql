CREATE OR ALTER PROCEDURE spProductConfigurationEdit
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  DECLARE @idProduct INT = JSON_VALUE(@json, '$.idProduct');
  DECLARE @idCompany INT = JSON_VALUE(@json, '$.idCompany');
  
  -- Validar que el producto existe y pertenece a la compañía
  IF NOT EXISTS (
    SELECT 1
    FROM tbCompanyProduct
    WHERE idProduct = @idProduct
    AND idCompany = @idCompany
  )
  BEGIN
    RAISERROR(N'Error: El producto no existe.', 16, 1);
    RETURN;
  END
  
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
BEGIN TRAN
-- Probar el procedimiento corregido
EXEC spProductConfigurationEdit @json = N'{
  "idCompany": 1
  , "idProduct": 34
  , "isMainCategory": false
  , "isCategory": false
  , "isProduct": false
  , "isIngredient": false
  , "isAdditional": false
  , "isCombo": false
  , "isUniqueSelection": false
}';
ROLLBACK TRAN