import customtkinter as ctk
from tkinter import messagebox
import db_manager
import random

# --- CONFIGURAÇÃO VISUAL ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")


class CasinoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Casino P3G4 - Blackjack")
        self.geometry("900x600")

        self.jogador = None  # Vai guardar os dados do user

        # Iniciar no Ecrã de Login
        self.show_login_screen()

    # ================= TELA DE LOGIN =================
    def show_login_screen(self):
        self.clean_screen()

        frame = ctk.CTkFrame(self)
        frame.pack(pady=40, padx=40, fill="both", expand=True)

        label = ctk.CTkLabel(frame, text="♣️ CASINO ONLINE ♦️", font=("Roboto", 24, "bold"))
        label.pack(pady=20)

        self.email_entry = ctk.CTkEntry(frame, placeholder_text="Email", width=300)
        self.email_entry.pack(pady=10)

        self.pass_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=300)
        self.pass_entry.pack(pady=10)

        btn_login = ctk.CTkButton(frame, text="Entrar", command=self.fazer_login)
        btn_login.pack(pady=10)

        btn_registo = ctk.CTkButton(frame, text="Criar Conta Nova", fg_color="transparent", border_width=2,
                                    command=self.show_register_screen)
        btn_registo.pack(pady=10)

    # ================= TELA DE REGISTO =================
    def show_register_screen(self):
        self.clean_screen()
        frame = ctk.CTkFrame(self)
        frame.pack(pady=20, padx=40, fill="both", expand=True)

        ctk.CTkLabel(frame, text="Novo Registo", font=("Roboto", 20)).pack(pady=10)

        self.reg_nome = ctk.CTkEntry(frame, placeholder_text="Nome", width=300)
        self.reg_nome.pack(pady=5)

        self.reg_cc = ctk.CTkEntry(frame, placeholder_text="CC / BI", width=300)
        self.reg_cc.pack(pady=5)

        self.reg_data = ctk.CTkEntry(frame, placeholder_text="Data Nasc (YYYY-MM-DD)", width=300)
        self.reg_data.pack(pady=5)

        self.reg_email = ctk.CTkEntry(frame, placeholder_text="Email", width=300)
        self.reg_email.pack(pady=5)

        self.reg_pass = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=300)
        self.reg_pass.pack(pady=5)

        ctk.CTkButton(frame, text="Confirmar Registo", command=self.registar_user).pack(pady=15)
        ctk.CTkButton(frame, text="Voltar", fg_color="gray", command=self.show_login_screen).pack(pady=5)

    # ================= LÓGICA DE LOGIN/REGISTO =================
    def fazer_login(self):
        email = self.email_entry.get()
        pw = self.pass_entry.get()

        dados = db_manager.login(email, pw)
        if dados:
            self.jogador = dados
            self.show_game_screen()
        else:
            messagebox.showerror("Erro", "Login falhou. Verifica os dados.")

    def registar_user(self):
        # Chama o DB Manager
        sucesso, msg = db_manager.criar_jogador(
            self.reg_nome.get(), self.reg_cc.get(), self.reg_data.get(),
            self.reg_email.get(), self.reg_pass.get()
        )
        if sucesso:
            messagebox.showinfo("Sucesso", "Conta criada! Podes fazer login.")
            self.show_login_screen()
        else:
            messagebox.showerror("Erro", msg)

    # ================= TELA DE JOGO (BLACKJACK) =================
    def show_game_screen(self):
        self.clean_screen()

        # 1. Preparar Sessão na BD
        self.mesa_id = db_manager.obter_mesa_id('Blackjack')
        self.sessao_id = db_manager.iniciar_sessao(self.jogador['id'], self.mesa_id)

        # --- UI DO JOGO ---
        # Topo: Info do Jogador
        top_frame = ctk.CTkFrame(self, height=50)
        top_frame.pack(fill="x", side="top")

        self.lbl_nome = ctk.CTkLabel(top_frame, text=f"👤 {self.jogador['nome']}", font=("Arial", 14))
        self.lbl_nome.pack(side="left", padx=20)

        self.lbl_saldo = ctk.CTkLabel(top_frame, text=f"💰 {self.jogador['saldo']:.2f}€", font=("Arial", 14, "bold"),
                                      text_color="#00FF00")
        self.lbl_saldo.pack(side="right", padx=20)

        # Mesa Verde
        self.table_frame = ctk.CTkFrame(self, fg_color="#004d00")  # Verde Casino
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Área do Dealer
        ctk.CTkLabel(self.table_frame, text="DEALER", text_color="white").pack(pady=(10, 0))
        self.dealer_cards_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        self.dealer_cards_frame.pack(pady=10)
        self.lbl_dealer_score = ctk.CTkLabel(self.table_frame, text="Pontos: ?", text_color="white")
        self.lbl_dealer_score.pack()

        # Área do Jogador
        ctk.CTkLabel(self.table_frame, text="TU", text_color="white").pack(pady=(30, 0))
        self.player_cards_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        self.player_cards_frame.pack(pady=10)
        self.lbl_player_score = ctk.CTkLabel(self.table_frame, text="Pontos: 0", text_color="white")
        self.lbl_player_score.pack()

        # Área de Ações (Botões)
        self.actions_frame = ctk.CTkFrame(self, height=80)
        self.actions_frame.pack(fill="x", side="bottom")

        # Input de Aposta
        self.entry_aposta = ctk.CTkEntry(self.actions_frame, placeholder_text="Aposta (€)", width=100)
        self.entry_aposta.pack(side="left", padx=20, pady=20)
        self.entry_aposta.insert(0, "10")

        self.btn_deal = ctk.CTkButton(self.actions_frame, text="JOGAR (DEAL)", fg_color="#D4AF37", text_color="black",
                                      command=self.start_round)
        self.btn_deal.pack(side="left", padx=10)

        self.btn_hit = ctk.CTkButton(self.actions_frame, text="PEDIR CARTA", state="disabled", command=self.hit)
        self.btn_hit.pack(side="left", padx=10)

        self.btn_stand = ctk.CTkButton(self.actions_frame, text="PARAR", state="disabled", fg_color="red",
                                       command=self.stand)
        self.btn_stand.pack(side="left", padx=10)

        # Botão Sair
        ctk.CTkButton(self.actions_frame, text="SAIR", fg_color="gray", width=60, command=self.logout).pack(
            side="right", padx=20)

    # ================= LÓGICA DO BLACKJACK =================
    def start_round(self):
        # Validar Aposta
        try:
            self.valor_aposta = float(self.entry_aposta.get())
        except:
            messagebox.showerror("Erro", "Valor de aposta inválido!")
            return

        if self.valor_aposta > self.jogador['saldo'] or self.valor_aposta <= 0:
            messagebox.showerror("Erro", "Saldo insuficiente ou valor inválido.")
            return

        # Limpar mesa
        self.clear_table_ui()
        self.deck = self.create_deck()
        self.player_hand = []
        self.dealer_hand = []

        # Dar cartas iniciais
        self.player_hand.append(self.draw_card())
        self.dealer_hand.append(self.draw_card())
        self.player_hand.append(self.draw_card())
        self.dealer_hand.append(self.draw_card())

        # Atualizar UI
        self.update_cards_ui(hide_dealer=True)
        self.btn_deal.configure(state="disabled")
        self.btn_hit.configure(state="normal")
        self.btn_stand.configure(state="normal")
        self.entry_aposta.configure(state="disabled")

        # Verificar Blackjack imediato (21)
        if self.calculate_score(self.player_hand) == 21:
            self.stand()  # Passa logo para o fim

    def hit(self):
        self.player_hand.append(self.draw_card())
        self.update_cards_ui(hide_dealer=True)

        if self.calculate_score(self.player_hand) > 21:
            self.end_round(result="bust")  # Rebentou

    def stand(self):
        # Dealer joga (simulação simples: dealer pede até ter 17)
        while self.calculate_score(self.dealer_hand) < 17:
            self.dealer_hand.append(self.draw_card())

        self.update_cards_ui(hide_dealer=False)
        self.determine_winner()

    def determine_winner(self):
        p_score = self.calculate_score(self.player_hand)
        d_score = self.calculate_score(self.dealer_hand)

        if d_score > 21:
            self.end_round("dealer_bust")
        elif p_score > d_score:
            self.end_round("win")
        elif p_score < d_score:
            self.end_round("lose")
        else:
            self.end_round("draw")

    def end_round(self, result):
        # Calcular Lucro
        lucro = 0
        res_str = ""

        if result == "win" or result == "dealer_bust":
            lucro = self.valor_aposta
            res_str = "Vitoria"
            msg = "GANHASTE! 🎉"
        elif result == "bust" or result == "lose":
            lucro = -self.valor_aposta
            res_str = "Derrota"
            msg = "PERDESTE... 💀"
        else:
            lucro = 0
            res_str = "Empate"
            msg = "EMPATE 😐"

        # --- REGISTAR NA BASE DE DADOS ---
        sucesso = db_manager.registar_aposta(self.sessao_id, self.valor_aposta, res_str, lucro)

        if sucesso:
            # Atualizar saldo visual
            self.jogador['saldo'] += lucro
            self.lbl_saldo.configure(text=f"💰 {self.jogador['saldo']:.2f}€")
            messagebox.showinfo("Fim da Ronda", f"{msg}\nResultado: {res_str}\nSaldo: {self.jogador['saldo']:.2f}€")
        else:
            messagebox.showerror("Erro BD", "Erro ao gravar aposta! O Trigger pode ter bloqueado.")

        # Reset Botões
        self.btn_deal.configure(state="normal")
        self.btn_hit.configure(state="disabled")
        self.btn_stand.configure(state="disabled")
        self.entry_aposta.configure(state="normal")
        self.update_cards_ui(hide_dealer=False)  # Mostra tudo no fim

    # ================= UTILITÁRIOS DE CARTAS =================
    def create_deck(self):
        suits = ['♥', '♦', '♣', '♠']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        deck = [{'rank': r, 'suit': s} for s in suits for r in ranks]
        random.shuffle(deck)
        return deck

    def draw_card(self):
        return self.deck.pop()

    def calculate_score(self, hand):
        score = 0
        aces = 0
        for card in hand:
            r = card['rank']
            if r in ['J', 'Q', 'K']:
                score += 10
            elif r == 'A':
                aces += 1
                score += 11
            else:
                score += int(r)
        while score > 21 and aces:
            score -= 10
            aces -= 1
        return score

    def draw_card_widget(self, parent, card, hidden=False):
        # Desenha um "cartão" bonito com CustomTkinter
        color = "red" if card['suit'] in ['♥', '♦'] else "black"
        text = "?" if hidden else f"{card['rank']}\n{card['suit']}"
        text_col = "gray" if hidden else color
        bg = "#2b2b2b" if hidden else "white"

        frame = ctk.CTkFrame(parent, width=60, height=90, fg_color=bg, corner_radius=8)
        frame.pack(side="left", padx=5)

        lbl = ctk.CTkLabel(frame, text=text, text_color=text_col, font=("Arial", 18, "bold"))
        lbl.place(relx=0.5, rely=0.5, anchor="center")

    def update_cards_ui(self, hide_dealer=True):
        # Limpar widgets antigos
        for widget in self.player_cards_frame.winfo_children(): widget.destroy()
        for widget in self.dealer_cards_frame.winfo_children(): widget.destroy()

        # Desenhar Dealer
        for i, card in enumerate(self.dealer_hand):
            is_hidden = (i == 1 and hide_dealer)  # Esconde a 2ª carta
            self.draw_card_widget(self.dealer_cards_frame, card, is_hidden)

        if hide_dealer:
            self.lbl_dealer_score.configure(text="Pontos: ?")
        else:
            self.lbl_dealer_score.configure(text=f"Pontos: {self.calculate_score(self.dealer_hand)}")

        # Desenhar Player
        for card in self.player_hand:
            self.draw_card_widget(self.player_cards_frame, card)
        self.lbl_player_score.configure(text=f"Pontos: {self.calculate_score(self.player_hand)}")

    def clear_table_ui(self):
        for widget in self.player_cards_frame.winfo_children(): widget.destroy()
        for widget in self.dealer_cards_frame.winfo_children(): widget.destroy()
        self.lbl_player_score.configure(text="Pontos: 0")
        self.lbl_dealer_score.configure(text="Pontos: 0")

    def clean_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

    def logout(self):
        self.jogador = None
        self.show_login_screen()


if __name__ == "__main__":
    app = CasinoApp()
    app.mainloop()