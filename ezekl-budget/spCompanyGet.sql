CREATE OR ALTER PROCEDURE spCompanyGet
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  
  -- Extraer valores del JSON (manejo de JSON vacío)
  DECLARE @search NVARCHAR(50);
  DECLARE @sort NVARCHAR(50);
  DECLARE @page INT;
  DECLARE @itemPerPage INT;
  DECLARE @includeInactive BIT;
  
  -- Inicializar con valores por defecto
  SET @search = '%';
  SET @sort = 'nameCompany_asc';
  SET @page = 1;
  SET @itemPerPage = 10;
  SET @includeInactive = 0;
  
  -- Sobrescribir con valores del JSON si existen
  IF @json != '{}' AND @json IS NOT NULL AND LEN(@json) > 2
  BEGIN
    SELECT 
      @search = '%' + ISNULL(search, '') + '%',
      @sort = ISNULL(sort, @sort),
      @page = ISNULL(page, @page),
      @itemPerPage = ISNULL(itemPerPage, @itemPerPage),
      @includeInactive = ISNULL(includeInactive, @includeInactive)
    FROM OPENJSON(@json) WITH (
      search NVARCHAR(50),
      sort NVARCHAR(50),
      page INT,
      itemPerPage INT,
      includeInactive BIT
    );
  END

  -- Query principal con CTE para paginación
  ; WITH CompanyQuery AS (
    SELECT 
      ROW_NUMBER() OVER (
        ORDER BY 
          IIF(@sort = 'idCompany_asc', C.idCompany, NULL),
          IIF(@sort = 'codeCompany_asc', C.codeCompany, NULL),
          IIF(@sort = 'codeCompany_desc', C.codeCompany, NULL) DESC,
          IIF(@sort = 'nameCompany_asc', C.nameCompany, NULL),
          IIF(@sort = 'nameCompany_desc', C.nameCompany, NULL) DESC,
          C.idCompany DESC
      ) RowNum,
      C.idCompany,
      C.codeCompany,
      C.nameCompany,
      C.descriptionCompany,
      C.active
    FROM tbCompany C
    WHERE (C.nameCompany LIKE @search OR C.codeCompany LIKE @search)
      AND (@includeInactive = 1 OR C.active = 1)
  )
  SELECT @json = JSON_QUERY((
    SELECT 
      (SELECT COUNT(*) FROM CompanyQuery) total,
      JSON_QUERY(ISNULL((
        SELECT 
          CQ.idCompany,
          CQ.codeCompany,
          CQ.nameCompany,
          CQ.descriptionCompany,
          CQ.active
        FROM CompanyQuery CQ
        WHERE CQ.RowNum BETWEEN (@page - 1) * @itemPerPage + 1 AND @page * @itemPerPage
        FOR JSON PATH
      ), '[]')) data
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));
  
  -- Retornar resultado
  SELECT JSON_QUERY(@json) json;
END
GO

-- Ejemplos de uso:

-- Obtener todas las compañías (JSON vacío)
EXEC spCompanyGet @json = N'{}';
/*
-- Buscar compañías específicas
EXEC spCompanyGet @json = N'{
  "search": "3101000",
  "sort": "nameCompany_asc",
  "page": 1,
  "itemPerPage": 10,
  "includeInactive": false
}';

-- Obtener todas con paginación específica
EXEC spCompanyGet @json = N'{
  "page": 2,
  "itemPerPage": 5
}';
*/