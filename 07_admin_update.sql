USE [p3g4];
GO

-- 1. Adicionar coluna 'isAdmin' (Protegido contra erros de repetição)
IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'isAdmin' AND Object_ID = Object_ID(N'Jogador'))
BEGIN
    ALTER TABLE Jogador ADD isAdmin BIT DEFAULT 0;
END
GO

-- 2. Promover o João a Admin
UPDATE Jogador SET isAdmin = 1 WHERE email = 'joao@teste.com';
GO

-- 3. Atualizar a Procedure de Login (CORRIGIDO COM ;)
CREATE OR ALTER PROCEDURE sp_Login
    @email    NVARCHAR(100),
    @password NVARCHAR(255),
    @ip       NVARCHAR(45)
AS
BEGIN
    SET NOCOUNT ON; -- <--- O PONTO E VÍRGULA OBRIGATÓRIO ESTÁ AQUI
    DECLARE @jogador_id INT;

    SELECT @jogador_id = id
    FROM Jogador
    WHERE email = @email AND password = @password;

    IF @jogador_id IS NOT NULL
    BEGIN
        INSERT INTO RegistoLogin (jogador_id, enderecoIp, sucesso) VALUES (@jogador_id, @ip, 1);

        -- Devolve também o campo 'isAdmin'
        SELECT id, nome, saldo, isAdmin, 'Sucesso' as Status FROM Jogador WHERE id = @jogador_id;
    END
    ELSE
    BEGIN
        DECLARE @id_tentativa INT = (SELECT id FROM Jogador WHERE email = @email);
        IF @id_tentativa IS NOT NULL
            INSERT INTO RegistoLogin (jogador_id, enderecoIp, sucesso) VALUES (@id_tentativa, @ip, 0);

        SELECT NULL as id, NULL as nome, NULL as saldo, 0 as isAdmin, 'Erro' as Status;
    END
END;
GO