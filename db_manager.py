import pyodbc

# --- CONFIGURAÇÕES ---
SERVER = 'mednat.ieeta.pt'
PORT = '8101'
DATABASE = 'p3g4'
USERNAME = 'p3g4'
PASSWORD = 'Marnoto_'  # <--- METE A TUA PASSWORD REAL AQUI!


def get_connection():
    connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER},{PORT};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'
    return pyodbc.connect(connection_string)


# --- FUNÇÕES ---

def login(email, password, ip='127.0.0.1'):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "{CALL sp_Login (?, ?, ?)}"
        cursor.execute(sql, (email, password, ip))
        row = cursor.fetchone()
        conn.commit()  # Gravar o log
        conn.close()

        if row and row.Status == 'Sucesso':
            return {"id": row.id, "nome": row.nome, "saldo": float(row.saldo)}
        return None
    except Exception as e:
        print(f"Erro Login: {e}")
        return None


def criar_jogador(nome, cc, data_nasc, email, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "{CALL sp_RegistarJogador (?, ?, ?, ?, ?)}"
        cursor.execute(sql, (nome, cc, data_nasc, email, password))

        row = cursor.fetchone()  # LER PRIMEIRO
        conn.commit()  # GRAVAR DEPOIS
        conn.close()

        if row and row.Status == 'Sucesso':
            return True, row.Mensagem
        return False, (row.Mensagem if row else "Erro desconhecido")
    except Exception as e:
        return False, str(e)


def obter_mesa_id(nome_jogo):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "SELECT TOP 1 m.id FROM Mesa m JOIN Jogo j ON m.jogo_id = j.id WHERE j.nome = ?"
        cursor.execute(sql, (nome_jogo,))
        row = cursor.fetchone()
        conn.close()
        return row.id if row else None
    except:
        return None


def iniciar_sessao(jogador_id, mesa_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "{CALL sp_IniciarSessao (?, ?)}"
        cursor.execute(sql, (jogador_id, mesa_id))

        row = cursor.fetchone()  # LER PRIMEIRO
        conn.commit()  # GRAVAR DEPOIS
        conn.close()

        return row.sessao_id if row else None
    except Exception as e:
        print(f"Erro Sessao: {e}")
        return None


def registar_aposta(sessao_id, valor, resultado, lucro):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "{CALL sp_RegistarAposta (?, ?, ?, ?)}"
        cursor.execute(sql, (sessao_id, valor, resultado, lucro))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro Aposta: {e}")
        return False


def atualizar_saldo_local(jogador_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT saldo FROM Jogador WHERE id = ?", (jogador_id,))
        row = cursor.fetchone()
        conn.close()
        return float(row.saldo) if row else 0.0
    except:
        return 0.0


def depositar_saldo(jogador_id, valor):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 1. Registar Transação
        sql_trans = "INSERT INTO Transacao (jogador_id, valor, tipoDeTransacao, sucesso) VALUES (?, ?, 'Deposito App', 1)"
        cursor.execute(sql_trans, (jogador_id, valor))

        # 2. Atualizar Saldo
        sql_update = "UPDATE Jogador SET saldo = saldo + ? WHERE id = ?"
        cursor.execute(sql_update, (valor, jogador_id))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro Deposito: {e}")
        return False