CREATE OR ALTER PROCEDURE spProductDeliveryTypeEdit
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  DECLARE @idProduct INT = JSON_VALUE(@json, '$.idProduct');
  DECLARE @idCompany INT = JSON_VALUE(@json, '$.idCompany');
  DECLARE @deliveryType TABLE (
    idDeliveryType INT
    , active BIT
    , price DECIMAL(18, 4)
    , idProductDeliveryType INT
    , idProduct INT
    , rowNum INT
  );

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

  -- Cargar registros recibidos
  INSERT INTO @deliveryType
  SELECT *
  FROM OPENJSON(@json, '$.deliveryType') WITH (
    idDeliveryType INT
    , active BIT
    , price DECIMAL(18, 4)
    , idProductDeliveryType INT
    , idProduct INT
    , rowNum INT
  );
  
  -- Actualizar registros
  UPDATE PDT
  SET PDT.active = DT.active
  FROM tbProductDeliveryType PDT
  INNER JOIN @deliveryType DT
  ON DT.idProductDeliveryType = PDT.idProductDeliveryType;

  -- Actualizar registros
  UPDATE PDTP
  SET PDTP.price = DT.price
  FROM tbProductDeliveryTypePrice PDTP
  INNER JOIN @deliveryType DT
  ON DT.idProductDeliveryType = PDTP.idProductDeliveryType;

  -- Preparar query
  SET @json = JSON_QUERY((
    SELECT @idProduct idProduct
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));
  
  SELECT JSON_QUERY(@json) json;
END
GO
BEGIN TRAN
DECLARE @json NVARCHAR(MAX) = N'{
  "idCompany": 1
  , "idProduct": 34
  , "deliveryType": [
    {
      "idDeliveryType": 1
      , "active": true
      , "price": 13.1313
      , "idProductDeliveryType": 67
    },
    {
      "idDeliveryType": 2
      , "active": false
      , "price": 68.6868
      , "idProductDeliveryType": 68
    }
  ]
}';
-- Probar el procedimiento corregido
EXEC spProductDeliveryTypeEdit @json;
ROLLBACK TRAN