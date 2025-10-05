DROP PROCEDURE IF EXISTS spLoginAuth
GO
CREATE PROCEDURE spLoginAuth
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  
  -- Extraer valores del JSON
  DECLARE @codeLogin VARCHAR(10);
  DECLARE @token VARCHAR(5);
  
  SELECT @codeLogin = codeLogin, @token = token
  FROM OPENJSON(@json) WITH (
    codeLogin VARCHAR(10)
    , token VARCHAR(5)
  );
  
  DECLARE @user NVARCHAR(MAX) = JSON_QUERY((
    SELECT L.idLogin, L.codeLogin, L.nameLogin
    , L.phoneLogin, L.emailLogin
    FROM tbLogin L WITH (NOLOCK)
    INNER JOIN tbLoginToken LT WITH (NOLOCK)
    ON LT.idLogin = L.idLogin
    WHERE L.codeLogin = @codeLogin
    AND LT.token = @token
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));
  
  -- Si la autenticación es exitosa, eliminar el token usado
  IF @user IS NOT NULL
  BEGIN
    DELETE LT
    FROM tbLoginToken LT
    INNER JOIN tbLogin L ON L.idLogin = LT.idLogin
    WHERE L.codeLogin = @codeLogin
    AND LT.token = @token;
  END
  
  SET @json = JSON_QUERY((
    SELECT CAST(IIF(@user IS NULL, 0, 1) AS BIT) success
    , JSON_QUERY(@user) auth
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));
  --Query Pagination
  SELECT JSON_QUERY(@json) json;
END
GO
EXEC spLoginAuth @json = N'{"codeLogin":"S","token": "12345"}';