DROP PROCEDURE IF EXISTS spLoginAuth GO CREATE PROCEDURE spLoginAuth
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  DECLARE @user NVARCHAR(MAX) = JSON_QUERY((
    SELECT L.idLogin, L.codeLogin, L.nameLogin
    , L.phoneLogin, L.emailLogin
    FROM OPENJSON(@json) WITH (
      codeLogin VARCHAR(10)
      , token VARCHAR(5)
    ) J
    INNER JOIN tbLogin L WITH (NOLOCK)
    ON L.codeLogin = J.codeLogin
    INNER JOIN tbLoginToken LT WITH (NOLOCK)
    ON LT.idLogin = L.idLogin
    AND LT.token = J.token
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));
  SET @json = JSON_QUERY((
    SELECT CAST(IIF(@user IS NULL, 0, 1) AS BIT) ok
    , JSON_QUERY(@user) auth
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));
  --Query Pagination
  SELECT JSON_QUERY(@json) json;
END
GO
EXEC spLoginAuth @json = N'{"codeLogin":"S","token": "12345"}';