-- Probar spLoginTokenAdd con comillas simples
BEGIN TRAN
EXEC spLoginTokenAdd @json = N'{"codeLogin":"S"}';
ROLLBACK TRAN

-- También probar sin ROLLBACK para ver el resultado completo
EXEC spLoginTokenAdd @json = N'{"codeLogin":"S"}';