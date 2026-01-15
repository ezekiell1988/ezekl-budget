CREATE OR ALTER PROCEDURE spProductGetOne
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

  -- Preparar query
  SET @json = JSON_QUERY((
    SELECT CT.nameProduct nameProductFather, P.idProductFather
    , P.idProduct, P.nameProduct, P.descriptionProduct
    , JSON_QUERY((
      SELECT PAA.idProductAccountingAccount
      , AA.nameAccountingAccount
      , PAA.effect, PAA.[percent]
      FROM tbProductAccountingAccount PAA
      INNER JOIN tbAccountingAccount AA
      ON AA.idAccountingAccount = PAA.idAccountingAccount
      WHERE PAA.idProduct = P.idProduct
      FOR JSON PATH
    )) accountingAccount
    , JSON_QUERY((
      SELECT PDTP.idProductDeliveryTypePrice
      , DT.nameDeliveryType, PDTP.price
      FROM tbProductDeliveryTypePrice PDTP
      INNER JOIN tbProductDeliveryType PDT
      ON PDT.idProductDeliveryType = PDTP.idProductDeliveryType
      INNER JOIN tbDeliveryType DT
      ON DT.idDeliveryType = PDT.idDeliveryType
      WHERE PDT.idProduct = P.idProduct
      FOR JSON PATH
    )) deliveryPrice
    , JSON_QUERY((
      SELECT PR.idProductRequired
      , ISNULL(PR.nameProductRequired, PRCT.nameProduct) nameProductRequired
      , JSON_QUERY((
        SELECT PRI.idProduct, PRIP.nameProduct
        FROM tbProductRequiredIncluded PRI
        INNER JOIN tbProduct PRIP
        ON PRIP.idProduct = PRI.idProduct
        WHERE PRI.idProductRequired = PR.idProductRequired
        FOR JSON PATH
      )) selected
      FROM tbProductRequired PR
      INNER JOIN tbProduct PRCT
      ON PRCT.idProduct = PR.idProductRelated
      WHERE PR.idProduct = P.idProduct
      FOR JSON PATH
    )) required
    FROM tbProduct P
    LEFT JOIN tbProduct CT
    ON CT.idProduct = P.idProductFather
    WHERE P.idProduct = @idProduct
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER, INCLUDE_NULL_VALUES
  ));
  
  SELECT JSON_QUERY(@json) json;
END
GO

-- Probar el procedimiento corregido
EXEC spProductGetOne @json = N'{
  "idCompany": 1
  , "idProduct": 32
}';