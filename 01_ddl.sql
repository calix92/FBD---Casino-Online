-- =====================================================
-- BASE DE DADOS: CASINO ONLINE (SQL) - VERSÃO FINAL SINGLE PLAYER
-- =====================================================

-- Tabela Jogador (Mantém-se igual)
CREATE TABLE Jogador (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    nome            NVARCHAR(100) NOT NULL,
    cc              NVARCHAR(20) UNIQUE NOT NULL,
    dataRegisto     DATE NOT NULL,
    dataNascimento  DATE NOT NULL,
    estadoVerificacao BIT DEFAULT 0,
    email           NVARCHAR(100) UNIQUE NOT NULL,
    saldo           DECIMAL(10,2) DEFAULT 0.00,
    password        NVARCHAR(255) NOT NULL
);
GO

-- =====================================================
-- Tabela RegistoLogin (Mantém-se igual)
CREATE TABLE RegistoLogin (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    jogador_id      INT NOT NULL,
    enderecoIp      NVARCHAR(45) NOT NULL,
    dataLogin       DATETIME DEFAULT GETDATE(),
    sucesso         BIT DEFAULT 1,

    FOREIGN KEY (jogador_id) REFERENCES Jogador(id)
        ON DELETE CASCADE
);
GO

-- =====================================================
-- Tabela Transacao (Mantém-se igual)
CREATE TABLE Transacao (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    jogador_id      INT NOT NULL,
    valor           DECIMAL(10,2) NOT NULL,
    tipoDeTransacao NVARCHAR(50) NOT NULL,
    sucesso         BIT DEFAULT 1,
    data            DATETIME DEFAULT GETDATE(),

    FOREIGN KEY (jogador_id) REFERENCES Jogador(id)
        ON DELETE CASCADE
);
GO

-- =====================================================
-- Tabela HistoricoPagamento (Mantém-se igual)
CREATE TABLE HistoricoPagamento (
    transacao_id    INT NOT NULL,
    numRegisto      INT NOT NULL,
    metodo          NVARCHAR(50),
    estado          NVARCHAR(30),
    valor           DECIMAL(10,2),
    dataPagamento   DATETIME DEFAULT GETDATE(),

    PRIMARY KEY (transacao_id, numRegisto),
    FOREIGN KEY (transacao_id) REFERENCES Transacao(id)
        ON DELETE CASCADE
);
GO

-- =====================================================
-- Tabela Jogo (Mantém-se igual)
CREATE TABLE Jogo (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    nome            NVARCHAR(50) NOT NULL,
    descricao       NVARCHAR(MAX)
);
GO

-- =====================================================
-- Tabela Dealer (Mantém-se igual)
CREATE TABLE Dealer (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    nome            NVARCHAR(100) NOT NULL
);
GO

-- =====================================================
-- Tabela Mesa (Mantém-se igual)
CREATE TABLE Mesa (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    jogo_id         INT NOT NULL,
    dealer_id       INT NULL,
    apostaMax       DECIMAL(10,2),
    apostaMin       DECIMAL(10,2),

    FOREIGN KEY (jogo_id) REFERENCES Jogo(id)
        ON DELETE CASCADE,
    FOREIGN KEY (dealer_id) REFERENCES Dealer(id)
        ON DELETE SET NULL
);
GO

-- =====================================================
-- Tabela SessaoDeJogo (ALTERADA)
-- Recebeu o jogador_id e numPartidas.
-- Perdeu a relação N:M com a tabela Joga (que foi eliminada).
-- =====================================================
CREATE TABLE SessaoDeJogo (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    mesa_id         INT NOT NULL,
    jogador_id      INT NOT NULL,     -- NOVO: Ligação direta ao Jogador (1:N)
    numPartidas     INT DEFAULT 0,    -- NOVO: Veio da antiga tabela Joga
    dataInicio      DATETIME DEFAULT GETDATE(),
    dataFim         DATETIME,

    FOREIGN KEY (mesa_id) REFERENCES Mesa(id)
        ON DELETE CASCADE,
    FOREIGN KEY (jogador_id) REFERENCES Jogador(id) -- FK para Jogador
        ON DELETE CASCADE
);
GO

-- =====================================================
-- Tabela Aposta (Mantém-se igual, liga à Sessão)
CREATE TABLE Aposta (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    sessaoJogo_id   INT NOT NULL,
    valor           DECIMAL(10,2) NOT NULL,
    resultado       NVARCHAR(50),
    lucro           DECIMAL(10,2),
    dataAposta      DATETIME DEFAULT GETDATE(),

    FOREIGN KEY (sessaoJogo_id) REFERENCES SessaoDeJogo(id)
        ON DELETE CASCADE
);
GO