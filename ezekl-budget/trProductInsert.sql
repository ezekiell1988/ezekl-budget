CREATE OR ALTER TRIGGER trProductInsert
ON tbProduct
AFTER INSERT, DELETE
AS
BEGIN
  -- Trigger para validar que cada effect sume 100% por producto
  SET NOCOUNT ON;

  -- Crear registro en cuentas contables
  INSERT INTO tbProductAccountingAccount (idProduct, idAccountingAccount, effect, [percent])
  SELECT I.idProduct, 5, 1, 100
  FROM inserted I
  UNION ALL
  SELECT I.idProduct, 1, -1, 100
  FROM inserted I;

  -- Crear registro en configuracion
  INSERT INTO tbProductConfiguration (idProduct)
  SELECT I.idProduct FROM inserted I;

  -- Crear registro en tipo de entrega
  INSERT INTO tbProductDeliveryType (idProduct, idDeliveryType)
  SELECT I.idProduct, DT.idDeliveryType
  FROM inserted I
  CROSS JOIN tbDeliveryType DT;

  -- Crear registro en tipo de entrega precio
  INSERT INTO tbProductDeliveryTypePrice (idProductDeliveryType, price)
  SELECT PDT.idProductDeliveryType, 0
  FROM inserted I
  INNER JOIN tbProductDeliveryType PDT
  ON PDT.idProduct = I.idProduct
  ORDER BY PDT.idProductDeliveryType;
END
GO
