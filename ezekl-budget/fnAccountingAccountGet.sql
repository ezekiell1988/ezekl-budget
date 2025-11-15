-- Función auxiliar para verificar si tiene hijos que cumplen el filtro
CREATE OR ALTER FUNCTION fnHasMatchingChildren(
  @idAccountingAccount INT,
  @search NVARCHAR(50),
  @includeInactive BIT
)
RETURNS BIT
AS
BEGIN
  DECLARE @hasMatch BIT = 0;
  
  -- Verificar si algún hijo directo cumple el filtro
  IF EXISTS (
    SELECT 1 FROM tbAccountingAccount
    WHERE idAccountingAccountFather = @idAccountingAccount
      AND (@includeInactive = 1 OR active = 1)
      AND (nameAccountingAccount LIKE @search OR codeAccountingAccount LIKE @search)
  )
  BEGIN
    SET @hasMatch = 1;
  END
  ELSE
  BEGIN
    -- Verificar recursivamente en nietos
    DECLARE @childId INT;
    DECLARE child_cursor CURSOR FOR
      SELECT idAccountingAccount FROM tbAccountingAccount
      WHERE idAccountingAccountFather = @idAccountingAccount
        AND (@includeInactive = 1 OR active = 1);
    
    OPEN child_cursor;
    FETCH NEXT FROM child_cursor INTO @childId;
    
    WHILE @@FETCH_STATUS = 0 AND @hasMatch = 0
    BEGIN
      IF dbo.fnHasMatchingChildren(@childId, @search, @includeInactive) = 1
        SET @hasMatch = 1;
      
      FETCH NEXT FROM child_cursor INTO @childId;
    END
    
    CLOSE child_cursor;
    DEALLOCATE child_cursor;
  END
  
  RETURN @hasMatch;
END
GO

-- Función para obtener el path completo de una cuenta contable con filtros
CREATE OR ALTER FUNCTION fnAccountingAccountGet(@json NVARCHAR(MAX))
RETURNS NVARCHAR(MAX)
AS
BEGIN
  -- Extraer valores del JSON para filtros
  DECLARE @search NVARCHAR(50);
  DECLARE @includeInactive BIT;
  DECLARE @idAccountingAccountFather INT;

  -- Inicializar con valores por defecto
  SET @search = '%';
  SET @includeInactive = 0;
  SET @idAccountingAccountFather = JSON_VALUE(@json, '$.idAccountingAccountFather');
  SET @includeInactive = ISNULL(JSON_VALUE(@json, '$.includeInactive'), @includeInactive);

  -- Sobrescribir con valores del JSON si existen
  IF @json != '{}' AND @json IS NOT NULL AND LEN(@json) > 2
  BEGIN
    DECLARE @searchParam NVARCHAR(50) = JSON_VALUE(@json, '$.search');
    IF @searchParam IS NOT NULL AND @searchParam != ''
      SET @search = '%' + @searchParam + '%';

  END

  -- Preparar query con filtros aplicados
  SET @json = JSON_QUERY((
    SELECT AA.idAccountingAccount
    , AA.idAccountingAccountFather
    , AA.codeAccountingAccount
    , AA.nameAccountingAccount
    , AA.active
    , JSON_QUERY(dbo.fnAccountingAccountGet((
      SELECT 
        AA.idAccountingAccount idAccountingAccountFather,
        JSON_VALUE(@json, '$.search') search,
        @includeInactive includeInactive
      FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
    ))) children
    FROM tbAccountingAccount AA
    WHERE AA.idAccountingAccountFather = @idAccountingAccountFather
      AND (@includeInactive = 1 OR AA.active = 1)
      AND (
        -- Incluir si no hay filtro específico
        (@search = '%%')
        OR
        -- Incluir si el nodo actual cumple el filtro
        (AA.nameAccountingAccount LIKE @search OR AA.codeAccountingAccount LIKE @search)
        OR
        -- Incluir si tiene hijos que cumplen el filtro
        dbo.fnHasMatchingChildren(AA.idAccountingAccount, @search, @includeInactive) = 1
      )
    FOR JSON PATH
  ));
  
  RETURN @json;
END
GO

-- Ejemplos de uso:
-- Obtener hijos sin filtro
-- SELECT dbo.fnAccountingAccountGet('{"idAccountingAccountFather": 1, "search":"General 3"}') AS AccountPath;