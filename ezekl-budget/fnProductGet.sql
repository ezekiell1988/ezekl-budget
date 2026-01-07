CREATE OR ALTER FUNCTION fnProductGetByIdProductFather (
  @json NVARCHAR(MAX)
)
RETURNS NVARCHAR(MAX)
AS
BEGIN
  DECLARE @idCompany INT = JSON_VALUE(@json, '$.idCompany');
  DECLARE @idProductFather INT = JSON_VALUE(@json, '$.idProductFather');

  -- Preparar query
  SET @json = JSON_QUERY((
    SELECT P.idProduct, P.nameProduct, P.descriptionProduct
    , JSON_QUERY(dbo.fnProductGetByIdProductFather((
      SELECT P.idProduct idProductFather
      FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
    ))) childrens
    FROM tbCompanyProduct CP
    INNER JOIN tbProduct P
    ON P.idProduct = CP.idProduct
    WHERE CP.idCompany = @idCompany
    AND P.idProductFather = @idProductFather
    FOR JSON PATH, INCLUDE_NULL_VALUES
  ));
  
  RETURN JSON_QUERY(@json);
END
GO

-- Probar el procedimiento corregido
SELECT dbo.fnProductGetByIdProductFather(N'{
  "idCompany": 1,
  "idProductFather": 1
}');