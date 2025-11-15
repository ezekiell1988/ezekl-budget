CREATE OR ALTER PROCEDURE spAccountingAccountGetOne
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;

  -- Extraer valores del JSON
  DECLARE @idAccountingAccount INT = JSON_VALUE(@json, '$.idAccountingAccount');
  DECLARE @includeHierarchy BIT = ISNULL(JSON_VALUE(@json, '$.includeHierarchy'), 0);
  DECLARE @includeParent BIT = ISNULL(JSON_VALUE(@json, '$.includeParent'), 0);
  
  --Queries
  SET @json = JSON_QUERY((
    SELECT AA.idAccountingAccount, AA.idAccountingAccountFather, AA.codeAccountingAccount
    , AA.nameAccountingAccount
    , IIF(@includeHierarchy = 1, JSON_QUERY(dbo.fnAccountingAccountGetHierarchy(AA.idAccountingAccount)), NULL) AS hierarchy
    , IIF(@includeParent = 1 AND AA.idAccountingAccountFather IS NOT NULL, 
        JSON_QUERY((
          SELECT P.idAccountingAccount, P.idAccountingAccountFather, P.codeAccountingAccount, P.nameAccountingAccount
          FROM tbAccountingAccount P 
          WHERE P.idAccountingAccount = AA.idAccountingAccountFather
          FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
        )), NULL) AS parent
    FROM tbAccountingAccount AA
    WHERE AA.idAccountingAccount = @idAccountingAccount
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));
  --Query Pagination
  SELECT JSON_QUERY(@json) json;
END
GO
-- Ejemplos de uso:
-- Obtener cuenta básica
EXEC spAccountingAccountGetOne @json = N'{"idAccountingAccount": 1}';

-- Obtener cuenta con jerarquía completa
EXEC spAccountingAccountGetOne @json = N'{"idAccountingAccount": 1, "includeHierarchy": true}';

-- Obtener cuenta con información del padre
EXEC spAccountingAccountGetOne @json = N'{"idAccountingAccount": 1, "includeParent": true}';

-- Obtener cuenta con jerarquía y padre
EXEC spAccountingAccountGetOne @json = N'{"idAccountingAccount": 1, "includeHierarchy": true, "includeParent": true}';