CREATE OR ALTER TRIGGER dbo.tbDocumentAccountingAccountInsertUpdate
ON tbDocument
AFTER INSERT, UPDATE
AS
BEGIN
  -- Trigger de validación financiera para documentos
  -- Asegura que los cálculos de precios, descuentos, impuestos y totales sean consistentes
  SET NOCOUNT ON;

  -- Validación de integridad contable: verifica que las operaciones matemáticas del documento sean correctas
  -- 1. Precio - Descuento = Subtotal
  -- 2. Subtotal + Impuestos = Total
  IF EXISTS (
    SELECT 1
    FROM inserted i
    WHERE (i.priceDocument - i.discountDocument - i.subtotalDocument) > 0.0001
    OR (i.subtotalDocument + i.taxesDocument - i.totalDocument) > 0.0001
  )
  BEGIN
    RAISERROR(N'Error: Los cálculos del documento no son válidos. Verifique que: Precio - Descuento = Subtotal y Subtotal + Impuestos = Total', 16, 1);
    ROLLBACK TRANSACTION;
  END
END
go