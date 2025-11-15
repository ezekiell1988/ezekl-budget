CREATE OR ALTER TRIGGER trDocumentProductAccountingAccountInsertUpdateDelete
ON tbDocumentProductAccountingAccount
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
  -- Trigger para validar que cada effect sume 100% por producto
  SET NOCOUNT ON;

  -- Obtener todas las combinaciones de idDocumentProduct y effect afectadas
  DECLARE @affected_combinations TABLE (idDocumentProduct INT, effect INT);
  
  INSERT INTO @affected_combinations (idDocumentProduct, effect)
  SELECT DISTINCT idDocumentProduct, effect FROM inserted
  UNION
  SELECT DISTINCT idDocumentProduct, effect FROM deleted;

  -- Validar que para cada combinación de idDocumentProduct y effect afectada, los porcentajes sumen 100
  -- PERO solo si quedan registros después de la operación (no validar cuando se eliminan todos)
  IF EXISTS (
    SELECT 1
    FROM @affected_combinations ac
    WHERE EXISTS (
      SELECT 1
      FROM tbDocumentProductAccountingAccount p
      WHERE p.idDocumentProduct = ac.idDocumentProduct
        AND p.effect = ac.effect
    ) -- Solo validar si quedan registros
    AND EXISTS (
      SELECT 1
      FROM tbDocumentProductAccountingAccount p
      WHERE p.idDocumentProduct = ac.idDocumentProduct
      GROUP BY p.idDocumentProduct
      HAVING ABS(SUM(p.amount * p.effect)) > 0.0001
    )
  )
  BEGIN
    RAISERROR(N'Error: Los porcentajes para cada effect de un producto deben sumar exactamente 100.', 16, 1);
    ROLLBACK TRANSACTION;
  END
END
GO
