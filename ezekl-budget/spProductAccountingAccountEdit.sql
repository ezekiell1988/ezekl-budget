CREATE OR ALTER PROCEDURE spProductAccountingAccountEdit
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  DECLARE @idProduct INT = JSON_VALUE(@json, '$.idProduct');
  DECLARE @idCompany INT = JSON_VALUE(@json, '$.idCompany');
  DECLARE @accountingAccount TABLE (
    idAccountingAccount INT
    , effect INT
    , [percent] DECIMAL(18,4)
    , idProductAccountingAccount INT
    , idProduct INT
    , rowNum INT
  );

  -- Validar que el producto existe y pertenece a la compañía
  IF NOT EXISTS (
    SELECT 1
    FROM tbCompanyProduct
    WHERE idProduct = @idProduct
    AND idCompany = @idCompany
  )
  BEGIN
    RAISERROR(N'Error: El producto no existe.', 16, 1);
    RETURN;
  END

  -- Totales
  DECLARE @variationRecords INT;

  -- Cargar registros recibidos
  INSERT INTO @accountingAccount
  SELECT Q.*
  , @idProduct
  , ROW_NUMBER() OVER (ORDER BY idProductAccountingAccount DESC
    , idAccountingAccount, effect
  )
  FROM (
    SELECT idAccountingAccount, effect, SUM([percent]) [percent]
    , idProductAccountingAccount
    FROM OPENJSON(@json, '$.accountingAccount') WITH (
      idAccountingAccount INT
      , effect INT
      , [percent] DECIMAL(18,4)
      , idProductAccountingAccount INT
    )
    GROUP BY idAccountingAccount, effect, idProductAccountingAccount
  ) Q;

  -- Validar porcentaje
  IF EXISTS (
    SELECT 1
    FROM @accountingAccount aa
    GROUP BY aa.idProduct, aa.effect
    HAVING ABS(SUM(aa.[percent]) - 100.0000) > 0.0001
  ) RAISERROR(N'Error: Los porcentajes para cada effect de un producto deben sumar exactamente 100.', 16, 1);

  -- Determinar si la cantidad de items para igualar los recibidos con los que hay en BD
  SET @variationRecords = (SELECT COUNT(rowNum) FROM @accountingAccount);
  SET @variationRecords = @variationRecords - ISNULL((
    SELECT COUNT(idProductAccountingAccount)
    FROM tbProductAccountingAccount
    WHERE idProduct = @idProduct
  ), 0);

  -- Proceso para que la cantidad de registros recibidos sean los mismos que los de la BD
  IF @variationRecords != 0
  BEGIN
    -- Actualizar porcentajes para que solo las primeras 2 cuentas tengan porcentaje y sumen 100 en cada efecto (1 y -1)
    ; WITH accountingAccount AS (
      SELECT ROW_NUMBER() OVER (ORDER BY idProductAccountingAccount) rowNum
      , idProductAccountingAccount
      FROM tbProductAccountingAccount
      WHERE idProduct = @idProduct
    )
    UPDATE PAA
    SET PAA.effect = CASE AA.rowNum WHEN 1 THEN 1 ELSE -1 END
    , PAA.[percent] = CASE WHEN AA.rowNum IN (1, 2) THEN 100 ELSE 0 END
    FROM tbProductAccountingAccount PAA
    INNER JOIN accountingAccount AA
    ON AA.idProductAccountingAccount = PAA.idProductAccountingAccount;

    -- Crear nuevos registros
    IF @variationRecords > 0
    BEGIN
      -- Insertar fila por fila y capturar IDs
      DECLARE @currentRowNum INT = 0;

      -- Se crea cursor con registros a crear
      DECLARE insertCursor CURSOR LOCAL FAST_FORWARD FOR
        SELECT rowNum
        FROM @accountingAccount
        WHERE idProductAccountingAccount IS NULL
        ORDER BY rowNum;

      -- Se abre cursor
      OPEN insertCursor;

      -- Se mueve al primer registro
      FETCH NEXT FROM insertCursor INTO @currentRowNum;

      WHILE @@FETCH_STATUS = 0
      BEGIN
        -- Se crea registro
        INSERT INTO tbProductAccountingAccount (idProduct, idAccountingAccount, effect, [percent])
        SELECT idProduct, idAccountingAccount, effect, 0
        FROM @accountingAccount
        WHERE rowNum = @currentRowNum;

        -- Se actualiza id creado
        UPDATE @accountingAccount
        SET idProductAccountingAccount = SCOPE_IDENTITY()
        WHERE rowNum = @currentRowNum;

        -- Se mueve al siguiente registro
        FETCH NEXT FROM insertCursor INTO @currentRowNum;
      END

      -- Se cierra cursor
      CLOSE insertCursor;

      -- Se elimina la memoria del cursor
      DEALLOCATE insertCursor;
    END

    -- Eliminar registros extra
    IF @variationRecords < 0
    BEGIN
      ; WITH query AS (
        SELECT ROW_NUMBER() OVER (ORDER BY PAA.idProductAccountingAccount DESC) rowNum
        , PAA.idProductAccountingAccount
        FROM tbProductAccountingAccount PAA
        LEFT JOIN @accountingAccount AA
        ON AA.idProductAccountingAccount = PAA.idProductAccountingAccount
        WHERE AA.idProductAccountingAccount IS NULL
      )
      DELETE PAA
      FROM tbProductAccountingAccount PAA
      INNER JOIN query Q
      ON Q.idProductAccountingAccount = PAA.idProductAccountingAccount
      WHERE Q.rowNum <= ABS(@variationRecords);
    END
  END

  -- Proceso para asignar id de la BD a los registros recibidos
  ; WITH accountingAssociateDB AS (
    SELECT ROW_NUMBER() OVER (ORDER BY PAA.idProduct) rowNum
    , PAA.idProductAccountingAccount
    FROM tbProductAccountingAccount PAA WITH (NOLOCK)
    LEFT JOIN @accountingAccount AA
    ON AA.idProductAccountingAccount = PAA.idProductAccountingAccount
    WHERE PAA.idProduct = @idProduct
    AND AA.idProductAccountingAccount IS NULL
  ), accountingAssociate AS (
    SELECT ROW_NUMBER() OVER (ORDER BY AA.idProduct) rowNumAssociate
    , AA.rowNum, AA.idProductAccountingAccount
    FROM @accountingAccount AA
    LEFT JOIN tbProductAccountingAccount PAA WITH (NOLOCK)
    ON PAA.idProductAccountingAccount = AA.idProductAccountingAccount
    WHERE PAA.idProductAccountingAccount IS NULL
  )
  UPDATE AA2
  SET AA2.idProductAccountingAccount = PAA.idProductAccountingAccount
  FROM tbProductAccountingAccount PAA
  INNER JOIN accountingAssociateDB AADB
  ON AADB.idProductAccountingAccount = PAA.idProductAccountingAccount
  INNER JOIN accountingAssociate AA
  ON AA.rowNumAssociate = AADB.rowNum
  INNER JOIN @accountingAccount AA2
  ON AA2.rowNum = AA.rowNum;

  -- Actualizacion con los datos recibidos y ya con los Ids de la BD
  UPDATE PAA
  SET PAA.idAccountingAccount = AA.idAccountingAccount
  , PAA.effect = AA.effect
  , PAA.[percent] = AA.[percent]
  FROM tbProductAccountingAccount PAA
  INNER JOIN @accountingAccount AA
  ON AA.idProductAccountingAccount = PAA.idProductAccountingAccount;

  -- Preparar query
  SET @json = JSON_QUERY((
    SELECT @idProduct idProduct
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));

  SELECT JSON_QUERY(@json) json;
END
GO
-- BEGIN TRAN
--Antes
-- SELECT * FROM tbProductAccountingAccount WHERE idProduct = 34;
-- Probar el procedimiento corregido
DECLARE @json NVARCHAR(MAX) = N'{
  "idCompany": 1
  , "idProduct": 34
  , "accountingAccount": [
    {
      "idAccountingAccount": 5
      , "effect": 1
      , "percent": 100
      , "idProductAccountingAccount": 67
    },
    {
      "idAccountingAccount": 1
      , "effect": -1
      , "percent": 100
      , "idProductAccountingAccount": 68
    }
  ]
}';
-- EXEC spProductAccountingAccountEdit @json;
--Despues
-- SELECT * FROM tbProductAccountingAccount WHERE idProduct = 34;
-- Resetear el identity de las tablas antes de la prueba
-- DBCC CHECKIDENT (tbProductAccountingAccount, RESEED);
-- ROLLBACK TRAN

