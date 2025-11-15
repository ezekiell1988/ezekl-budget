CREATE OR ALTER PROCEDURE spDocumentAdd
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  DECLARE @jsonData NVARCHAR(MAX);
  DECLARE @idDocument INT;
  DECLARE @codeMonth VARCHAR(6) = ISNULL(JSON_VALUE(@json, '$.codeMonth')
    , LEFT(CONVERT(VARCHAR(8), CAST(JSON_VALUE(@json, '$.documentDate') AS DATE), 112), 6)
  );
  DECLARE @idMonth INT = ISNULL(JSON_VALUE(@json, '$.idMonth')
    , (SELECT idMonth FROM tbMonth WHERE codeMonth = @codeMonth)
  );
  DECLARE @idCompany INT = ISNULL(JSON_VALUE(@json, '$.idCompany'), (
    SELECT idCompany
    FROM tbCompany
    WHERE codeCompany = JSON_VALUE(@json, '$.codeCompany')
  ));

  -- Mes
  IF @idMonth IS NULL
  BEGIN
    INSERT INTO tbMonth (codeMonth) VALUES (@codeMonth)
    SET @idMonth = SCOPE_IDENTITY()
  END

  -- Compania
  IF @idCompany IS NULL
  BEGIN
    SET @jsonData = JSON_MODIFY(@json, '$.descriptionCompany'
      , ISNULL(JSON_VALUE(@json, '$.descriptionCompany'), N'Sin descripción')
    );
    
    -- Crear tabla temporal para el resultado del sp
    CREATE TABLE #CompanyResult (json NVARCHAR(MAX));
    
    INSERT INTO #CompanyResult
    EXEC spCompanyAdd @json = @jsonData;
    
    SET @idCompany = JSON_VALUE((SELECT TOP 1 json FROM #CompanyResult), '$.idCompany');
    
    DROP TABLE #CompanyResult;
  END

  -- Crear documento
  INSERT INTO tbDocument (documentDate) VALUES (JSON_VALUE(@json, '$.documentDate'));

  -- id de registro
  SET @idDocument = SCOPE_IDENTITY();

  -- Crear documento - compania
  INSERT INTO tbDocumentCompany (idDocument, idCompany) VALUES (@idDocument, @idCompany);

  -- Crear documento - tipo
  INSERT INTO tbDocumentType (idDocument, idType) VALUES (
    @idDocument, JSON_VALUE(@json, '$.idType')
  );
  -- Crear mes - documento
  INSERT INTO tbMonthDocument (idMonth, idDocument) VALUES (@idMonth, @idDocument);

  -- Crear documento - productos (INSERT masivo con OUTPUT)
  DECLARE @ProductsInserted TABLE (
    idDocumentProduct INT,
    lineDocumentProduct INT,
    idProduct INT
  );

  -- INSERT masivo de productos con OUTPUT
  INSERT INTO tbDocumentProduct (
    lineDocumentProduct,
    idDocument,
    idProduct,
    nameProduct,
    priceProduct,
    discountProduct,
    subtotalProduct,
    taxesProduct,
    totalProduct,
    taxesPercentProduct,
    discountPercentProduct
  )
  OUTPUT 
    INSERTED.idDocumentProduct,
    INSERTED.lineDocumentProduct,
    INSERTED.idProduct
  INTO @ProductsInserted
  SELECT 
    ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS lineDocumentProduct,
    @idDocument,
    CAST(JSON_VALUE(value, '$.idProduct') AS INT),
    JSON_VALUE(value, '$.nameProduct'),
    CAST(JSON_VALUE(value, '$.priceProduct') AS DECIMAL(18,4)),
    CAST(JSON_VALUE(value, '$.discountProduct') AS DECIMAL(18,4)),
    CAST(JSON_VALUE(value, '$.subtotalProduct') AS DECIMAL(18,4)),
    CAST(JSON_VALUE(value, '$.taxesProduct') AS DECIMAL(18,4)),
    CAST(JSON_VALUE(value, '$.totalProduct') AS DECIMAL(18,4)),
    CAST(JSON_VALUE(value, '$.taxesPercentProduct') AS DECIMAL(18,4)),
    CAST(JSON_VALUE(value, '$.discountPercentProduct') AS DECIMAL(18,4))
  FROM OPENJSON(JSON_QUERY(@json, '$.products'));

  -- INSERT masivo de cuentas contables por producto
  INSERT INTO tbDocumentProductAccountingAccount (
    idDocumentProduct,
    idAccountingAccount,
    effect,
    amount
  )
  SELECT 
    pi.idDocumentProduct,
    CAST(JSON_VALUE(accounts.value, '$.idAccountingAccount') AS INT),
    CAST(JSON_VALUE(accounts.value, '$.effect') AS INT),
    CAST(JSON_VALUE(accounts.value, '$.amount') AS DECIMAL(18,4))
  FROM OPENJSON(JSON_QUERY(@json, '$.products')) AS products
  CROSS APPLY @ProductsInserted pi
  CROSS APPLY OPENJSON(JSON_QUERY(products.value, '$.accounts')) AS accounts
  WHERE pi.idProduct = CAST(JSON_VALUE(products.value, '$.idProduct') AS INT);

  -- INSERT/UPDATE masivo de cuentas contables del documento (acumuladas)
  ; WITH AccountSums AS (
    SELECT
      @idDocument AS idDocument,
      CAST(JSON_VALUE(accounts.value, '$.idAccountingAccount') AS INT) AS idAccountingAccount,
      CAST(JSON_VALUE(accounts.value, '$.effect') AS INT) AS effect,
      SUM(CAST(JSON_VALUE(accounts.value, '$.amount') AS DECIMAL(18,4))) AS totalAmount
    FROM OPENJSON(JSON_QUERY(@json, '$.products')) AS products
    CROSS APPLY OPENJSON(JSON_QUERY(products.value, '$.accounts')) AS accounts
    GROUP BY
      JSON_VALUE(accounts.value, '$.idAccountingAccount'),
      JSON_VALUE(accounts.value, '$.effect')
  )
  MERGE tbDocumentAccountingAccount AS target
  USING AccountSums AS source
  ON target.idDocument = source.idDocument
     AND target.idAccountingAccount = source.idAccountingAccount
     AND target.effect = source.effect
  WHEN MATCHED THEN
    UPDATE SET amount = target.amount + source.totalAmount
  WHEN NOT MATCHED THEN
    INSERT (idDocument, idAccountingAccount, effect, amount)
    VALUES (source.idDocument, source.idAccountingAccount, source.effect, source.totalAmount);

  -- Actualizar totales del documento basándose en la suma de productos
  UPDATE tbDocument 
  SET 
    priceDocument = totals.totalPrice,
    discountDocument = totals.totalDiscount,
    subtotalDocument = totals.totalSubtotal,
    taxesDocument = totals.totalTaxes,
    totalDocument = totals.totalAmount
  FROM tbDocument d
  CROSS APPLY (
    SELECT 
      SUM(dp.priceProduct) AS totalPrice,
      SUM(dp.discountProduct) AS totalDiscount,
      SUM(dp.subtotalProduct) AS totalSubtotal,
      SUM(dp.taxesProduct) AS totalTaxes,
      SUM(dp.totalProduct) AS totalAmount
    FROM tbDocumentProduct dp 
    WHERE dp.idDocument = @idDocument
  ) AS totals
  WHERE d.idDocument = @idDocument;

  -- Preparar query
  SET @json = JSON_QUERY((
    SELECT @idDocument idDocument
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));
  
  SELECT JSON_QUERY(@json) json;
END
GO

-- Probar el procedimiento corregido
EXEC spDocumentAdd @json = N'{
  "idType": 2,
  "documentDate": "2025-10-14",
  "codeCompany": "31010001",
  "nameCompany": "Chino San Ramón",
  "products": [
    {
      "idProduct": 3,
      "nameProduct": "Soda 2.5 Litros",
      "priceProduct": 111.1111,
      "discountProduct": 11.1111,
      "subtotalProduct": 100,
      "taxesProduct": 13,
      "totalProduct": 113,
      "taxesPercentProduct": 13,
      "discountPercentProduct": 10,
      "accounts": [
        {
          "idAccountingAccount": 5,
          "effect": 1,
          "amount": 113
        },
        {
          "idAccountingAccount": 1,
          "effect": -1,
          "amount": 113
        }
      ]
    }
  ]
}';

/*
EXEC spTruncateTable @table = 'dbo.tbDocument';
EXEC spTruncateTable @table = 'dbo.tbDocumentAccountingAccount';
EXEC spTruncateTable @table = 'dbo.tbDocumentCompany';
EXEC spTruncateTable @table = 'dbo.tbDocumentProduct';
EXEC spTruncateTable @table = 'dbo.tbDocumentProductAccountingAccount';
EXEC spTruncateTable @table = 'dbo.tbDocumentType';
EXEC spTruncateTable @table = 'dbo.tbMonth';
EXEC spTruncateTable @table = 'dbo.tbMonthDocument';
*/