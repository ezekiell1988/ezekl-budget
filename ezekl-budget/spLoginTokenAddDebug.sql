DROP PROCEDURE IF EXISTS spLoginTokenAdd
GO
CREATE PROCEDURE spLoginTokenAdd
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  
  -- Variables de debug
  DECLARE @debug_info NVARCHAR(MAX);
  DECLARE @user_count INT;
  DECLARE @input_codeLogin VARCHAR(10);
  
  -- Extraer codeLogin del JSON de entrada
  SELECT @input_codeLogin = codeLogin
  FROM OPENJSON(@json) WITH (
    codeLogin VARCHAR(10)
  );
  
  -- Contar cuántos usuarios existen con ese código
  SELECT @user_count = COUNT(*)
  FROM tbLogin 
  WHERE codeLogin = @input_codeLogin;
  
  -- Crear información de debug
  SET @debug_info = JSON_QUERY((
    SELECT @input_codeLogin as input_code, @user_count as user_count,
           'Looking for user with codeLogin = ' + ISNULL(@input_codeLogin, 'NULL') as debug_message
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));
  
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
  
  -- Si no encuentra el usuario, devolver debug info
  IF @user IS NULL
  BEGIN
    SET @json = JSON_QUERY((
      SELECT 0 as success, 'Usuario no encontrado con el código proporcionado' as message,
             JSON_QUERY(@debug_info) as debug_info
      FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
    ));
    SELECT JSON_QUERY(@json) json;
    RETURN;
  END
  
  -- Si encuentra el usuario, proceder normalmente
  DECLARE @token VARCHAR(5) = RIGHT('00000' + CAST(ABS(CHECKSUM(NEWID())) % 100000 AS VARCHAR(5)), 5);
  INSERT INTO tbLoginToken (idLogin, token) VALUES (
    JSON_VALUE(@user, '$.idLogin'), @token
  );
  SET @json = JSON_QUERY((
    SELECT 1 as success, 'Token generado exitosamente' as message,
           SCOPE_IDENTITY() idLoginToken
    , @token token, JSON_QUERY(@user) auth
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));
  
  SELECT JSON_QUERY(@json) json;
END
GO

-- Probar el procedimiento con debug
EXEC spLoginTokenAdd @json = N'{"codeLogin":"S"}';