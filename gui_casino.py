import customtkinter as ctk
from tkinter import messagebox
import db_manager
import random
from PIL import Image, ImageTk
import os
import time

# --- CONFIGURAÇÃO VISUAL ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")


class CasinoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Casino P3G4 - Blackjack & Banca Francesa")
        self.geometry("900x600")

        # Arrancar maximizado
        self.after(0, lambda: self.state('zoomed'))

        self.jogador = None
        self.bg_image = None
        self.bg_label = None

        # Carregar a imagem uma vez para memória
        self.carregar_imagem_fundo()

        # Iniciar
        self.show_login_screen()

    def carregar_imagem_fundo(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "fotocc.jpg")
        try:
            pil_image = Image.open(image_path)
            self.bg_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(1920, 1080))
        except Exception as e:
            print(f"Aviso: Não foi possível carregar imagem de fundo ({e})")

    def setup_background(self):
        if self.bg_image:
            self.bg_label = ctk.CTkLabel(self, text="", image=self.bg_image)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            self.bg_label = ctk.CTkFrame(self, fg_color="#004d00")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        return self.bg_label

    def clean_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

    # ================= 1. LOGIN & REGISTO =================
    def show_login_screen(self):
        self.clean_screen()
        frame = ctk.CTkFrame(self)
        frame.pack(pady=40, padx=40, fill="both", expand=True)
        ctk.CTkLabel(frame, text="♣️ CASINO P3G4 ♦️", font=("Roboto", 30, "bold")).pack(pady=40)

        self.email_entry = ctk.CTkEntry(frame, placeholder_text="Email", width=300);
        self.email_entry.pack(pady=10)
        self.pass_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=300);
        self.pass_entry.pack(pady=10)

        ctk.CTkButton(frame, text="ENTRAR", command=self.fazer_login, width=200, height=40).pack(pady=20)
        ctk.CTkButton(frame, text="Criar Conta", fg_color="transparent", border_width=1,
                      command=self.show_register_screen).pack(pady=10)

    def show_register_screen(self):
        self.clean_screen()
        frame = ctk.CTkFrame(self)
        frame.pack(pady=20, padx=40, fill="both", expand=True)
        ctk.CTkLabel(frame, text="Novo Registo", font=("Roboto", 24)).pack(pady=20)

        self.reg_nome = ctk.CTkEntry(frame, placeholder_text="Nome", width=300);
        self.reg_nome.pack(pady=5)
        self.reg_cc = ctk.CTkEntry(frame, placeholder_text="CC", width=300);
        self.reg_cc.pack(pady=5)
        self.reg_data = ctk.CTkEntry(frame, placeholder_text="Data (YYYY-MM-DD)", width=300);
        self.reg_data.pack(pady=5)
        self.reg_email = ctk.CTkEntry(frame, placeholder_text="Email", width=300);
        self.reg_email.pack(pady=5)
        self.reg_pass = ctk.CTkEntry(frame, placeholder_text="Password", width=300, show="*");
        self.reg_pass.pack(pady=5)

        ctk.CTkButton(frame, text="CONFIRMAR", command=self.registar_user).pack(pady=20)
        ctk.CTkButton(frame, text="Voltar", fg_color="gray", command=self.show_login_screen).pack(pady=5)

    def fazer_login(self):
        dados = db_manager.login(self.email_entry.get(), self.pass_entry.get())
        if dados:
            self.jogador = dados
            self.show_main_menu()
        else:
            messagebox.showerror("Erro", "Login falhou.")

    def registar_user(self):
        ok, msg = db_manager.criar_jogador(self.reg_nome.get(), self.reg_cc.get(), self.reg_data.get(),
                                           self.reg_email.get(), self.reg_pass.get())
        if ok:
            messagebox.showinfo("Sucesso", "Conta criada!"); self.show_login_screen()
        else:
            messagebox.showerror("Erro", msg)

    # ================= 2. MENU PRINCIPAL (ATUALIZADO) =================
    def show_main_menu(self):
        self.clean_screen()
        bg = self.setup_background()

        # Aumentei um pouco a altura para caberem os novos botões
        menu_frame = ctk.CTkFrame(bg, fg_color="#2b2b2b", corner_radius=20, width=500, height=550)
        menu_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Mostra se é admin no título
        titulo = f"Bem-vindo, {self.jogador['nome']}"
        if self.jogador.get('isAdmin'): titulo += " (ADMIN)"

        ctk.CTkLabel(menu_frame, text=titulo, font=("Arial", 20, "bold")).pack(pady=(30, 10))
        ctk.CTkLabel(menu_frame, text=f"Saldo: {self.jogador['saldo']:.2f}€", text_color="#00FF00",
                     font=("Arial", 18)).pack(pady=10)

        # Botões de Jogo
        ctk.CTkButton(menu_frame, text="🃏 JOGAR BLACKJACK", width=300, height=40, fg_color="#D4AF37",
                      text_color="black", command=self.iniciar_blackjack).pack(pady=10)
        ctk.CTkButton(menu_frame, text="🎲 JOGAR BANCA FRANCESA", width=300, height=40, fg_color="#D4AF37",
                      text_color="black", command=self.iniciar_banca).pack(pady=10)

        # Botão de Depósito
        ctk.CTkButton(menu_frame, text="💰 DEPOSITAR", width=300, height=40, fg_color="#4CAF50", text_color="white",
                      command=self.menu_depositar).pack(pady=10)

        ctk.CTkButton(menu_frame, text="💸 LEVANTAR", width=300, height=40, fg_color="#F44336", text_color="white",
                      command=self.menu_levantar).pack(pady=5)

        # --- NOVO: Botão Meu Histórico ---
        ctk.CTkButton(menu_frame, text="📜 MEU HISTÓRICO", width=300, height=40, fg_color="#2196F3",
                      command=self.show_my_history).pack(pady=10)

        # --- NOVO: Botão Painel Admin (Só aparece se isAdmin=True) ---
        if self.jogador.get('isAdmin'):
            ctk.CTkButton(menu_frame, text="🔒 PAINEL ADMIN", width=300, height=40, fg_color="#B71C1C",
                          command=self.show_admin_panel).pack(pady=10)

        ctk.CTkButton(menu_frame, text="Sair", fg_color="red", command=self.show_login_screen).pack(pady=20)

    def menu_depositar(self):
        dialog = ctk.CTkInputDialog(text="Quanto queres depositar? (€)", title="Depósito")
        valor_str = dialog.get_input()
        if valor_str:
            try:
                valor = float(valor_str)
                if valor <= 0: raise ValueError
                if db_manager.depositar_saldo(self.jogador['id'], valor):
                    self.jogador['saldo'] += valor
                    messagebox.showinfo("Sucesso", f"Depositaste {valor}€ com sucesso!")
                    self.show_main_menu()
                else:
                    messagebox.showerror("Erro", "Falha na base de dados.")
            except:
                messagebox.showerror("Erro", "Valor inválido.")

    def menu_levantar(self):
        dialog = ctk.CTkInputDialog(text="Quanto queres levantar? (€)", title="Levantamento")
        valor_str = dialog.get_input()

        if valor_str:
            try:
                valor = float(valor_str)
                if valor <= 0: raise ValueError

                # Verificar se tem saldo suficiente antes de ir à BD
                if valor > self.jogador['saldo']:
                    messagebox.showerror("Erro", "Saldo insuficiente para esse levantamento!")
                    return

                if db_manager.levantar_saldo(self.jogador['id'], valor):
                    self.jogador['saldo'] -= valor
                    messagebox.showinfo("Sucesso", f"Levantaste {valor}€! O dinheiro foi enviado.")
                    self.show_main_menu()  # Atualiza o saldo no ecrã
                else:
                    messagebox.showerror("Erro", "Erro ao processar levantamento.")
            except:
                messagebox.showerror("Erro", "Valor inválido.")

    # ================= 3. BLACKJACK (Mantido igual) =================
    def iniciar_blackjack(self):
        self.mesa_id = db_manager.obter_mesa_id('Blackjack')
        if not self.mesa_id: messagebox.showerror("Erro", "Mesa não encontrada na BD!"); return
        self.sessao_id = db_manager.iniciar_sessao(self.jogador['id'], self.mesa_id)
        self.show_blackjack_screen()

    def show_blackjack_screen(self):
        self.clean_screen()
        bg = self.setup_background()
        self.create_top_bar(self)

        self.actions_frame = ctk.CTkFrame(self, height=100, fg_color="#2b2b2b")
        self.actions_frame.pack(side="bottom", fill="x");
        self.actions_frame.pack_propagate(False)
        self.entry_aposta = ctk.CTkEntry(self.actions_frame, placeholder_text="€", width=80);
        self.entry_aposta.pack(side="left", padx=20);
        self.entry_aposta.insert(0, "10")
        self.btn_deal = ctk.CTkButton(self.actions_frame, text="JOGAR", fg_color="#D4AF37", text_color="black",
                                      command=self.bj_deal);
        self.btn_deal.pack(side="left", padx=10)
        self.btn_hit = ctk.CTkButton(self.actions_frame, text="PEDIR", state="disabled", command=self.bj_hit);
        self.btn_hit.pack(side="left", padx=10)
        self.btn_stand = ctk.CTkButton(self.actions_frame, text="PARAR", state="disabled", fg_color="red",
                                       command=self.bj_stand);
        self.btn_stand.pack(side="left", padx=10)
        ctk.CTkButton(self.actions_frame, text="MENU", fg_color="gray", command=self.show_main_menu).pack(side="right",
                                                                                                          padx=20)

        ctk.CTkLabel(bg, text="DEALER", font=("Arial", 24, "bold"), text_color="yellow", fg_color="transparent").pack(
            pady=(80, 10))
        self.dealer_cards_frame = ctk.CTkFrame(bg, fg_color="transparent");
        self.dealer_cards_frame.pack()
        self.lbl_dealer_score = ctk.CTkLabel(bg, text="?", font=("Arial", 18), text_color="yellow",
                                             fg_color="transparent");
        self.lbl_dealer_score.pack()
        ctk.CTkLabel(bg, text="", height=80, fg_color="transparent").pack()
        ctk.CTkLabel(bg, text="TU", font=("Arial", 24, "bold"), text_color="cyan", fg_color="transparent").pack(
            pady=(10, 10))
        self.player_cards_frame = ctk.CTkFrame(bg, fg_color="transparent");
        self.player_cards_frame.pack()
        self.lbl_player_score = ctk.CTkLabel(bg, text="0", font=("Arial", 18), text_color="cyan",
                                             fg_color="transparent");
        self.lbl_player_score.pack()

    def bj_deal(self):
        try:
            self.valor = float(self.entry_aposta.get())
            if self.valor > self.jogador['saldo'] or self.valor <= 0: raise ValueError
        except:
            messagebox.showerror("Erro", "Aposta inválida"); return
        self.deck = self.create_deck();
        self.phand = [self.draw_card(), self.draw_card()];
        self.dhand = [self.draw_card(), self.draw_card()]
        self.update_bj_ui(hide=True)
        self.btn_deal.configure(state="disabled");
        self.entry_aposta.configure(state="disabled")
        self.btn_hit.configure(state="normal");
        self.btn_stand.configure(state="normal")
        if self.calc_score(self.phand) == 21: self.bj_stand()

    def bj_hit(self):
        self.phand.append(self.draw_card());
        self.update_bj_ui(hide=True)
        if self.calc_score(self.phand) > 21: self.bj_end("bust")

    def bj_stand(self):
        while self.calc_score(self.dhand) < 17: self.dhand.append(self.draw_card())
        self.update_bj_ui(hide=False)
        p, d = self.calc_score(self.phand), self.calc_score(self.dhand)
        if d > 21:
            self.bj_end("win")
        elif p > d:
            self.bj_end("win")
        elif p < d:
            self.bj_end("lose")
        else:
            self.bj_end("draw")

    def bj_end(self, res):
        lucro = self.valor if res == "win" else (-self.valor if res in ["bust", "lose"] else 0)
        txt = "Vitoria" if res == "win" else ("Derrota" if res in ["bust", "lose"] else "Empate")
        if db_manager.registar_aposta(self.sessao_id, self.valor, txt, lucro):
            self.jogador['saldo'] += lucro;
            self.update_saldo_lbl()
            messagebox.showinfo("Fim", f"{txt}! Saldo: {self.jogador['saldo']:.2f}€")
        else:
            messagebox.showerror("Erro", "Erro na BD")
        self.btn_deal.configure(state="normal");
        self.entry_aposta.configure(state="normal")
        self.btn_hit.configure(state="disabled");
        self.btn_stand.configure(state="disabled")

    def update_bj_ui(self, hide):
        for w in self.player_cards_frame.winfo_children(): w.destroy()
        for w in self.dealer_cards_frame.winfo_children(): w.destroy()
        for c in self.phand: self.draw_c(self.player_cards_frame, c)
        for i, c in enumerate(self.dhand): self.draw_c(self.dealer_cards_frame, c, hide and i == 1)
        self.lbl_player_score.configure(text=str(self.calc_score(self.phand)))
        self.lbl_dealer_score.configure(text="?" if hide else str(self.calc_score(self.dhand)))

    # ================= 4. BANCA FRANCESA (Mantido igual) =================
    def iniciar_banca(self):
        self.mesa_id = db_manager.obter_mesa_id('Banca Francesa')
        if not self.mesa_id: self.mesa_id = db_manager.obter_mesa_id('Blackjack')
        self.sessao_id = db_manager.iniciar_sessao(self.jogador['id'], self.mesa_id)
        self.show_banca_screen()

    def show_banca_screen(self):
        self.clean_screen();
        bg = self.setup_background();
        self.create_top_bar(self)
        ctk.CTkLabel(bg, text="BANCA FRANCESA", font=("Arial", 30, "bold"), text_color="gold",
                     fg_color="transparent").pack(pady=(50, 20))
        self.dice_frame = ctk.CTkFrame(bg, fg_color="transparent");
        self.dice_frame.pack(pady=20)
        self.dice_labels = []
        for _ in range(3):
            lbl = ctk.CTkLabel(self.dice_frame, text="🎲", font=("Arial", 60), text_color="white",
                               fg_color="transparent")
            lbl.pack(side="left", padx=20);
            self.dice_labels.append(lbl)
        self.lbl_resultado = ctk.CTkLabel(bg, text="Faz a tua aposta...", font=("Arial", 24, "bold"),
                                          text_color="white", fg_color="transparent");
        self.lbl_resultado.pack(pady=30)
        self.actions_frame = ctk.CTkFrame(self, height=150, fg_color="#2b2b2b");
        self.actions_frame.pack(side="bottom", fill="x");
        self.actions_frame.pack_propagate(False)
        self.entry_aposta_bf = ctk.CTkEntry(self.actions_frame, width=100, justify="center");
        self.entry_aposta_bf.pack(pady=5);
        self.entry_aposta_bf.insert(0, "10")
        btn_frame = ctk.CTkFrame(self.actions_frame, fg_color="transparent");
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="GRANDE", fg_color="#4CAF50", width=150,
                      command=lambda: self.jogar_banca("Grande")).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="PEQUENO", fg_color="#2196F3", width=150,
                      command=lambda: self.jogar_banca("Pequeno")).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="ASES", fg_color="#F44336", width=150,
                      command=lambda: self.jogar_banca("Ases")).pack(side="left", padx=10)
        ctk.CTkButton(self.actions_frame, text="VOLTAR", fg_color="gray", command=self.show_main_menu, height=30).place(
            relx=0.9, rely=0.8, anchor="center")

    def jogar_banca(self, tipo):
        try:
            val = float(self.entry_aposta_bf.get())
        except:
            return
        if val > self.jogador['saldo'] or val <= 0: return

        while True:
            d = [random.randint(1, 6) for _ in range(3)];
            s = sum(d)
            if s == 3:
                res = "Ases"; break
            elif s in [14, 15, 16]:
                res = "Grande"; break
            elif s in [5, 6, 7]:
                res = "Pequeno"; break

        dice_chars = ["", "⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
        for i, l in enumerate(self.dice_labels): l.configure(text=dice_chars[d[i]])

        ganhou = (tipo == res);
        luc = val * 60 if ganhou and res == "Ases" else (val if ganhou else -val)
        txt_bd = "Vitoria" if ganhou else "Derrota"
        self.lbl_resultado.configure(text=f"SAIU {res.upper()} ({s})!", text_color=("#00FF00" if ganhou else "red"))
        if db_manager.registar_aposta(self.sessao_id, val, txt_bd, luc):
            self.jogador['saldo'] += luc;
            self.update_saldo_lbl()

    # ================= 5. TELAS NOVAS: HISTÓRICO E ADMIN =================

    def show_my_history(self):
        self.clean_screen()
        bg = self.setup_background()

        frame = ctk.CTkFrame(bg, fg_color="#2b2b2b", width=800, height=600)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(frame, text="📜 Meu Histórico (Últimas 10)", font=("Arial", 20, "bold")).pack(pady=20)

        scroll = ctk.CTkScrollableFrame(frame, width=700, height=400)
        scroll.pack(pady=10)

        historico = db_manager.obter_historico_pessoal(self.jogador['id'])
        ctk.CTkLabel(scroll, text=f"{'JOGO':<15} | {'APOSTA':<10} | {'RES':<10} | {'LUCRO':<10} | {'DATA'}",
                     font=("Consolas", 14, "bold"), anchor="w").pack(fill="x", padx=10)
        ctk.CTkLabel(scroll, text="-" * 80).pack()

        for row in historico:
            data_fmt = row.dataAposta.strftime('%Y-%m-%d %H:%M')
            txt = f"{row.nome:<15} | {row.valor:>8.2f}€ | {row.resultado:<10} | {row.lucro:>+8.2f}€ | {data_fmt}"
            col = "#00FF00" if row.lucro > 0 else ("red" if row.lucro < 0 else "white")
            ctk.CTkLabel(scroll, text=txt, font=("Consolas", 12), text_color=col, anchor="w").pack(fill="x", padx=10)

        ctk.CTkButton(frame, text="Voltar", command=self.show_main_menu).pack(pady=20)

    def show_admin_panel(self):
        self.clean_screen()
        bg = self.setup_background()

        frame = ctk.CTkFrame(bg, fg_color="#1a1a1a", width=900, height=700)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame, text="🔒 PAINEL DE ADMINISTRAÇÃO", font=("Arial", 24, "bold"), text_color="red").pack(
            pady=20)

        # Abas / Tabs
        tabview = ctk.CTkTabview(frame, width=800, height=500)
        tabview.pack(pady=10)
        tabview.add("Jogadores")
        tabview.add("Apostas Globais")

        # ABA 1: JOGADORES
        scroll_jog = ctk.CTkScrollableFrame(tabview.tab("Jogadores"), width=750, height=400)
        scroll_jog.pack()
        jogadores = db_manager.admin_obter_todos_jogadores()

        ctk.CTkLabel(scroll_jog, text=f"{'ID':<5} {'NOME':<20} {'EMAIL':<30} {'SALDO':<10}",
                     font=("Consolas", 12, "bold")).pack(anchor="w")
        for j in jogadores:
            txt = f"{j.id:<5} {j.nome:<20} {j.email:<30} {j.saldo:>8.2f}€"
            ctk.CTkLabel(scroll_jog, text=txt, font=("Consolas", 12)).pack(anchor="w")

        # ABA 2: APOSTAS GLOBAIS (CORRIGIDA)
        scroll_bet = ctk.CTkScrollableFrame(tabview.tab("Apostas Globais"), width=750, height=400)
        scroll_bet.pack()
        apostas = db_manager.admin_obter_todas_apostas()

        # Cabeçalho: RESULTADO em vez de VALOR
        # ID(5) | EMAIL(30) | JOGO(15) | RES(10) | LUCRO(10) | DATA
        header_txt = f"{'ID':<5} {'EMAIL DO JOGADOR':<30} {'JOGO':<15} {'RESULTADO':<10} {'LUCRO':<10} {'DATA'}"
        ctk.CTkLabel(scroll_bet, text=header_txt, font=("Consolas", 12, "bold")).pack(anchor="w")
        ctk.CTkLabel(scroll_bet, text="-" * 100, font=("Consolas", 12)).pack(anchor="w")

        for a in apostas:
            dt = a.dataAposta.strftime('%d/%m %H:%M')

            # Nota: a.resultado vem agora da query
            txt = f"{a.id:<5} {a.email:<30} {a.jogo_nome:<15} {a.resultado:<10} {a.lucro:>+8.2f}€ {dt}"

            col = "green" if a.lucro > 0 else "red"
            ctk.CTkLabel(scroll_bet, text=txt, font=("Consolas", 12), text_color=col).pack(anchor="w")

        ctk.CTkButton(frame, text="Voltar ao Menu", fg_color="gray", command=self.show_main_menu).pack(pady=20)
    # --- UTILITÁRIOS (Mantidos igual) ---
    def create_top_bar(self, p):
        top = ctk.CTkFrame(p, height=40, fg_color="#2b2b2b");
        top.pack(fill="x", side="top")
        ctk.CTkLabel(top, text=f"👤 {self.jogador['nome']}", font=("Arial", 14)).pack(side="left", padx=20)
        self.lbl_saldo_ui = ctk.CTkLabel(top, text=f"💰 {self.jogador['saldo']:.2f}€", text_color="#00FF00",
                                         font=("Arial", 14, "bold"));
        self.lbl_saldo_ui.pack(side="right", padx=20)

    def update_saldo_lbl(self):
        if hasattr(self, 'lbl_saldo_ui'): self.lbl_saldo_ui.configure(text=f"💰 {self.jogador['saldo']:.2f}€")

    def create_deck(self):
        v = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'];
        n = ['♥', '♦', '♣', '♠']
        d = [{'r': r, 's': s} for s in n for r in v];
        random.shuffle(d);
        return d

    def draw_card(self):
        return self.deck.pop()

    def draw_c(self, p, c, h=False):
        col = "red" if c['s'] in ['♥', '♦'] else "black";
        txt = "?" if h else f"{c['r']}\n{c['s']}";
        bg = "#222" if h else "white"
        f = ctk.CTkFrame(p, width=60, height=80, fg_color=bg);
        f.pack(side="left", padx=5)
        ctk.CTkLabel(f, text=txt, text_color=("gray" if h else col), font=("Arial", 16, "bold")).place(relx=0.5,
                                                                                                       rely=0.5,
                                                                                                       anchor="center")

    def calc_score(self, h):
        s, a = 0, 0
        for c in h:
            if c['r'] in ['J', 'Q', 'K']:
                s += 10
            elif c['r'] == 'A':
                a += 1; s += 11
            else:
                s += int(c['r'])
        while s > 21 and a: s -= 10; a -= 1
        return s


if __name__ == "__main__":
    app = CasinoApp()
    app.mainloop()