CREATE OR ALTER PROCEDURE spProductMediaFileDel
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  DECLARE @idProduct INT = JSON_VALUE(@json, '$.idProduct');
  DECLARE @idCompany INT = JSON_VALUE(@json, '$.idCompany');
  DECLARE @idMediaFileList NVARCHAR(MAX) = JSON_QUERY(@json, '$.idMediaFiles');

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

  -- Tabla temporal para almacenar paths de archivos a eliminar
  CREATE TABLE #FilesToDelete (
    idMediaFile INT,
    idProductMediaFile INT,
    pathMediaFile NVARCHAR(500)
  );

  -- Obtener información de los archivos antes de eliminar
  INSERT INTO #FilesToDelete (idMediaFile, idProductMediaFile, pathMediaFile)
  SELECT 
    pm.idMediaFile,
    pm.idProductMediaFile,
    mf.pathMediaFile
  FROM tbProductMediaFile pm
  INNER JOIN tbMediaFile mf ON pm.idMediaFile = mf.idMediaFile
  INNER JOIN OPENJSON(@idMediaFileList) WITH (idMediaFile INT '$') ids
    ON pm.idMediaFile = ids.idMediaFile
  WHERE pm.idProduct = @idProduct;

  -- Eliminar relaciones ProductMediaFile
  DELETE pm
  FROM tbProductMediaFile pm
  INNER JOIN #FilesToDelete ftd ON pm.idProductMediaFile = ftd.idProductMediaFile;

  -- Verificar si los mediaFiles ya no están siendo usados por otros productos
  -- y eliminarlos (cascada eliminará CompanyMediaFile)
  DELETE mf
  FROM tbMediaFile mf
  INNER JOIN #FilesToDelete ftd ON mf.idMediaFile = ftd.idMediaFile
  WHERE NOT EXISTS (
    SELECT 1 
    FROM tbProductMediaFile pm 
    WHERE pm.idMediaFile = ftd.idMediaFile
  );

  -- Preparar respuesta con paths para eliminar del servidor
  SET @json = JSON_QUERY((
    SELECT (
      SELECT 
        idMediaFile,
        idProductMediaFile,
        pathMediaFile
      FROM #FilesToDelete
      FOR JSON PATH
    ) AS mediaFiles
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));

  DROP TABLE #FilesToDelete;
  
  SELECT JSON_QUERY(@json) json;
END
GO
EXEC spProductMediaFileDel @json = N'{
  "idCompany": 1
  , "idProduct": 1
  , "idMediaFiles": [1, 2]
}';
