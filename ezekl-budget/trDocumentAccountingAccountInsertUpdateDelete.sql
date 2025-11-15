CREATE OR ALTER TRIGGER dbo.trDocumentAccountingAccountInsertUpdateDelete
ON tbDocumentAccountingAccount
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
  -- Trigger para validar que amount * effect sume 0 por factura
  SET NOCOUNT ON;

  -- Obtener todos los idDocument afectados (de inserts, updates y deletes)
  DECLARE @affected_documents TABLE (idDocument INT);
  
  INSERT INTO @affected_documents (idDocument)
  SELECT DISTINCT idDocument FROM inserted
  UNION
  SELECT DISTINCT idDocument FROM deleted;

  -- Validar que para cada factura afectada, la suma de (amount * effect) = 0
  -- PERO solo si quedan registros después de la operación (no validar cuando se eliminan todos)
  IF EXISTS (
    SELECT 1
    FROM @affected_documents ad
    WHERE EXISTS (
      SELECT 1
      FROM tbDocumentAccountingAccount p
      WHERE p.idDocument = ad.idDocument
    ) -- Solo validar si quedan registros para el documento
    AND EXISTS (
      SELECT 1
      FROM tbDocumentAccountingAccount p
      WHERE p.idDocument = ad.idDocument
      GROUP BY p.idDocument
      HAVING ABS(SUM(p.amount * p.effect)) > 0.0001
    )
  )
  BEGIN
    RAISERROR(N'Error: La suma de (amount * effect) para cada factura debe ser igual a 0. Las entradas y salidas deben estar balanceadas.', 16, 1);
    ROLLBACK TRANSACTION;
  END
END
go