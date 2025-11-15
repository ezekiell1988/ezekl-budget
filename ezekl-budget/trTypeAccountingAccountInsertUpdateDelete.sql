CREATE OR ALTER TRIGGER trTypeAccountingAccountInsertUpdateDelete
ON tbTypeAccountingAccount
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
  -- Trigger para validar que cada effect sume 100% por producto
  SET NOCOUNT ON;

  -- Obtener todas las combinaciones de idType y effect afectadas
  DECLARE @affected_combinations TABLE (idType INT, effect INT);
  
  INSERT INTO @affected_combinations (idType, effect)
  SELECT DISTINCT idType, effect FROM inserted
  UNION
  SELECT DISTINCT idType, effect FROM deleted;

  -- Validar que para cada combinación de idType y effect afectada, los porcentajes sumen 100
  -- PERO solo si quedan registros después de la operación (no validar cuando se eliminan todos)
  IF EXISTS (
    SELECT 1
    FROM @affected_combinations ac
    WHERE EXISTS (
      SELECT 1
      FROM tbTypeAccountingAccount p
      WHERE p.idType = ac.idType
        AND p.effect = ac.effect
    ) -- Solo validar si quedan registros
    AND EXISTS (
      SELECT 1
      FROM tbTypeAccountingAccount p
      WHERE p.idType = ac.idType
        AND p.effect = ac.effect
      GROUP BY p.idType, p.effect
      HAVING ABS(SUM(p.[percent]) - 100.0000) > 0.0001
    )
  )
  BEGIN
    RAISERROR(N'Error: Los porcentajes para cada effect de un producto deben sumar exactamente 100.', 16, 1);
    ROLLBACK TRANSACTION;
  END
END
GO
