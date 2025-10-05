-- Debug detallado de spLoginTokenAdd

-- 1. Verificar que el usuario S existe
SELECT 'Usuario S encontrado:' as debug, * FROM tbLogin WHERE codeLogin = 'S';

-- 2. Probar la consulta interna del procedimiento paso a paso
DECLARE @json NVARCHAR(MAX) = N'{"codeLogin":"S"}';

-- Extraer codeLogin del JSON
SELECT 'JSON de entrada:' as debug, @json as json_input;

-- Parsear JSON con OPENJSON
SELECT 'Parseando JSON:' as debug, * 
FROM OPENJSON(@json) WITH (
  codeLogin VARCHAR(10)
) J;

-- Hacer JOIN con tbLogin
SELECT 'Resultado del JOIN:' as debug, L.idLogin, L.codeLogin, L.nameLogin, L.phoneLogin, L.emailLogin
FROM OPENJSON(@json) WITH (
  codeLogin VARCHAR(10)
) J
INNER JOIN tbLogin L WITH (NOLOCK)
ON L.codeLogin = J.codeLogin;

-- Probar la consulta JSON_QUERY completa
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

SELECT 'Usuario JSON resultado:' as debug, @user as user_json;

-- Validar si @user es NULL
IF @user IS NULL
BEGIN
    SELECT 'ERROR: @user es NULL' as debug;
END
ELSE
BEGIN
    SELECT 'SUCCESS: @user contiene datos' as debug, @user as user_data;
END