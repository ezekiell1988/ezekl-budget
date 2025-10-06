DROP PROCEDURE IF EXISTS spAccountingAccountGet
GO
CREATE PROCEDURE spAccountingAccountGet
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  
  -- Extraer valores del JSON
  DECLARE @noQuery BIT;
  DECLARE @sort NVARCHAR(50);
  DECLARE @page INT;
  DECLARE @itemPerPage INT;
  DECLARE @search NVARCHAR(50);
  
  SELECT @noQuery = ISNULL(noQuery, 0)
  , @sort = ISNULL(sort, 'codeAccountingAccount_asc')
  , @page = ISNULL(page, 1)
  , @itemPerPage = ISNULL(itemPerPage, 10)
  , @search = '%' + ISNULL(search, '%') + '%'
  FROM OPENJSON(@json) WITH (
    noQuery BIT
    , sort NVARCHAR(50)
    , page INT
    , itemPerPage INT
    , search NVARCHAR(50)
  );

  --Queries
  ; WITH Query AS (
    SELECT ROW_NUMBER() OVER (ORDER BY IIF(@sort = 'idAccountingAccount_asc', AA.idAccountingAccount, NULL)
      , IIF(@sort = 'codeAccountingAccount_asc', AA.codeAccountingAccount, NULL)
      , IIF(@sort = 'codeAccountingAccount_desc', AA.codeAccountingAccount, NULL) DESC
      , IIF(@sort = 'nameAccountingAccount_asc', AA.codeAccountingAccount, NULL)
      , IIF(@sort = 'nameAccountingAccount_desc', AA.codeAccountingAccount, NULL) DESC
      , AA.idAccountingAccount DESC
    ) RowNum, AA.idAccountingAccount, AA.codeAccountingAccount
    , AA.nameAccountingAccount
    FROM tbAccountingAccount AA
    WHERE AA.nameAccountingAccount LIKE @search
  )
  SELECT @json = JSON_QUERY((
    SELECT (SELECT COUNT(*) FROM Query) total
    , JSON_QUERY((
      SELECT Q.idAccountingAccount, Q.codeAccountingAccount
      , Q.nameAccountingAccount
      FROM Query Q
      WHERE Q.RowNum BETWEEN (@page - 1) * @itemPerPage + 1 AND @page * @itemPerPage
      FOR JSON PATH
    )) data
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));
  --Query Pagination
  SELECT JSON_QUERY(@json) json;
END
GO
EXEC spAccountingAccountGet @json = N'{"sort":"nameAccountingAccount_asc", "itemPerPage": 2}';