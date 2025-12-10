-- =====================================================
-- SCRIPT TRIGGERS: SEGURANÇA (CORRIGIDO)
-- =====================================================
USE [p3g4];
GO

CREATE OR ALTER TRIGGER trg_SegurancaSaldo
ON Jogador
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON; -- Ponto e vírgula ADICIONADO AQUI

    -- Verifica se, após a atualização, alguém ficou com saldo menor que 0
    IF EXISTS (SELECT 1 FROM Inserted WHERE saldo < 0)
    BEGIN
        RAISERROR ('ERRO CRÍTICO: Operação cancelada. O jogador não tem saldo suficiente.', 16, 1);
        ROLLBACK TRANSACTION;
    END
END
GO