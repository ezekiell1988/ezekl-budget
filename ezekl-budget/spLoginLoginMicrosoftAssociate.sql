DROP PROCEDURE IF EXISTS spLoginLoginMicrosoftAssociate
GO
CREATE PROCEDURE spLoginLoginMicrosoftAssociate
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;

  -- Obtener datos del usuario existente (sin columna activeLogin)
  DECLARE @user NVARCHAR(MAX) = JSON_QUERY((
    SELECT L.idLogin, L.codeLogin, L.nameLogin, L.phoneLogin, L.emailLogin
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
    SET @json = JSON_QUERY((
      SELECT 0 as success, 'Usuario no encontrado con el código proporcionado' as message
      FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
    ));
    SELECT JSON_QUERY(@json) json;
    RETURN;
  END

  -- Obtener datos del registro Microsoft
  DECLARE @microsoft NVARCHAR(MAX) = JSON_QUERY((
    SELECT M.idLoginMicrosoft, M.codeLoginMicrosoft
    FROM OPENJSON(@json) WITH (
      codeLoginMicrosoft NVARCHAR(100)
    ) J
    INNER JOIN tbLoginMicrosoft M WITH (NOLOCK)
    ON M.codeLoginMicrosoft = J.codeLoginMicrosoft
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));

  -- Validar que el registro Microsoft existe
  IF @microsoft IS NULL
  BEGIN
    SET @json = JSON_QUERY((
      SELECT 0 as success, 'Registro de Microsoft no encontrado con el código proporcionado' as message
      FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
    ));
    SELECT JSON_QUERY(@json) json;
    RETURN;
  END

  DECLARE @idLogin INT = JSON_VALUE(@user, '$.idLogin');
  DECLARE @idLoginMicrosoft INT = JSON_VALUE(@microsoft, '$.idLoginMicrosoft');

  -- Verificar si ya existe una asociación para cualquiera de las dos cuentas
  IF EXISTS (SELECT 1 FROM tbLoginLoginMicrosoft
             WHERE idLogin = @idLogin OR idLoginMicrosoft = @idLoginMicrosoft)
  BEGIN
    SET @json = JSON_QUERY((
      SELECT 0 as success, 'Una de las cuentas ya está asociada con otra cuenta' as message
      FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
    ));
    SELECT JSON_QUERY(@json) json;
    RETURN;
  END

  -- Crear la asociación (solo con las columnas que existen)
  INSERT INTO tbLoginLoginMicrosoft (idLogin, idLoginMicrosoft)
  VALUES (@idLogin, @idLoginMicrosoft);

  -- Respuesta exitosa con datos del usuario
  SET @json = JSON_QUERY((
    SELECT 1 as success, 'Cuentas asociadas exitosamente' as message,
           SCOPE_IDENTITY() idAssociation,
           JSON_QUERY(@user) userData
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));

  SELECT JSON_QUERY(@json) json;
END
GO

-- Probar el procedimiento
BEGIN TRAN
EXEC spLoginLoginMicrosoftAssociate @json = N'{"codeLogin":"S","codeLoginMicrosoft":"45c3d46f-b00a-42ca-8f7d-414cf18bd1bd"}';
ROLLBACK TRAN

-- Resetear el identity de la tabla
DBCC CHECKIDENT ('tbLoginLoginMicrosoft', RESEED, 0);