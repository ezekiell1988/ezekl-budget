CREATE OR ALTER VIEW vwAccountingAccountTotal AS
  SELECT AA.idAccountingAccount, AA.nameAccountingAccount, DAA.effect * DAA.amount amount
  FROM tbDocumentAccountingAccount DAA
  INNER JOIN tbAccountingAccount AA
  ON AA.idAccountingAccount = DAA.idAccountingAccount;
GO

SELECT * FROM vwAccountingAccountTotal;