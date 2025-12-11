-- =====================================================
-- SCRIPT UDF: FUNÇÕES DE UTILIZADOR (CORRIGIDO)
-- =====================================================
USE [p3g4];
GO

-- 1. Se a função já existir, apaga-a primeiro
DROP FUNCTION IF EXISTS dbo.udf_CalcularLucroTotal;
GO

-- 2. Criar a função de novo
CREATE FUNCTION dbo.udf_CalcularLucroTotal (@jogador_id INT)
RETURNS DECIMAL(10,2)
AS
BEGIN
    DECLARE @total DECIMAL(10,2); -- Ponto e vírgula aqui!

    -- Soma o lucro de todas as apostas feitas em sessões desse jogador
    SELECT @total = SUM(a.lucro)
    FROM Aposta a
    INNER JOIN SessaoDeJogo s ON a.sessaoJogo_id = s.id
    WHERE s.jogador_id = @jogador_id;

    -- Se não tiver apostas, devolve 0 em vez de NULL
    RETURN ISNULL(@total, 0.00);
END;
GO