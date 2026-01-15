CREATE OR ALTER PROCEDURE spProductMediaFileAdd
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  DECLARE @idCompany INT = JSON_VALUE(@json, '$.idCompany');
  DECLARE @idProduct INT = JSON_VALUE(@json, '$.idProduct');
  DECLARE @idMediaFile INT;
  DECLARE @idProductMediaFile INT;
  DECLARE @mediaFileJson NVARCHAR(MAX);
  DECLARE @resultJson NVARCHAR(MAX);
  DECLARE @currentPriority INT;

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

  -- Obtener la última prioridad del producto
  SELECT @currentPriority = ISNULL(MAX(priority), 0)
  FROM tbProductMediaFile
  WHERE idProduct = @idProduct;

  -- Tabla temporal para almacenar resultados
  CREATE TABLE #Results (
    orderIndex INT,
    idProductMediaFile INT,
    idMediaFile INT,
    nameMediaFile NVARCHAR(200),
    pathMediaFile NVARCHAR(500),
    urlMediaFile NVARCHAR(600)
  );

  -- Iterar sobre cada mediaFile en el array
  DECLARE mediaCursor CURSOR FOR
  SELECT value
  FROM OPENJSON(@json, '$.mediaFiles');

  OPEN mediaCursor;
  FETCH NEXT FROM mediaCursor INTO @mediaFileJson;

  WHILE @@FETCH_STATUS = 0
  BEGIN
    -- Agregar idCompany al JSON del mediaFile
    SET @mediaFileJson = JSON_MODIFY(@mediaFileJson, '$.idCompany', @idCompany);

    -- Llamar a spMediaFileAdd para crear el archivo
    DECLARE @mediaResult TABLE (json NVARCHAR(MAX));
    INSERT INTO @mediaResult
    EXEC spMediaFileAdd @json = @mediaFileJson;

    -- Extraer el idMediaFile del resultado
    SELECT @resultJson = json FROM @mediaResult;
    SET @idMediaFile = JSON_VALUE(@resultJson, '$.idMediaFile');

    -- Incrementar prioridad para este registro
    SET @currentPriority = @currentPriority + 1;

    -- Crear relación ProductMediaFile con prioridad
    INSERT INTO tbProductMediaFile (idProduct, idMediaFile, priority)
    VALUES (@idProduct, @idMediaFile, @currentPriority);

    SET @idProductMediaFile = SCOPE_IDENTITY();

    -- Guardar resultado con orden
    INSERT INTO #Results (orderIndex, idProductMediaFile, idMediaFile, nameMediaFile, pathMediaFile, urlMediaFile)
    SELECT 
      @currentPriority,
      @idProductMediaFile,
      JSON_VALUE(@resultJson, '$.idMediaFile'),
      JSON_VALUE(@resultJson, '$.nameMediaFile'),
      JSON_VALUE(@resultJson, '$.pathMediaFile'),
      JSON_VALUE(@resultJson, '$.urlMediaFile');

    -- Limpiar tabla temporal para siguiente iteración
    DELETE FROM @mediaResult;

    FETCH NEXT FROM mediaCursor INTO @mediaFileJson;
  END;

  CLOSE mediaCursor;
  DEALLOCATE mediaCursor;

  -- Preparar respuesta JSON con todos los mediaFiles creados
  SET @json = JSON_QUERY((
    SELECT @idProductMediaFile idProductMediaFile
    , (
      SELECT 
        idProductMediaFile,
        idMediaFile,
        nameMediaFile,
        pathMediaFile,
        urlMediaFile
      FROM #Results
      ORDER BY orderIndex
      FOR JSON PATH
    ) AS mediaFiles
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));

  DROP TABLE #Results;
  
  SELECT JSON_QUERY(@json) json;
END
GO
EXEC spProductMediaFileAdd @json = N'{
  "idCompany": 1
  , "idProduct": 1
  , "mediaFiles": [
    {
      "sizeMediaFile": "2048576"
      , "mimetype": "image/jpeg"
      , "mediaType": "image"
      , "extension": "jpg"
    },
    {
      "sizeMediaFile": "2048576"
      , "mimetype": "image/jpeg"
      , "mediaType": "image"
      , "extension": "jpg"
    }
  ]
}';

EXEC spTruncateTable @table = 'dbo.tbProductMediaFile';
EXEC spTruncateTable @table = 'dbo.tbCompanyMediaFile';
EXEC spTruncateTable @table = 'dbo.tbMediaFile';