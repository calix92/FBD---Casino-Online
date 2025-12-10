-- =====================================================
-- SCRIPT DE RESET (APAGAR TUDO)
-- Executar isto antes de criar as tabelas novamente
-- =====================================================

-- 1. Apagar tabelas que dependem de outras (As "Filhas")
-- Usamos "IF EXISTS" para não dar erro se a tabela já não existir

IF OBJECT_ID('dbo.Aposta', 'U') IS NOT NULL DROP TABLE dbo.Aposta;
IF OBJECT_ID('dbo.HistoricoPagamento', 'U') IS NOT NULL DROP TABLE dbo.HistoricoPagamento;
IF OBJECT_ID('dbo.RegistoLogin', 'U') IS NOT NULL DROP TABLE dbo.RegistoLogin;

-- 2. Apagar tabelas intermédias
IF OBJECT_ID('dbo.SessaoDeJogo', 'U') IS NOT NULL DROP TABLE dbo.SessaoDeJogo;
IF OBJECT_ID('dbo.Joga', 'U') IS NOT NULL DROP TABLE dbo.Joga; -- Limpeza da versão antiga
IF OBJECT_ID('dbo.Transacao', 'U') IS NOT NULL DROP TABLE dbo.Transacao;
IF OBJECT_ID('dbo.Mesa', 'U') IS NOT NULL DROP TABLE dbo.Mesa;

-- 3. Apagar tabelas principais (As "Mães")
IF OBJECT_ID('dbo.Dealer', 'U') IS NOT NULL DROP TABLE dbo.Dealer;
IF OBJECT_ID('dbo.Jogo', 'U') IS NOT NULL DROP TABLE dbo.Jogo;
IF OBJECT_ID('dbo.Jogador', 'U') IS NOT NULL DROP TABLE dbo.Jogador;

GO