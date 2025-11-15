CREATE OR ALTER PROCEDURE spTruncateTable
  @table VARCHAR(200)
AS
BEGIN
  SET NOCOUNT ON;
  DECLARE @deleteSql VARCHAR(500) = 'DELETE FROM ' + @table + ';';
  -- Borrar los registros de la tabla
  EXEC(@deleteSql);
  -- Resetear el identity de las tablas antes de la prueba
  DBCC CHECKIDENT (@table, RESEED, 0);
END
GO

-- Probar el procedimiento corregido
EXEC spTruncateTable @table = 'dbo.tbType';