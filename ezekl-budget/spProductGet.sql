CREATE OR ALTER PROCEDURE spProductGet
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;

  -- Preparar query
  SET @json = JSON_QUERY((
    SELECT idProduct, nameProduct, descriptionProduct
    , JSON_QUERY(dbo.fnProductGet((
      SELECT P.idProduct idProductFather
      FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
    ))) childrens
    FROM tbProduct P
    WHERE P.idProductFather IS NULL
    FOR JSON PATH, INCLUDE_NULL_VALUES
  ));
  
  SELECT JSON_QUERY(@json) json;
END
GO

-- Probar el procedimiento corregido
EXEC spProductGet @json = N'{
  "idCompany": 1
}';