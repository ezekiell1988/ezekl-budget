CREATE OR ALTER VIEW vwAccountingAccountMoves AS
  SELECT M.idMonth, M.codeMonth, AA.idAccountingAccount, AA.nameAccountingAccount
  , DP.idProduct, DP.nameProduct, DPAA.effect * DPAA.amount amount
  FROM tbDocumentProductAccountingAccount DPAA
  INNER JOIN tbAccountingAccount AA
  ON AA.idAccountingAccount = DPAA.idAccountingAccount
  INNER JOIN tbDocumentProduct DP
  ON DP.idDocumentProduct = DPAA.idDocumentProduct
  INNER JOIN tbMonthDocument MD
  ON MD.idDocument = DP.idDocument
  INNER JOIN  tbMonth M
  ON M.idMonth = MD.idMonth;
GO

SELECT * FROM vwAccountingAccountMoves;