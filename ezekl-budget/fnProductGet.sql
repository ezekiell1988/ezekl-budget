CREATE OR ALTER FUNCTION fnProductGet (
  @json NVARCHAR(MAX)
)
RETURNS NVARCHAR(MAX)
AS
BEGIN

  -- Preparar query
  SET @json = JSON_QUERY((
    SELECT idProduct, nameProduct, descriptionProduct
    , JSON_QUERY(dbo.fnProductGet((
      SELECT P.idProduct idProductFather
      FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
    ))) childrens
    FROM tbProduct P
    INNER JOIN OPENJSON(@json) WITH (
      idProductFather INT
    ) J
    ON J.idProductFather = P.idProductFather
    FOR JSON PATH, INCLUDE_NULL_VALUES
  ));
  
  RETURN JSON_QUERY(@json);
END
GO

-- Probar el procedimiento corregido
SELECT dbo.fnProductGet(N'{
  "idProductFather": 1
}');