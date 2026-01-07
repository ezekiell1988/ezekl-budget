CREATE OR ALTER PROCEDURE spProductGet
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  DECLARE @idCompany INT = JSON_VALUE(@json, '$.idCompany');

  -- Preparar query
  SET @json = JSON_QUERY((
    SELECT P.idProduct, P.nameProduct, P.descriptionProduct
    , JSON_QUERY(dbo.fnProductGetByIdProductFather((
      SELECT P.idProduct idProductFather, CP.idCompany
      FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
    ))) childrens
    FROM tbCompanyProduct CP
    INNER JOIN tbProduct P
    ON P.idProduct = CP.idProduct
    WHERE CP.idCompany = @idCompany
    AND P.idProductFather IS NULL
    FOR JSON PATH, INCLUDE_NULL_VALUES
  ));
  
  SELECT JSON_QUERY(@json) json;
END
GO

-- Probar el procedimiento corregido
EXEC spProductGet @json = N'{
  "idCompany": 1
}';