DROP PROCEDURE IF EXISTS spLoginMicrosoftAddOrEdit
GO
CREATE PROCEDURE spLoginMicrosoftAddOrEdit
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  
  -- Extraer datos principales de Microsoft del JSON
  DECLARE @microsoftUserId NVARCHAR(500);
  DECLARE @email NVARCHAR(500);
  DECLARE @displayName NVARCHAR(255);
  DECLARE @userPrincipalName NVARCHAR(500);
  DECLARE @givenName NVARCHAR(255);
  DECLARE @surname NVARCHAR(255);
  DECLARE @jobTitle NVARCHAR(255);
  DECLARE @department NVARCHAR(255);
  DECLARE @companyName NVARCHAR(255);
  DECLARE @officeLocation NVARCHAR(255);
  DECLARE @businessPhones NVARCHAR(MAX);
  DECLARE @mobilePhone NVARCHAR(50);
  DECLARE @microsoftTenantId NVARCHAR(100);
  DECLARE @preferredLanguage NVARCHAR(10);
  DECLARE @accessToken NVARCHAR(MAX);
  DECLARE @refreshToken NVARCHAR(MAX);
  DECLARE @tokenExpiresAt DATETIME2;
  
  -- Parsear JSON de entrada usando OPENJSON (más eficiente)
  SELECT 
    @microsoftUserId = J.id,
    @email = J.mail,
    @displayName = J.displayName,
    @userPrincipalName = J.userPrincipalName,
    @givenName = J.givenName,
    @surname = J.surname,
    @jobTitle = J.jobTitle,
    @department = J.department,
    @companyName = J.companyName,
    @officeLocation = J.officeLocation,
    @businessPhones = J.businessPhones,
    @mobilePhone = J.mobilePhone,
    @microsoftTenantId = J.tenantId,
    @preferredLanguage = J.preferredLanguage,
    @accessToken = J.accessToken,
    @refreshToken = J.refreshToken,
    @tokenExpiresAt = TRY_CAST(J.tokenExpiresAt AS DATETIME2)
  FROM OPENJSON(@json) WITH (
    id NVARCHAR(500) '$.id',
    mail NVARCHAR(500) '$.mail',
    displayName NVARCHAR(255) '$.displayName',
    userPrincipalName NVARCHAR(500) '$.userPrincipalName',
    givenName NVARCHAR(255) '$.givenName',
    surname NVARCHAR(255) '$.surname',
    jobTitle NVARCHAR(255) '$.jobTitle',
    department NVARCHAR(255) '$.department',
    companyName NVARCHAR(255) '$.companyName',
    officeLocation NVARCHAR(255) '$.officeLocation',
    businessPhones NVARCHAR(MAX) '$.businessPhones' AS JSON,
    mobilePhone NVARCHAR(50) '$.mobilePhone',
    tenantId NVARCHAR(100) '$.tenantId',
    preferredLanguage NVARCHAR(10) '$.preferredLanguage',
    accessToken NVARCHAR(MAX) '$.accessToken',
    refreshToken NVARCHAR(MAX) '$.refreshToken',
    tokenExpiresAt NVARCHAR(50) '$.tokenExpiresAt'
  ) AS J;
  
  -- Usar userPrincipalName como email si mail está vacío
  IF @email IS NULL OR @email = ''
    SET @email = @userPrincipalName;
  
  -- Validar datos mínimos requeridos
  IF @microsoftUserId IS NULL OR @email IS NULL
  BEGIN
    SET @json = JSON_QUERY((
      SELECT 0 as success, 'Datos de Microsoft incompletos: ID y email son requeridos' as message
      FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
    ));
    SELECT JSON_QUERY(@json) json;
    RETURN;
  END
  
  -- Verificar si el usuario ya existe por email o Microsoft ID
  DECLARE @existingId INT;
  SELECT @existingId = idLoginMicrosoft 
  FROM tbLoginMicrosoft 
  WHERE emailLoginMicrosoft = @email 
     OR codeLoginMicrosoft = @microsoftUserId;
  
  -- Variables para el resultado
  DECLARE @operationType NVARCHAR(10);
  DECLARE @recordId INT;
  
  IF @existingId IS NOT NULL
  BEGIN
    -- ACTUALIZAR registro existente
    UPDATE tbLoginMicrosoft SET
      codeLoginMicrosoft = @microsoftUserId,
      nameLoginMicrosoft = ISNULL(@displayName, nameLoginMicrosoft),
      emailLoginMicrosoft = @email,
      userPrincipalName = @userPrincipalName,
      jobTitle = @jobTitle,
      department = @department,
      companyName = @companyName,
      officeLocation = @officeLocation,
      businessPhones = @businessPhones,
      mobilePhone = @mobilePhone,
      microsoftTenantId = @microsoftTenantId,
      preferredLanguage = @preferredLanguage,
      accessToken = @accessToken,
      refreshToken = @refreshToken,
      tokenExpiresAt = @tokenExpiresAt,
      lastLoginDate = GETDATE(),
      modifiedDate = GETDATE(),
      loginCount = ISNULL(loginCount, 0) + 1,
      isActive = 1
    WHERE idLoginMicrosoft = @existingId;
    
    SET @operationType = 'UPDATE';
    SET @recordId = @existingId;
  END
  ELSE
  BEGIN
    -- INSERTAR nuevo registro
    INSERT INTO tbLoginMicrosoft (
      codeLoginMicrosoft,
      nameLoginMicrosoft,
      emailLoginMicrosoft,
      userPrincipalName,
      jobTitle,
      department,
      companyName,
      officeLocation,
      businessPhones,
      mobilePhone,
      microsoftTenantId,
      preferredLanguage,
      accessToken,
      refreshToken,
      tokenExpiresAt,
      createdDate,
      lastLoginDate,
      modifiedDate,
      loginCount,
      isActive,
      isVerified,
      accountEnabled
    ) VALUES (
      @microsoftUserId,
      @displayName,
      @email,
      @userPrincipalName,
      @jobTitle,
      @department,
      @companyName,
      @officeLocation,
      @businessPhones,
      @mobilePhone,
      @microsoftTenantId,
      @preferredLanguage,
      @accessToken,
      @refreshToken,
      @tokenExpiresAt,
      GETDATE(),
      GETDATE(),
      GETDATE(),
      1,
      1,
      1,
      1
    );
    
    SET @operationType = 'INSERT';
    SET @recordId = SCOPE_IDENTITY();
  END
  
  -- Obtener datos completos del usuario para la respuesta
  DECLARE @userInfo NVARCHAR(MAX) = JSON_QUERY((
    SELECT 
      M.idLoginMicrosoft,
      M.codeLoginMicrosoft as microsoftUserId,
      M.nameLoginMicrosoft as displayName,
      M.emailLoginMicrosoft as email,
      M.userPrincipalName,
      M.jobTitle,
      M.department,
      M.companyName,
      M.officeLocation,
      M.businessPhones,
      M.mobilePhone,
      M.microsoftTenantId,
      M.preferredLanguage,
      M.loginCount,
      M.lastLoginDate,
      M.isActive,
      M.isVerified,
      M.accountEnabled
    FROM tbLoginMicrosoft M
    WHERE M.idLoginMicrosoft = @recordId
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));
  
  -- Verificar si el usuario Microsoft está asociado con tbLogin
  DECLARE @linkedLoginId INT = NULL;
  DECLARE @linkedUserData NVARCHAR(MAX) = NULL;
  
  -- Buscar si existe relación con tbLogin por email o codeLogin
  SELECT @linkedLoginId = L.idLogin
  FROM tbLogin L
  INNER JOIN tbLoginLoginMicrosoft LM ON L.idLogin = LM.idLogin
  WHERE LM.idLoginMicrosoft = @recordId;
  
  -- Si hay asociación, obtener datos del usuario para el JWE
  IF @linkedLoginId IS NOT NULL
  BEGIN
    SET @linkedUserData = JSON_QUERY((
      SELECT 
        L.idLogin,
        L.codeLogin,
        L.nameLogin,
        L.emailLogin,
        L.phoneLogin
      FROM tbLogin L
      INNER JOIN tbLoginLoginMicrosoft LM ON L.idLogin = LM.idLogin
      INNER JOIN tbLoginMicrosoft M ON LM.idLoginMicrosoft = M.idLoginMicrosoft
      WHERE L.idLogin = @linkedLoginId AND M.idLoginMicrosoft = @recordId
      FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
    ));
  END
  
  -- Construir respuesta según si hay asociación o no
  SET @json = JSON_QUERY((
    SELECT 
      1 as success, 
      CONCAT('Usuario Microsoft ', @operationType, ' exitosamente') as message,
      @operationType as operation,
      @recordId as idLoginMicrosoft,
      CASE 
        WHEN @linkedLoginId IS NOT NULL THEN 'associated'
        ELSE 'needs_association'
      END as associationStatus,
      JSON_QUERY(@userInfo) as microsoftUser,
      JSON_QUERY(@linkedUserData) as linkedUser
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));
  
  SELECT JSON_QUERY(@json) json;
END
GO

-- Ejemplo de uso - Insertar nuevo usuario de Microsoft
BEGIN TRAN
EXEC spLoginMicrosoftAddOrEdit @json = N'{
  "id": "b5c4ceb3-9bf1-4a1f-8e4e-72b852d771e9",
  "mail": "juan.perez@company.com",
  "displayName": "Juan Pérez",
  "userPrincipalName": "juan.perez@company.onmicrosoft.com",
  "givenName": "Juan",
  "surname": "Pérez", 
  "jobTitle": "Desarrollador Senior",
  "department": "Tecnología",
  "companyName": "Mi Empresa S.A.",
  "officeLocation": "Oficina Central",
  "businessPhones": ["555-1234", "555-5678"],
  "mobilePhone": "555-9999",
  "tenantId": "2f80d4e1-da0e-4b6d-84da-30f67e280e4b",
  "preferredLanguage": "es-MX",
  "accessToken": "encrypted_access_token_here",
  "refreshToken": "encrypted_refresh_token_here",
  "tokenExpiresAt": "2025-10-08T20:00:00Z"
}';
ROLLBACK TRAN
GO

-- Ejemplo de uso - Actualizar usuario existente
BEGIN TRAN
EXEC spLoginMicrosoftAddOrEdit @json = N'{
  "id": "b5c4ceb3-9bf1-4a1f-8e4e-72b852d771e9",
  "mail": "juan.perez@company.com",
  "displayName": "Juan Carlos Pérez",
  "jobTitle": "Lead Developer",
  "accessToken": "new_encrypted_access_token_here"
}';
ROLLBACK TRAN
GO

-- Resetear contador de identidad después de las pruebas
IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'tbLoginMicrosoft')
BEGIN
    DECLARE @maxId INT;
    SELECT @maxId = ISNULL(MAX(idLoginMicrosoft), 0) FROM tbLoginMicrosoft;
    
    -- Resetear el contador de identidad al siguiente número disponible
    DBCC CHECKIDENT('tbLoginMicrosoft', RESEED, @maxId);
    
    PRINT '✅ Contador de identidad de tbLoginMicrosoft reseteado correctamente';
END
GO