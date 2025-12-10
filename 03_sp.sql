-- =====================================================
-- SCRIPT SP: STORED PROCEDURES (CORRIGIDO)
-- Executar APÓS ter os dados (DML)
-- =====================================================
USE [p3g4]; -- Confirma o nome da BD
GO

-- -----------------------------------------------------
-- 1. REGISTAR NOVO JOGADOR
-- -----------------------------------------------------
CREATE OR ALTER PROCEDURE sp_RegistarJogador
    @nome           NVARCHAR(100),
    @cc             NVARCHAR(20),
    @dataNascimento DATE,
    @email          NVARCHAR(100),
    @password       NVARCHAR(255)
AS
BEGIN
    SET NOCOUNT ON; -- Ponto e vírgula adicionado

    -- Verificar se email já existe
    IF EXISTS (SELECT 1 FROM Jogador WHERE email = @email)
    BEGIN
        SELECT 'Erro' as Status, 'Email já registado.' as Mensagem;
        RETURN;
    END

    -- Verificar se CC já existe
    IF EXISTS (SELECT 1 FROM Jogador WHERE cc = @cc)
    BEGIN
        SELECT 'Erro' as Status, 'CC já registado.' as Mensagem;
        RETURN;
    END

    INSERT INTO Jogador (nome, cc, dataRegisto, dataNascimento, email, password, saldo, estadoVerificacao)
    VALUES (@nome, @cc, GETDATE(), @dataNascimento, @email, @password, 0.00, 1);

    SELECT 'Sucesso' as Status, 'Jogador criado com sucesso!' as Mensagem;
END
GO

-- -----------------------------------------------------
-- 2. LOGIN
-- -----------------------------------------------------
CREATE OR ALTER PROCEDURE sp_Login
    @email    NVARCHAR(100),
    @password NVARCHAR(255),
    @ip       NVARCHAR(45)
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @jogador_id INT;

    -- Tenta encontrar o jogador
    SELECT @jogador_id = id
    FROM Jogador
    WHERE email = @email AND password = @password;

    IF @jogador_id IS NOT NULL
    BEGIN
        -- Login Válido: Guarda no histórico e devolve dados
        INSERT INTO RegistoLogin (jogador_id, enderecoIp, sucesso) VALUES (@jogador_id, @ip, 1);

        SELECT id, nome, saldo, 'Sucesso' as Status FROM Jogador WHERE id = @jogador_id;
    END
    ELSE
    BEGIN
        -- Login Inválido
        DECLARE @id_tentativa INT = (SELECT id FROM Jogador WHERE email = @email);
        IF @id_tentativa IS NOT NULL
            INSERT INTO RegistoLogin (jogador_id, enderecoIp, sucesso) VALUES (@id_tentativa, @ip, 0);

        SELECT NULL as id, NULL as nome, NULL as saldo, 'Erro' as Status;
    END
END
GO

-- -----------------------------------------------------
-- 3. INICIAR SESSÃO
-- -----------------------------------------------------
CREATE OR ALTER PROCEDURE sp_IniciarSessao
    @jogador_id INT,
    @mesa_id    INT
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO SessaoDeJogo (mesa_id, jogador_id, numPartidas, dataInicio)
    VALUES (@mesa_id, @jogador_id, 0, GETDATE());

    SELECT SCOPE_IDENTITY() AS sessao_id;
END
GO

-- -----------------------------------------------------
-- 4. REGISTAR APOSTA
-- -----------------------------------------------------
CREATE OR ALTER PROCEDURE sp_RegistarAposta
    @sessao_id INT,
    @valor     DECIMAL(10,2),
    @resultado NVARCHAR(50),
    @lucro     DECIMAL(10,2)
AS
BEGIN
    SET NOCOUNT ON;

    -- 1. Guardar a aposta
    INSERT INTO Aposta (sessaoJogo_id, valor, resultado, lucro, dataAposta)
    VALUES (@sessao_id, @valor, @resultado, @lucro, GETDATE());

    -- 2. Atualizar contador de partidas
    UPDATE SessaoDeJogo
    SET numPartidas = numPartidas + 1
    WHERE id = @sessao_id;

    -- 3. Atualizar o saldo do Jogador
    DECLARE @jogador_id INT = (SELECT jogador_id FROM SessaoDeJogo WHERE id = @sessao_id);

    UPDATE Jogador
    SET saldo = saldo + @lucro
    WHERE id = @jogador_id;
END
GO