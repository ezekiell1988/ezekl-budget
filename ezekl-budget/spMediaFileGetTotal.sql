CREATE OR ALTER PROCEDURE spMediaFileGetTotal
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  DECLARE @idCompany INT = JSON_VALUE(@json, '$.idCompany');

  -- Agrupar por tipo de medio y por año
  ;WITH MediaTypeTotals AS (
    SELECT 
      MF.mediaType,
      COUNT(MF.idMediaFile) quantity,
      ISNULL(SUM(MF.sizeMediaFile), 0) totalSize
    FROM tbCompanyMediaFile CMF
    INNER JOIN tbMediaFile MF ON MF.idMediaFile = CMF.idMediaFile
    WHERE CMF.idCompany = @idCompany
    GROUP BY MF.mediaType
  ),
  YearTotals AS (
    SELECT 
      YEAR(MF.createAt) year,
      COUNT(MF.idMediaFile) quantity,
      ISNULL(SUM(MF.sizeMediaFile), 0) totalSize
    FROM tbCompanyMediaFile CMF
    INNER JOIN tbMediaFile MF ON MF.idMediaFile = CMF.idMediaFile
    WHERE CMF.idCompany = @idCompany
    GROUP BY YEAR(MF.createAt)
  )
  -- Preparar query con totales generales, por tipo y por año
  SELECT @json = JSON_QUERY((
    SELECT 
      (SELECT ISNULL(SUM(quantity), 0) FROM MediaTypeTotals) quantity,
      (SELECT ISNULL(SUM(totalSize), 0) FROM MediaTypeTotals) totalSize,
      JSON_QUERY((
        SELECT mediaType, quantity, totalSize
        FROM MediaTypeTotals
        FOR JSON PATH
      )) mediaType,
      JSON_QUERY((
        SELECT year, quantity, totalSize
        FROM YearTotals
        ORDER BY year DESC
        FOR JSON PATH
      )) byYear
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER, INCLUDE_NULL_VALUES
  ));
  
  SELECT JSON_QUERY(@json) json;
END
GO

-- Probar el procedimiento corregido
EXEC spMediaFileGetTotal @json = N'{
  "idCompany": 1
}';