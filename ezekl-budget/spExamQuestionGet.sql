CREATE OR ALTER PROCEDURE spExamQuestionGet
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  
  -- Extraer valores del JSON (manejo de JSON vacío)
  DECLARE @idLogin INT;
  DECLARE @search NVARCHAR(50);
  DECLARE @sort NVARCHAR(50);
  DECLARE @page INT;
  DECLARE @itemPerPage INT;
  DECLARE @idExam INT;
  DECLARE @idLanguage INT = 1;

  -- Inicializar con valores por defecto
  SET @search = '%';
  SET @sort = 'nameCompany_asc';
  SET @page = 1;
  SET @itemPerPage = 10;
  SET @idExam = 0;
  
  -- Sobrescribir con valores del JSON si existen
  IF @json != '{}' AND @json IS NOT NULL AND LEN(@json) > 2
  BEGIN
    SELECT @idLogin = idLogin,
      @search = '%' + ISNULL(search, '') + '%',
      @sort = ISNULL(sort, @sort),
      @page = ISNULL(page, @page),
      @itemPerPage = ISNULL(itemPerPage, @itemPerPage),
      @idExam = ISNULL(idExam, @idExam)
    FROM OPENJSON(@json) WITH (
      idLogin INT,
      search NVARCHAR(50),
      sort NVARCHAR(50),
      page INT,
      itemPerPage INT,
      idExam INT
    );
  END
  -- Query principal con CTE para paginación
  ; WITH Query AS (
    SELECT ROW_NUMBER() OVER (ORDER BY IIF(@sort = 'numberQuestion_asc', Q.numberQuestion, NULL)
      , IIF(@sort = 'numberQuestion_desc', Q.numberQuestion, NULL) DESC
    ) RowNum, EQ.idExamQuestion
    , Q.numberQuestion, Q.startPage, Q.endPage, Q.shortQuestion
    , Q.questionContext, Q.communityDiscussion, Q.correctAnswer
    , Q.explanation, Q.imageExplanation
    , CAST(CASE WHEN LEQ.idLoginExamQuestion IS NULL THEN 0 ELSE 1 END AS BIT) readed
    FROM tbExamQuestion EQ
    INNER JOIN tbQuestion Q
    ON Q.idQuestion = EQ.idQuestion
    AND EQ.idExam = @idExam
    INNER JOIN tbQuestionLanguage QL
    ON QL.idQuestion = Q.idQuestion
    AND QL.idLanguage = @idLanguage
    LEFT JOIN tbLoginExamQuestion LEQ
    ON LEQ.idExamQuestion = EQ.idExamQuestion
    AND LEQ.idLogin = @idLogin
    WHERE (Q.shortQuestion LIKE @search OR Q.shortQuestion LIKE @search)
  )
  SELECT @json = JSON_QUERY((
    SELECT 
      (SELECT COUNT(*) FROM Query) total,
      JSON_QUERY(ISNULL((
        SELECT Q.idExamQuestion, Q.numberQuestion
        , Q.startPage, Q.endPage, Q.shortQuestion
        , Q.questionContext, Q.communityDiscussion
        , Q.correctAnswer, Q.explanation, Q.imageExplanation
        , Q.readed
        FROM Query Q
        WHERE Q.RowNum BETWEEN (@page - 1) * @itemPerPage + 1 AND @page * @itemPerPage
        FOR JSON PATH
      ), '[]')) data
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
  ));
  
  -- Retornar resultado
  SELECT JSON_QUERY(@json) json;
END
GO

-- Ejemplos de uso:
EXEC spExamQuestionGet @json = N'{
  "idLogin": 1,
  "search": null,
  "sort": "nameCompany_asc",
  "page": 1,
  "itemPerPage": 10,
  "idExam": 1
}';