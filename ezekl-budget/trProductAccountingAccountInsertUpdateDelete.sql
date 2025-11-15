CREATE OR ALTER TRIGGER trProductAccountingAccountInsertUpdateDelete
ON tbProductAccountingAccount
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
  -- Trigger para validar que cada effect sume 100% por producto
  SET NOCOUNT ON;

  -- Obtener todas las combinaciones de idProduct y effect afectadas
  DECLARE @affected_combinations TABLE (idProduct INT, effect INT);
  
  INSERT INTO @affected_combinations (idProduct, effect)
  SELECT DISTINCT idProduct, effect FROM inserted
  UNION
  SELECT DISTINCT idProduct, effect FROM deleted;

  -- Validar que para cada combinación de idProduct y effect afectada, los porcentajes sumen 100
  -- PERO solo si quedan registros después de la operación (no validar cuando se eliminan todos)
  IF EXISTS (
    SELECT 1
    FROM @affected_combinations ac
    WHERE EXISTS (
      SELECT 1
      FROM tbProductAccountingAccount p
      WHERE p.idProduct = ac.idProduct
        AND p.effect = ac.effect
    ) -- Solo validar si quedan registros
    AND EXISTS (
      SELECT 1
      FROM tbProductAccountingAccount p
      WHERE p.idProduct = ac.idProduct
        AND p.effect = ac.effect
      GROUP BY p.idProduct, p.effect
      HAVING ABS(SUM(p.[percent]) - 100.0000) > 0.0001
    )
  )
  BEGIN
    RAISERROR(N'Error: Los porcentajes para cada effect de un producto deben sumar exactamente 100.', 16, 1);
    ROLLBACK TRANSACTION;
  END
END
GO
