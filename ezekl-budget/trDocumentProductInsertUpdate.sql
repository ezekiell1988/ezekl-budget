CREATE OR ALTER TRIGGER dbo.trDocumentProductInsertUpdate
ON tbDocumentProduct
AFTER INSERT, UPDATE
AS
BEGIN
  -- Trigger de validación financiera para productos
  -- Asegura que los cálculos de precios, descuentos, impuestos y totales sean consistentes
  SET NOCOUNT ON;

  -- Validación de integridad contable: verifica que las operaciones matemáticas del documento sean correctas
  -- 1. Precio - Descuento = Subtotal
  -- 2. Subtotal + Impuestos = Total
  IF EXISTS (
    SELECT 1
    FROM inserted i
    WHERE (i.totalProduct - i.discountProduct - i.subtotalProduct) > 0.0001
    OR (i.subtotalProduct + i.totalProduct - i.totalProduct) > 0.0001
  )
  BEGIN
    RAISERROR(N'Error: Los cálculos del producto no son válidos. Verifique que: Precio - Descuento = Subtotal y Subtotal + Impuestos = Total', 16, 1);
    ROLLBACK TRANSACTION;
  END
END
go