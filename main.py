import db_manager
import time
import random

# --- VARIÁVEIS GLOBAIS ---
JOGADOR_ATUAL = None  # Vai guardar {"id": 1, "nome": "João", "saldo": 100.0}


def limpar_ecra():
    print("\n" * 5)


# --- MENUS ---

def menu_inicial():
    while True:
        limpar_ecra()
        print("=== 🎰 CASINO ONLINE P3G4 🎰 ===")
        print("1. Login")
        print("2. Registar Conta")
        print("3. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            fazer_login()
        elif opcao == '2':
            registar_conta()
        elif opcao == '3':
            print("Até logo!")
            break
        else:
            print("Opção inválida.")


def menu_principal():
    """Menu para quando o utilizador já está logado"""
    global JOGADOR_ATUAL

    while True:
        # Atualizar saldo sempre que mostra o menu
        JOGADOR_ATUAL['saldo'] = db_manager.atualizar_saldo_local(JOGADOR_ATUAL['id'])

        limpar_ecra()
        print(f"👤 Olá, {JOGADOR_ATUAL['nome']} | 💰 Saldo: {JOGADOR_ATUAL['saldo']:.2f}€")
        print("-------------------------------")
        print("1. Jogar Blackjack 🃏")
        print("2. Jogar Banca Francesa 🎲 (Brevemente)")
        print("3. Depositar Dinheiro (Simulação)")
        print("4. Logout")

        opcao = input("Escolha: ")

        if opcao == '1':
            jogar_blackjack()
        elif opcao == '2':
            print("Jogo ainda em construção...")
            time.sleep(2)
        elif opcao == '3':
            print("Funcionalidade extra (podes implementar depois!)")
            time.sleep(2)
        elif opcao == '4':
            JOGADOR_ATUAL = None
            break


# --- AÇÕES ---

def fazer_login():
    global JOGADOR_ATUAL
    print("\n--- LOGIN ---")
    email = input("Email: ")
    password = input("Password: ")

    dados = db_manager.login(email, password)

    if dados:
        JOGADOR_ATUAL = dados
        print(f"\n✅ Bem-vindo, {dados['nome']}!")
        time.sleep(1)
        menu_principal()
    else:
        print("\n❌ Email ou password errados.")
        time.sleep(2)


def registar_conta():
    print("\n--- NOVO REGISTO ---")
    nome = input("Nome: ")
    cc = input("CC: ")
    data = input("Data Nascimento (YYYY-MM-DD): ")
    email = input("Email: ")
    pw = input("Password: ")

    sucesso, msg = db_manager.criar_jogador(nome, cc, data, email, pw)
    print(f"\nResultado: {msg}")
    time.sleep(2)


# --- LÓGICA DO JOGO (SIMPLIFICADA) ---
def jogar_blackjack():
    global JOGADOR_ATUAL
    print("\n🃏 A entrar na mesa de Blackjack...")

    # 1. Preparar Sessão na BD
    mesa_id = db_manager.obter_mesa_id('Blackjack')
    if not mesa_id:
        print("❌ Erro: Nenhuma mesa de Blackjack encontrada na BD.")
        time.sleep(3)
        return

    sessao_id = db_manager.iniciar_sessao(JOGADOR_ATUAL['id'], mesa_id)
    print(f"✅ Sessão #{sessao_id} iniciada. Boa sorte!")

    while True:
        print(f"\n💰 Saldo Atual: {JOGADOR_ATUAL['saldo']:.2f}€")
        aposta_str = input("Quanto queres apostar? (0 para sair): ")

        try:
            aposta = float(aposta_str)
        except:
            print("Valor inválido.")
            continue

        if aposta == 0:
            break
        if aposta > JOGADOR_ATUAL['saldo']:
            print("❌ Saldo insuficiente!")
            continue

        # 2. Simulação do Jogo (Aqui podes meter a lógica real das cartas depois)
        print("A dar as cartas...")
        time.sleep(1)

        # 50% de chance de ganhar (Só para testar a BD)
        ganhou = random.choice([True, False])

        if ganhou:
            lucro = aposta  # Ganha o dobro (recupera aposta + valor igual)
            resultado = 'Vitoria'
            print(f"🎉 GANHASTE! Recebeste +{lucro}€")
        else:
            lucro = -aposta  # Perde o valor apostado
            resultado = 'Derrota'
            print(f"💀 PERDESTE... Ficaste sem {aposta}€")

        # 3. Registar tudo na BD
        sucesso = db_manager.registar_aposta(sessao_id, aposta, resultado, lucro)

        if sucesso:
            # Atualizar saldo localmente para o próximo loop
            JOGADOR_ATUAL['saldo'] += lucro
        else:
            print("⚠️ Erro crítico ao gravar na BD! (Trigger de segurança disparou?)")
            break


# --- INÍCIO ---
if __name__ == "__main__":
    menu_inicial()