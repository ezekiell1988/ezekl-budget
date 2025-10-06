DROP PROCEDURE IF EXISTS spAccountingAccountGetOne
GO
CREATE PROCEDURE spAccountingAccountGetOne
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;

  -- Extraer valores del JSON
  DECLARE @idAccountingAccount INT = JSON_VALUE(@json, '$.idAccountingAccount');
  --Queries
  SET @json = JSON_QUERY((
    SELECT AA.idAccountingAccount, AA.codeAccountingAccount
    , AA.nameAccountingAccount
    FROM tbAccountingAccount AA
    WHERE AA.idAccountingAccount = @idAccountingAccount
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));
  --Query Pagination
  SELECT JSON_QUERY(@json) json;
END
GO
EXEC spAccountingAccountGetOne @json = N'{"idAccountingAccount": 1}';