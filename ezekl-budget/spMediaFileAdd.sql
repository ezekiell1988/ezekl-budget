CREATE OR ALTER PROCEDURE spMediaFileAdd
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  DECLARE @idCompany INT = JSON_VALUE(@json, '$.idCompany');
  DECLARE @nameMediaFile NVARCHAR(200) = FORMAT(GETDATE(), 'yyyyMMddHHmmSS') + '.' + JSON_VALUE(@json, '$.extension');
  DECLARE @pathMediaFile NVARCHAR(500) = 'uploads/';
  DECLARE @sizeMediaFile BIGINT = JSON_VALUE(@json, '$.sizeMediaFile');
  DECLARE @mimetype VARCHAR(100) = JSON_VALUE(@json, '$.mimetype');
  DECLARE @mediaType VARCHAR(50) = JSON_VALUE(@json, '$.mediaType');
  DECLARE @idMediaFile INT;

  -- Crear producto
  INSERT INTO tbMediaFile (
    nameMediaFile, pathMediaFile, sizeMediaFile, mimetype, mediaType
  ) VALUES (
    @nameMediaFile, @pathMediaFile
    , @sizeMediaFile, @mimetype, @mediaType
  );

  -- idMediaFile
  SET @idMediaFile = SCOPE_IDENTITY();

  -- Actualizar nombre y path
  SET @nameMediaFile = CAST(@idMediaFile AS VARCHAR) + '_' + @nameMediaFile;
  SET @pathMediaFile = @pathMediaFile
    + CASE WHEN RIGHT(@pathMediaFile, 1) != '/' THEN '/' ELSE '' END
    + @nameMediaFile
  ;
  UPDATE tbMediaFile
  SET nameMediaFile = @nameMediaFile
  , pathMediaFile = @pathMediaFile
  WHERE idMediaFile = @idMediaFile;

  -- Crear company
  INSERT INTO tbCompanyMediaFile (idCompany, idMediaFile)
  VALUES (@idCompany, @idMediaFile);

  -- Preparar query
  SET @json = JSON_QUERY((
    SELECT @idMediaFile idMediaFile
    , @nameMediaFile nameMediaFile
    , @pathMediaFile pathMediaFile
    , 'https://img.ezekl.com/' + @nameMediaFile urlMediaFile
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));
  
  SELECT JSON_QUERY(@json) json;
END
GO
EXEC spMediaFileAdd @json = N'{
  "idCompany": 1
  , "sizeMediaFile": "2048576"
  , "mimetype": "image/jpeg"
  , "mediaType": "image"
  , "extension": "jpg"
}';

EXEC spTruncateTable @table = 'dbo.tbMediaFile';