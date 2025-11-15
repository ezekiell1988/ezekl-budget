CREATE OR ALTER PROCEDURE spAccountingAccountGet
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
  SET @sort = 'nameAccountingAccount_asc';
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
  ; WITH AccountingAccountQuery AS (
    SELECT
      ROW_NUMBER() OVER (
        ORDER BY
          IIF(@sort = 'idAccountingAccount_asc', AA.idAccountingAccount, NULL),
          IIF(@sort = 'idAccountingAccountFather_asc', AA.idAccountingAccountFather, NULL),
          IIF(@sort = 'idAccountingAccountFather_desc', AA.idAccountingAccountFather, NULL) DESC,
          IIF(@sort = 'codeAccountingAccount_asc', AA.codeAccountingAccount, NULL),
          IIF(@sort = 'codeAccountingAccount_desc', AA.codeAccountingAccount, NULL) DESC,
          IIF(@sort = 'nameAccountingAccount_asc', AA.nameAccountingAccount, NULL),
          IIF(@sort = 'nameAccountingAccount_desc', AA.nameAccountingAccount, NULL) DESC,
          AA.idAccountingAccount DESC
      ) RowNum,
      AA.idAccountingAccount,
      AA.idAccountingAccountFather,
      AA.codeAccountingAccount,
      AA.nameAccountingAccount,
      AA.active
    FROM tbAccountingAccount AA
    WHERE AA.idAccountingAccountFather IS NULL
      AND (@includeInactive = 1 OR AA.active = 1)
      AND (
        -- Si no hay filtro específico, incluir todos los nodos raíz
        (@search = '%%')
        OR
        -- Si el nodo raíz cumple el filtro, incluirlo
        (AA.nameAccountingAccount LIKE @search OR AA.codeAccountingAccount LIKE @search)
        OR
        -- Si tiene descendientes que cumplen el filtro, incluir el nodo raíz
        dbo.fnHasMatchingChildren(AA.idAccountingAccount, @search, @includeInactive) = 1
      )
  )
  SELECT @json = JSON_QUERY((
    SELECT
      (SELECT COUNT(*) FROM AccountingAccountQuery) total,
      JSON_QUERY(ISNULL((
        SELECT
          CQ.idAccountingAccount,
          CQ.idAccountingAccountFather,
          CQ.codeAccountingAccount,
          CQ.nameAccountingAccount,
          CQ.active
          , JSON_QUERY(dbo.fnAccountingAccountGet((
            SELECT 
              CQ.idAccountingAccount idAccountingAccountFather,
              REPLACE(REPLACE(@search, '%', ''), '', NULL) search,
              @includeInactive includeInactive
            FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
          ))) children
        FROM AccountingAccountQuery CQ
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

-- Obtener estructura jerárquica completa (comportamiento por defecto con JSON vacío)
-- EXEC spAccountingAccountGet @json = N'{}';
EXEC spAccountingAccountGet @json = N'{"sort":"nameAccountingAccount_asc", "page": 1, "itemPerPage": 20, "includeInactive": true}';