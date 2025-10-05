-- Crear usuarios de prueba para el sistema de login

-- Verificar si existe la tabla tbLogin
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'tbLogin')
BEGIN
    CREATE TABLE tbLogin (
        idLogin INT IDENTITY(1,1) PRIMARY KEY,
        codeLogin VARCHAR(10) NOT NULL UNIQUE,
        nameLogin NVARCHAR(100) NOT NULL,
        emailLogin NVARCHAR(100) NOT NULL,
        phoneLogin NVARCHAR(20) NULL,
        createdAt DATETIME2 DEFAULT GETDATE()
    );
    PRINT 'Tabla tbLogin creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Tabla tbLogin ya existe';
END

-- Verificar si existe la tabla tbLoginToken
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'tbLoginToken')
BEGIN
    CREATE TABLE tbLoginToken (
        idLoginToken INT IDENTITY(1,1) PRIMARY KEY,
        idLogin INT NOT NULL,
        token VARCHAR(5) NOT NULL,
        createdAt DATETIME2 DEFAULT GETDATE(),
        FOREIGN KEY (idLogin) REFERENCES tbLogin(idLogin)
    );
    PRINT 'Tabla tbLoginToken creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Tabla tbLoginToken ya existe';
END

-- Insertar usuarios de prueba si no existen
IF NOT EXISTS (SELECT * FROM tbLogin WHERE codeLogin = 'S')
BEGIN
    INSERT INTO tbLogin (codeLogin, nameLogin, emailLogin, phoneLogin) 
    VALUES ('S', 'Usuario de Prueba S', 'usuario.s@example.com', '+506 1234-5678');
    PRINT 'Usuario S creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Usuario S ya existe';
END

IF NOT EXISTS (SELECT * FROM tbLogin WHERE codeLogin = 'ADMIN')
BEGIN
    INSERT INTO tbLogin (codeLogin, nameLogin, emailLogin, phoneLogin) 
    VALUES ('ADMIN', 'Administrador del Sistema', 'admin@ezekl.com', '+506 8888-8888');
    PRINT 'Usuario ADMIN creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Usuario ADMIN ya existe';
END

IF NOT EXISTS (SELECT * FROM tbLogin WHERE codeLogin = 'TEST')
BEGIN
    INSERT INTO tbLogin (codeLogin, nameLogin, emailLogin, phoneLogin) 
    VALUES ('TEST', 'Usuario de Prueba Test', 'test@ezekl.com', '+506 9999-9999');
    PRINT 'Usuario TEST creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Usuario TEST ya existe';
END

-- Mostrar usuarios existentes
SELECT 
    idLogin, 
    codeLogin, 
    nameLogin, 
    emailLogin, 
    phoneLogin,
    createdAt
FROM tbLogin 
ORDER BY idLogin;