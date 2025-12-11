import pyodbc

# --- CONFIGURAÇÕES ---
SERVER = 'mednat.ieeta.pt'
PORT = '8101'
DATABASE = 'p3g4'
USERNAME = 'p3g4'
PASSWORD = 'Marnoto_'  # <--- A TUA PASSWORD REAL AQUI!


def get_connection():
    connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER},{PORT};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'
    return pyodbc.connect(connection_string)


# --- FUNÇÕES EXISTENTES (MANTIDAS IGUAIS) ---

def login(email, password, ip='127.0.0.1'):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "{CALL sp_Login (?, ?, ?)}"
        cursor.execute(sql, (email, password, ip))
        row = cursor.fetchone()
        conn.commit()
        conn.close()

        if row and row.Status == 'Sucesso':
            # ATUALIZAÇÃO: Agora lemos também o isAdmin
            return {
                "id": row.id,
                "nome": row.nome,
                "saldo": float(row.saldo),
                "isAdmin": bool(row.isAdmin)  # Novo campo
            }
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
        row = cursor.fetchone();
        conn.commit();
        conn.close()
        if row and row.Status == 'Sucesso': return True, row.Mensagem
        return False, (row.Mensagem if row else "Erro")
    except Exception as e:
        return False, str(e)


def obter_mesa_id(nome_jogo):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "SELECT TOP 1 m.id FROM Mesa m JOIN Jogo j ON m.jogo_id = j.id WHERE j.nome = ?"
        cursor.execute(sql, (nome_jogo,))
        row = cursor.fetchone();
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
        row = cursor.fetchone();
        conn.commit();
        conn.close()
        return row.sessao_id if row else None
    except:
        return None


def registar_aposta(sessao_id, valor, resultado, lucro):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "{CALL sp_RegistarAposta (?, ?, ?, ?)}"
        cursor.execute(sql, (sessao_id, valor, resultado, lucro))
        conn.commit();
        conn.close()
        return True
    except:
        return False


def atualizar_saldo_local(jogador_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT saldo FROM Jogador WHERE id = ?", (jogador_id,))
        row = cursor.fetchone();
        conn.close()
        return float(row.saldo) if row else 0.0
    except:
        return 0.0


def depositar_saldo(jogador_id, valor):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql_trans = "INSERT INTO Transacao (jogador_id, valor, tipoDeTransacao, sucesso) VALUES (?, ?, 'Deposito App', 1)"
        cursor.execute(sql_trans, (jogador_id, valor))
        sql_update = "UPDATE Jogador SET saldo = saldo + ? WHERE id = ?"
        cursor.execute(sql_update, (valor, jogador_id))
        conn.commit();
        conn.close()
        return True
    except:
        return False


# --- NOVAS FUNÇÕES (ADMIN E HISTÓRICO) ---

def obter_historico_pessoal(jogador_id):
    """Devolve as últimas 10 jogadas do jogador"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # JOINs para mostrar o nome do jogo e da aposta
        sql = """
              SELECT TOP 10 jg.nome, a.valor, a.resultado, a.lucro, a.dataAposta
              FROM Aposta a
                       JOIN SessaoDeJogo s ON a.sessaoJogo_id = s.id
                       JOIN Mesa m ON s.mesa_id = m.id
                       JOIN Jogo jg ON m.jogo_id = jg.id
              WHERE s.jogador_id = ?
              ORDER BY a.dataAposta DESC \
              """
        cursor.execute(sql, (jogador_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    except:
        return []


def admin_obter_todos_jogadores():
    """ADMIN: Lista todos os utilizadores"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, email, saldo, dataRegisto FROM Jogador")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except:
        return []


def admin_obter_todas_apostas():
    """ADMIN: Lista as últimas 20 apostas globais"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # MUDANÇA: Buscamos j.id, j.email e renomeamos jg.nome para jogo_nome
        sql = """
            SELECT TOP 20 j.id, j.email, jg.nome AS jogo_nome, a.resultado, a.lucro, a.dataAposta
            FROM Aposta a
            JOIN SessaoDeJogo s ON a.sessaoJogo_id = s.id
            JOIN Jogador j ON s.jogador_id = j.id
            JOIN Mesa m ON s.mesa_id = m.id
            JOIN Jogo jg ON m.jogo_id = jg.id
            ORDER BY a.dataAposta DESC
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()
        return rows
    except: return []


def levantar_saldo(jogador_id, valor):
    """Regista o levantamento e retira o dinheiro da conta"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 1. Registar na tabela Transacao
        sql_trans = "INSERT INTO Transacao (jogador_id, valor, tipoDeTransacao, sucesso) VALUES (?, ?, 'Levantamento', 1)"
        cursor.execute(sql_trans, (jogador_id, valor))

        # 2. Atualizar (Subtrair) o saldo do Jogador
        sql_update = "UPDATE Jogador SET saldo = saldo - ? WHERE id = ?"
        cursor.execute(sql_update, (valor, jogador_id))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro Levantamento: {e}")
        return False