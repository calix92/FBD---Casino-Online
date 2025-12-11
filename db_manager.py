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
    """Devolve as últimas 10 jogadas do jogador com o nome do Dealer"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # ADICIONADO: LEFT JOIN com Mesa e Dealer, e d.nome na SELECT
        sql = """
              SELECT TOP 10 jg.nome, a.valor, a.resultado, a.lucro, a.dataAposta, d.nome AS nome_dealer
              FROM Aposta a
                       JOIN SessaoDeJogo s ON a.sessaoJogo_id = s.id
                       JOIN Mesa m ON s.mesa_id = m.id
                       JOIN Jogo jg ON m.jogo_id = jg.id
                       LEFT JOIN Dealer d ON m.dealer_id = d.id -- Novo JOIN
              WHERE s.jogador_id = ?
              ORDER BY a.dataAposta DESC
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
    """ADMIN: Lista as últimas 20 apostas globais com o nome do Dealer"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # ADICIONADO: LEFT JOIN com Mesa e Dealer, e d.nome na SELECT
        sql = """
            SELECT TOP 20 j.id, j.email, jg.nome AS jogo_nome, a.resultado, a.lucro, a.dataAposta, d.nome AS nome_dealer
            FROM Aposta a
            JOIN SessaoDeJogo s ON a.sessaoJogo_id = s.id
            JOIN Jogador j ON s.jogador_id = j.id
            JOIN Mesa m ON s.mesa_id = m.id
            JOIN Jogo jg ON m.jogo_id = jg.id
            LEFT JOIN Dealer d ON m.dealer_id = d.id -- Novo JOIN
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

def obter_transacoes_pessoais(jogador_id):
    """Devolve o histórico de depósitos e levantamentos do jogador"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Vamos buscar o tipo, valor e data. Ordenamos da mais recente para a mais antiga.
        sql = """
              SELECT tipoDeTransacao, valor, data 
              FROM Transacao 
              WHERE jogador_id = ? 
              ORDER BY data DESC
              """
        cursor.execute(sql, (jogador_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"Erro ao obter transações: {e}")
        return []


def admin_obter_todas_transacoes():
    """ADMIN: Lista todas as transações (depósitos e levantamentos) de todos os jogadores"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Vamos buscar o ID da transação, ID do jogador, Email, Tipo, Valor e Data
        sql = """
              SELECT t.id, j.id AS jogador_id, j.email, t.tipoDeTransacao, t.valor, t.data
              FROM Transacao t
                       JOIN Jogador j ON t.jogador_id = j.id
              ORDER BY t.data DESC \
              """
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"Erro Admin Transacoes: {e}")
        return []


def sortear_dealer_mesa(mesa_id):
    """Pede ao SQL Server para sortear um dealer aleatório e atribuí-lo à mesa"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Chama a Stored Procedure que criámos
        sql = "{CALL sp_SortearDealerParaMesa (?)}"
        cursor.execute(sql, (mesa_id,))

        row = cursor.fetchone()
        conn.commit()  # Importante: estamos a fazer um UPDATE na mesa
        conn.close()

        return row.nome if row else "Dealer Fantasma"
    except Exception as e:
        print(f"Erro ao sortear dealer: {e}")
        return "Dealer da Casa"