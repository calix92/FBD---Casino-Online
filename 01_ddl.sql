    -- =====================================================
-- BASE DE DADOS: CASINO ONLINE (SQL)
-- =====================================================

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
CREATE TABLE Jogo (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    nome            NVARCHAR(50) NOT NULL,
    descricao       NVARCHAR(MAX)
);
GO

-- =====================================================
CREATE TABLE Dealer (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    nome            NVARCHAR(100) NOT NULL
);
GO

-- =====================================================
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
CREATE TABLE SessaoDeJogo (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    mesa_id         INT NOT NULL,
    dataInicio      DATETIME DEFAULT GETDATE(),
    dataFim         DATETIME,

    FOREIGN KEY (mesa_id) REFERENCES Mesa(id)
        ON DELETE CASCADE
);
GO

-- =====================================================
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

-- =====================================================
CREATE TABLE Joga (
    jogador_id          INT NOT NULL,
    sessaoJogo_id       INT NOT NULL,
    dataPrimeiraSessao  DATE,
    numPartidas         INT DEFAULT 0,

    PRIMARY KEY (jogador_id, sessaoJogo_id),
    FOREIGN KEY (jogador_id) REFERENCES Jogador(id)
        ON DELETE CASCADE,
    FOREIGN KEY (sessaoJogo_id) REFERENCES SessaoDeJogo(id)
        ON DELETE CASCADE
);
GO
