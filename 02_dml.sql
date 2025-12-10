-- =====================================================
-- SCRIPT DML: DADOS DE TESTE (SEED) - CORRIGIDO (COM N PREFIX)
-- =====================================================

USE [p3g4]; -- Ou o nome da tua BD
GO

-- 1. CRIAR OS JOGOS
INSERT INTO Jogo (nome, descricao) VALUES
(N'Blackjack', N'O clássico 21. Tenta bater o dealer sem rebentar.'),
(N'Banca Francesa', N'Jogo de dados tradicional português. Apostas na sorte.');
GO

-- 2. CRIAR O DEALER
INSERT INTO Dealer (nome) VALUES
(N'Bot Dealer 3000');
GO

-- 3. CRIAR MESAS
DECLARE @idBlackjack INT = (SELECT id FROM Jogo WHERE nome = N'Blackjack');
DECLARE @idBanca     INT = (SELECT id FROM Jogo WHERE nome = N'Banca Francesa');
DECLARE @idDealer    INT = (SELECT id FROM Dealer WHERE nome = N'Bot Dealer 3000');

INSERT INTO Mesa (jogo_id, dealer_id, apostaMin, apostaMax) VALUES
(@idBlackjack, @idDealer, 5.00, 100.00),
(@idBlackjack, @idDealer, 50.00, 1000.00),
(@idBanca,     @idDealer, 2.00, 500.00);
GO

-- 4. CRIAR JOGADORES DE TESTE
INSERT INTO Jogador (nome, cc, dataRegisto, dataNascimento, email, saldo, password, estadoVerificacao) VALUES
(N'João Apostador', N'12345678', GETDATE(), '1990-05-20', N'joao@teste.com', 0.00, N'pass123', 1),
(N'Ana Sorte',      N'87654321', GETDATE(), '1995-08-15', N'ana@teste.com',  0.00, N'pass123', 1);
GO

-- 5. SIMULAR DEPÓSITOS
DECLARE @idJoao INT = (SELECT id FROM Jogador WHERE email = N'joao@teste.com');
DECLARE @idAna  INT = (SELECT id FROM Jogador WHERE email = N'ana@teste.com');

INSERT INTO Transacao (jogador_id, valor, tipoDeTransacao, sucesso) VALUES (@idJoao, 500.00, N'Deposito', 1);
UPDATE Jogador SET saldo = 500.00 WHERE id = @idJoao;

INSERT INTO Transacao (jogador_id, valor, tipoDeTransacao, sucesso) VALUES (@idAna, 1000.00, N'Deposito', 1);
UPDATE Jogador SET saldo = 1000.00 WHERE id = @idAna;
GO

-- 6. SIMULAR SESSÃO ANTIGA
DECLARE @idJoaoSessao INT = (SELECT id FROM Jogador WHERE email = N'joao@teste.com');
DECLARE @idMesaBJ INT = (SELECT TOP 1 id FROM Mesa WHERE jogo_id = (SELECT id FROM Jogo WHERE nome = N'Blackjack'));

INSERT INTO SessaoDeJogo (mesa_id, jogador_id, numPartidas, dataInicio, dataFim) VALUES
(@idMesaBJ, @idJoaoSessao, 1, DATEADD(day, -1, GETDATE()), DATEADD(day, -1, GETDATE()));

DECLARE @idSessao INT = (SELECT TOP 1 id FROM SessaoDeJogo WHERE jogador_id = @idJoaoSessao);
INSERT INTO Aposta (sessaoJogo_id, valor, resultado, lucro) VALUES
(@idSessao, 50.00, N'Vitoria', 50.00);

UPDATE Jogador SET saldo = saldo + 50.00 WHERE id = @idJoaoSessao;
GO