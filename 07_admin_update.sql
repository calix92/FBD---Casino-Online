USE [p3g4];
GO

-- 1. Adicionar coluna 'isAdmin' à tabela Jogador (0 = Normal, 1 = Admin)
ALTER TABLE Jogador ADD isAdmin BIT DEFAULT 0;
GO

-- 2. Promover o João a Admin (Substitui pelo email que usas)
UPDATE Jogador SET isAdmin = 1 WHERE email = 'joao@teste.com';
GO

-- 3. Atualizar a Procedure de Login para devolver essa informação
CREATE OR ALTER PROCEDURE sp_Login
    @email    NVARCHAR(100),
    @password NVARCHAR(255),
    @ip       NVARCHAR(45)
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @jogador_id INT;

    SELECT @jogador_id = id
    FROM Jogador
    WHERE email = @email AND password = @password;

    IF @jogador_id IS NOT NULL
    BEGIN
        INSERT INTO RegistoLogin (jogador_id, enderecoIp, sucesso) VALUES (@jogador_id, @ip, 1);

        -- AGORA DEVOLVE TAMBÉM O CAMPO 'isAdmin'
        SELECT id, nome, saldo, isAdmin, 'Sucesso' as Status FROM Jogador WHERE id = @jogador_id;
    END
    ELSE
    BEGIN
        DECLARE @id_tentativa INT = (SELECT id FROM Jogador WHERE email = @email);
        IF @id_tentativa IS NOT NULL
            INSERT INTO RegistoLogin (jogador_id, enderecoIp, sucesso) VALUES (@id_tentativa, @ip, 0);

        SELECT NULL as id, NULL as nome, NULL as saldo, 0 as isAdmin, 'Erro' as Status;
    END
END
GO