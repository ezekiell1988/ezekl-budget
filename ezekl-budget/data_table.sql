/********************************************************************
    Script: table_details_mssql.sql
    Descripción: Obtiene el detalle completo de una tabla en MSSQL:
                 columnas, tipos de datos, claves primarias, 
                 foráneas, índices y constraints.
    Autor: ChatGPT (GPT-5)
********************************************************************/

DECLARE @TableName SYSNAME = 'tbLoginMicrosoft';
-- 🔧 Cambiar por el nombre de la tabla
DECLARE @SchemaName SYSNAME = 'dbo';
-- 🔧 Cambiar si tu esquema es distinto

/* ===============================================================
   1️⃣  COLUMNAS Y TIPOS DE DATOS
   =============================================================== */
--COLUMNAS
SELECT
    c.COLUMN_NAME,
    c.DATA_TYPE,
    c.CHARACTER_MAXIMUM_LENGTH,
    c.NUMERIC_PRECISION,
    c.NUMERIC_SCALE,
    c.IS_NULLABLE,
    c.COLUMN_DEFAULT,
    COLUMNPROPERTY(OBJECT_ID(c.TABLE_SCHEMA + '.' + c.TABLE_NAME), c.COLUMN_NAME, 'IsIdentity') AS IsIdentity
FROM INFORMATION_SCHEMA.COLUMNS c
WHERE c.TABLE_NAME = @TableName
    AND c.TABLE_SCHEMA = @SchemaName
ORDER BY c.ORDINAL_POSITION;


/* ===============================================================
   2️⃣  CLAVES PRIMARIAS
   =============================================================== */
--CLAVE
SELECT
    kc.CONSTRAINT_NAME,
    kc.COLUMN_NAME
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
    JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kc
    ON kc.CONSTRAINT_NAME = tc.CONSTRAINT_NAME
WHERE tc.TABLE_NAME = @TableName
    AND tc.TABLE_SCHEMA = @SchemaName
    AND tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
ORDER BY kc.ORDINAL_POSITION;


/* ===============================================================
   3️⃣  CLAVES FORÁNEAS (RELACIONES)
   =============================================================== */
--CLAVES
SELECT
    fk.CONSTRAINT_NAME AS ForeignKey,
    fkcu.COLUMN_NAME AS ColumnName,
    pkcu.TABLE_SCHEMA AS ReferencedSchema,
    pkcu.TABLE_NAME AS ReferencedTable,
    pkcu.COLUMN_NAME AS ReferencedColumn
FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc
    INNER JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS fk
    ON rc.CONSTRAINT_NAME = fk.CONSTRAINT_NAME
    INNER JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS pk
    ON rc.UNIQUE_CONSTRAINT_NAME = pk.CONSTRAINT_NAME
    INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE fkcu
    ON fk.CONSTRAINT_NAME = fkcu.CONSTRAINT_NAME
    INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE pkcu
    ON pk.CONSTRAINT_NAME = pkcu.CONSTRAINT_NAME
        AND fkcu.ORDINAL_POSITION = pkcu.ORDINAL_POSITION
WHERE fk.TABLE_NAME = @TableName
    AND fk.TABLE_SCHEMA = @SchemaName;


/* ===============================================================
   4️⃣  ÍNDICES
   =============================================================== */
--ÍNDICES
SELECT
    i.name AS IndexName,
    i.type_desc AS IndexType,
    col.name AS ColumnName,
    ic.key_ordinal AS KeyOrdinal,
    i.is_unique AS IsUnique,
    i.is_primary_key AS IsPrimaryKey
FROM sys.indexes i
    INNER JOIN sys.index_columns ic
    ON i.object_id = ic.object_id AND i.index_id = ic.index_id
    INNER JOIN sys.columns col
    ON ic.object_id = col.object_id AND ic.column_id = col.column_id
    INNER JOIN sys.tables t
    ON i.object_id = t.object_id
    INNER JOIN sys.schemas s
    ON t.schema_id = s.schema_id
WHERE t.name = @TableName
    AND s.name = @SchemaName
ORDER BY i.name, ic.key_ordinal;


/* ===============================================================
   5️⃣  CONSTRAINTS ADICIONALES (UNIQUE, CHECK, DEFAULT)
   =============================================================== */
--CONSTRAINTS
SELECT
    tc.CONSTRAINT_NAME,
    tc.CONSTRAINT_TYPE,
    kcu.COLUMN_NAME
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
    LEFT JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
    ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
WHERE tc.TABLE_NAME = @TableName
    AND tc.TABLE_SCHEMA = @SchemaName
ORDER BY tc.CONSTRAINT_TYPE;