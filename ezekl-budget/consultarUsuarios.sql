-- Consultar usuarios existentes en la tabla tbLogin
SELECT TOP 10 
    idLogin, 
    codeLogin, 
    nameLogin, 
    emailLogin, 
    phoneLogin
FROM tbLogin WITH (NOLOCK)
ORDER BY idLogin;

-- Contar total de usuarios
SELECT COUNT(*) AS TotalUsuarios FROM tbLogin WITH (NOLOCK);