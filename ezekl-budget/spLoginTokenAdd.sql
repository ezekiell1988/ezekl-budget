DROP PROCEDURE IF EXISTS spLoginTokenAdd
GO
CREATE PROCEDURE spLoginTokenAdd
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  DECLARE @user NVARCHAR(MAX) = JSON_QUERY((
    SELECT L.idLogin, L.codeLogin, L.nameLogin
    , L.phoneLogin, L.emailLogin
    FROM OPENJSON(@json) WITH (
      codeLogin VARCHAR(10)
    ) J
    INNER JOIN tbLogin L WITH (NOLOCK)
    ON L.codeLogin = J.codeLogin
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));
  
  -- Validar que el usuario existe
  IF @user IS NULL
  BEGIN
    THROW 50001, N'Usuario no encontrado con el código proporcionado', 1;
  END
  
  DECLARE @token VARCHAR(5) = RIGHT('00000' + CAST(ABS(CHECKSUM(NEWID())) % 100000 AS VARCHAR(5)), 5);
  INSERT INTO tbLoginToken (idLogin, token) VALUES (
    JSON_VALUE(@user, '$.idLogin'), @token
  );
  SET @json = JSON_QUERY((
    SELECT SCOPE_IDENTITY() idLoginToken
    , @token token, JSON_QUERY(@user) auth
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));
  --Query Pagination
  SELECT JSON_QUERY(@json) json;
END
GO
BEGIN TRAN
EXEC spLoginTokenAdd @json = N'{"codeLogin":"S"}';
ROLLBACK TRAN