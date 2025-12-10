-- =====================================================
-- 00_RESET_DB.SQL (Apagar tudo para recomeçar)
-- =====================================================
USE [p3g4]; -- Confirma se é a tua BD
GO

-- 1. Apagar tabelas dependentes ("Filhas")
IF OBJECT_ID('dbo.Aposta', 'U') IS NOT NULL DROP TABLE dbo.Aposta;
IF OBJECT_ID('dbo.HistoricoPagamento', 'U') IS NOT NULL DROP TABLE dbo.HistoricoPagamento;
IF OBJECT_ID('dbo.RegistoLogin', 'U') IS NOT NULL DROP TABLE dbo.RegistoLogin;
IF OBJECT_ID('dbo.SessaoDeJogo', 'U') IS NOT NULL DROP TABLE dbo.SessaoDeJogo;

-- 2. Apagar tabelas intermédias
IF OBJECT_ID('dbo.Transacao', 'U') IS NOT NULL DROP TABLE dbo.Transacao;
IF OBJECT_ID('dbo.Mesa', 'U') IS NOT NULL DROP TABLE dbo.Mesa;

-- 3. Apagar tabelas principais ("Mães")
IF OBJECT_ID('dbo.Dealer', 'U') IS NOT NULL DROP TABLE dbo.Dealer;
IF OBJECT_ID('dbo.Jogo', 'U') IS NOT NULL DROP TABLE dbo.Jogo;
IF OBJECT_ID('dbo.Jogador', 'U') IS NOT NULL DROP TABLE dbo.Jogador;
GO