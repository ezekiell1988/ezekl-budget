CREATE OR ALTER PROCEDURE spMediaFileGet
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  
  -- Extraer valores del JSON (manejo de JSON vacío)
  DECLARE @idCompany INT;
  DECLARE @search NVARCHAR(50);
  DECLARE @sort NVARCHAR(50);
  DECLARE @page INT;
  DECLARE @itemPerPage INT;
  DECLARE @mediaType NVARCHAR(20);
  
  -- Inicializar con valores por defecto
  SET @search = '%';
  SET @sort = 'createAt_desc';
  SET @page = 1;
  SET @itemPerPage = 10;
  SET @mediaType = NULL;
  
  -- Sobrescribir con valores del JSON si existen
  IF @json != '{}' AND @json IS NOT NULL AND LEN(@json) > 2
  BEGIN
    SELECT 
      @idCompany = idCompany,
      @search = '%' + ISNULL(search, '') + '%',
      @sort = ISNULL(sort, @sort),
      @page = ISNULL(page, @page),
      @itemPerPage = ISNULL(itemPerPage, @itemPerPage),
      @mediaType = mediaType
    FROM OPENJSON(@json) WITH (
      idCompany INT,
      search NVARCHAR(50),
      sort NVARCHAR(50),
      page INT,
      itemPerPage INT,
      mediaType NVARCHAR(20)
    );
  END

  -- Validar que idCompany es requerido
  IF @idCompany IS NULL
  BEGIN
    RAISERROR(N'Error: idCompany es requerido', 16, 1);
    RETURN;
  END

  -- Query principal con CTE para paginación
  ; WITH MediaFileQuery AS (
    SELECT 
      ROW_NUMBER() OVER (
        ORDER BY 
          IIF(@sort = 'idMediaFile_asc', MF.idMediaFile, NULL),
          IIF(@sort = 'idMediaFile_desc', MF.idMediaFile, NULL) DESC,
          IIF(@sort = 'nameMediaFile_asc', MF.nameMediaFile, NULL),
          IIF(@sort = 'nameMediaFile_desc', MF.nameMediaFile, NULL) DESC,
          IIF(@sort = 'createAt_asc', MF.createAt, NULL),
          IIF(@sort = 'createAt_desc', MF.createAt, NULL) DESC,
          MF.createAt DESC
      ) RowNum,
      MF.idMediaFile,
      MF.nameMediaFile,
      MF.pathMediaFile,
      MF.sizeMediaFile,
      MF.mimetype,
      MF.mediaType,
      MF.createAt
    FROM tbMediaFile MF
    INNER JOIN tbCompanyMediaFile CMF ON MF.idMediaFile = CMF.idMediaFile
    WHERE CMF.idCompany = @idCompany
      AND (MF.nameMediaFile LIKE @search OR MF.mimetype LIKE @search)
      AND (@mediaType IS NULL OR MF.mediaType = @mediaType)
  )
  SELECT @json = JSON_QUERY((
    SELECT 
      (SELECT COUNT(*) FROM MediaFileQuery) total,
      JSON_QUERY(ISNULL((
        SELECT 
          MFQ.idMediaFile,
          MFQ.nameMediaFile,
          MFQ.pathMediaFile,
          MFQ.sizeMediaFile,
          MFQ.mimetype,
          MFQ.mediaType,
          MFQ.createAt
        FROM MediaFileQuery MFQ
        WHERE MFQ.RowNum BETWEEN (@page - 1) * @itemPerPage + 1 AND @page * @itemPerPage
        FOR JSON PATH
      ), '[]')) data
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));
  
  -- Retornar resultado
  SELECT JSON_QUERY(@json) json;
END
GO

-- Ejemplos de uso:

-- Obtener todos los archivos multimedia de una compañía (JSON mínimo)
EXEC spMediaFileGet @json = N'{"idCompany": 1}';

/*
-- Buscar archivos específicos
EXEC spMediaFileGet @json = N'{
  "idCompany": 1,
  "search": "jpg",
  "sort": "nameMediaFile_asc",
  "page": 1,
  "itemPerPage": 10
}';

-- Filtrar por tipo de medio
EXEC spMediaFileGet @json = N'{
  "idCompany": 1,
  "mediaType": "image",
  "page": 1,
  "itemPerPage": 20
}';

-- Obtener todos con paginación específica
EXEC spMediaFileGet @json = N'{
  "idCompany": 1,
  "page": 2,
  "itemPerPage": 5
}';
*/