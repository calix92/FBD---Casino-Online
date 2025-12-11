-- =====================================================
-- SCRIPT INDEXES: OTIMIZAÇÃO DE PERFORMANCE
-- Executar no fim de tudo
-- =====================================================
USE [p3g4];
GO

-- 1. Índice para acelerar o LOGIN
-- Como pesquisamos muito por 'email', este índice torna o login instantâneo
-- mesmo que tenhas 1 milhão de jogadores.
CREATE NONCLUSTERED INDEX idx_Jogador_Email
ON Jogador(email);
GO

-- 2. Índice para acelerar RELATÓRIOS POR DATA
-- Útil se o professor pedir "quanto lucrámos em Dezembro?"
CREATE NONCLUSTERED INDEX idx_Aposta_Data
ON Aposta(dataAposta);
GO

-- 3. Índice para encontrar sessões de um jogador rapidamente
CREATE NONCLUSTERED INDEX idx_Sessao_Jogador
ON SessaoDeJogo(jogador_id);
GO