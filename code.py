import getpass
import json
import os
import subprocess
from time import sleep
import customtkinter
import pyautogui
import webbrowser
import atexit


class FrameLateral(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.CriaInterface = None
        self.FrameSuperior = None

        self.label_titulo = customtkinter.CTkLabel(self, text="Acesso Remoto", font=("Calibri Bold", 25),
                                                   justify="center")
        self.label_titulo.grid(row=5, column=0, padx=30, pady=(10, 10), sticky="ew")
        self.label_ip = customtkinter.CTkLabel(self, text="IP do Servidor:")
        self.label_ip.grid(row=6, column=0, padx=30, pady=(13, 0), sticky="ew")
        self.entry_ip = customtkinter.CTkEntry(self, corner_radius=25, justify='center')
        self.entry_ip.grid(row=7, column=0, padx=(5, 15), pady=(13, 0), sticky="ew")
        self.label_usuario = customtkinter.CTkLabel(self, text="Nome de Usuário:")
        self.label_usuario.grid(row=8, column=0, padx=30, pady=(13, 0), sticky="ew")
        username = getpass.getuser()
        self.entry_usuario = customtkinter.CTkEntry(self, corner_radius=25, justify="center")
        self.entry_usuario.grid(row=9, column=0, padx=(5, 15), pady=(13, 0), sticky="ew")
<<<<<<< HEAD
        self.entry_usuario.insert(0, f"{username}@cloud")
=======
        self.entry_usuario.insert(0, username)
>>>>>>> 544f86ee3f06642d711208d3e5366242d200598e
        self.label_senha = customtkinter.CTkLabel(self, text="Senha:")
        self.label_senha.grid(row=10, column=0, padx=30, pady=(13, 0), sticky="ew")
        self.entry_senha = customtkinter.CTkEntry(self, show="*", corner_radius=25, justify='center')
        self.entry_senha.grid(row=11, column=0, padx=(5, 15), pady=(13, 0), sticky="ew")
        self.button_conectar = customtkinter.CTkButton(self, text="Conectar", command=self.conectar, text_color="white",
                                                       corner_radius=15, fg_color="#E4621B", hover_color="#3E3E63")
        self.button_conectar.grid(row=12, column=0, padx=30, pady=(13, 0), sticky="ew")

        # Configura o enter para validar a conexão
        self.entry_senha.bind("<Return>", lambda event: self.conectar())

    def conectar(self):
        ip = self.entry_ip.get()
        usuario = self.entry_usuario.get()
        self.entry_senha.get()

        if not (ip and usuario and self.entry_senha.get()):
            self.CriaInterface.mensagem_de_alertas()

        else:
            try:
                self.remover_aviso_certificado(ip)
                arquivo_rdp = self.criar_arquivo_rdp(ip, usuario)
                subprocess.Popen(['mstsc', arquivo_rdp])
                app.lower()
                self.entry_ip.delete(0, 'end')
                self.entry_senha.delete(0, 'end')
                self.entry_senha.insert(0, self.entry_senha.get())
                self.entry_senha.focus()
            except Exception as e:
                print(f"Erro ao conectar: {e}")

            tempo_rdp = self.Frame_Superior.exibir_tempo()
            sleep(float(tempo_rdp))
            pyautogui.write(senha)
            pyautogui.press("enter")

    @staticmethod
    def remover_aviso_certificado(ip):
        try:
            subprocess.run(
                'reg add "HKLM\\Software\\Microsoft\\Terminal Server Client" /v AuthenticationLevelOverride /t REG_DWORD /d 0 /f >nul 2>&1',
                shell=True)
            subprocess.run(
                f'reg add "HKCU\\SOFTWARE\\Microsoft\\Terminal Server Client\\LocalDevices" /v "{ip}" /t REG_DWORD /d 0x0000006f /f >nul 2>&1',
                shell=True)
        except Exception as e:
            print(f"Erro ao remover aviso de certificado: {e}")

    @staticmethod
    def criar_arquivo_rdp(ip, usuario):
        pasta_acesso_remoto = "C:\\AcessoRemoto"
        filename = os.path.join(pasta_acesso_remoto, f"{ip}_conexao_remota.rdp")
        with open(filename, 'w') as file:
            file.write(f"full address:s:{ip}\n")
            file.write(f"username:s:{usuario}\n")
            file.write("prompt for credentials:i:0\n")

        return filename


class FrameSuperior(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        # faz a exlusão dos arquivo rdp quando finalizar a tela
        atexit.register(self.sair)

        self.variavel_opcao = customtkinter.StringVar(self)

        self.label_seletor_de_tempo = customtkinter.CTkLabel(self, text="Tempo para fazer o login:", width=10, height=15
                                                             , font=("Calibri", 15))
        self.label_seletor_de_tempo.grid(row=0, column=0, padx=(10, 45), pady=(8, 0), sticky="w")
        self.seletor_de_tempo = customtkinter.CTkOptionMenu(self, variable=self.variavel_opcao,
                                                            dropdown_fg_color="#3F5663", width=23, height=20,
                                                            button_color="#3E3E63", fg_color="#3E3E63",
                                                            button_hover_color="#3F4A63",
                                                            values=("0.5", "1.0", "1.5", "2.0", "2.5", "3.0", "3.5"))
        self.seletor_de_tempo.grid(row=0, column=0, padx=(170, 0), pady=(8, 0), sticky="w")
        self.seletor_de_tempo.configure(
            command=lambda value: self.atualiza_opcoes(self.variavel_opcao, self.salvar_tempo))

    @staticmethod
    def atualiza_opcoes(variavel_opcao, salvar_tempo):
        valor_selecionado = variavel_opcao.get()
        salvar_tempo()

    def salvar_tempo(self):
        pasta_config_tempo = "C:\\AcessoRemoto\\Dados"
        arquivo_config_tempo = os.path.join(pasta_config_tempo, "config.json")

        texto = self.variavel_opcao.get()

        if os.path.exists(arquivo_config_tempo):
            with open(arquivo_config_tempo, "r") as file:
                dados_existente = json.load(file)
        else:
            dados_existente = {}

        dados_existente["tempo"] = texto

        with open(arquivo_config_tempo, "w") as file:
            json.dump(dados_existente, file)

    @staticmethod
    def ler_arquivo_tempo():
        pasta_acesso_remoto = "C:\\AcessoRemoto\\Dados"
        arquivo_config_tempo = os.path.join(pasta_acesso_remoto, "config.json")

        if os.path.exists(arquivo_config_tempo):
            with open(arquivo_config_tempo, "r") as file:
                dados = json.load(file)
            return dados
        return None

    def exibir_tempo(self):
        texto_tempo = self.ler_arquivo_tempo()

        if texto_tempo and "tempo" in texto_tempo:
            tempo_rdp = texto_tempo["tempo"]
            self.seletor_de_tempo.set(tempo_rdp)
            return tempo_rdp

    @staticmethod
    def remover_arquivos_rdp():
        pasta_acesso_remoto = "C:\\AcessoRemoto"
        for arquivo in os.listdir(pasta_acesso_remoto):
            if arquivo.endswith(".rdp"):
                os.remove(os.path.join(pasta_acesso_remoto, arquivo))

    @staticmethod
    def sair():
        FrameSuperior.remover_arquivos_rdp()
        pasta_dados = "C:\\AcessoRemoto\\Dados"
        arquivos_protegidos = ["anotacoes.json", "config.json"]

        for arquivo in os.listdir(pasta_dados):
            if arquivo in arquivos_protegidos:
                continue
            os.remove(os.path.join(pasta_dados, arquivo))
            app.quit()


class FramePrincipal(customtkinter.CTkTabview):
    def __init__(self, master):
        super().__init__(master)
        self.tela_de_informacao = None
        self.CriaInterface = None

        self.add("Favoritos")
        self.add("Anotações")

        self.button_add = customtkinter.CTkButton(master=self.tab("Favoritos"), text="Editar",
                                                  font=("Calibri Bold", 13), command=self.gerenciar_edicao,
                                                  hover_color="#3E3E63", fg_color="#c75416", text_color="white",
                                                  corner_radius=15, width=50, height=25)
        self.button_add.grid(row=0, column=1, padx=(10, 8), pady=10, sticky="e")
        self.camp_fav1 = customtkinter.CTkEntry(master=self.tab("Favoritos"), width=200, height=30)
        self.camp_fav1.grid(row=1, column=1, padx=(10, 5), pady=(10, 5), sticky="e")
        self.camp_fav2 = customtkinter.CTkEntry(master=self.tab("Favoritos"), width=200, height=30)
        self.camp_fav2.grid(row=2, column=1, padx=(10, 5), pady=(5, 5), sticky="e")
        self.camp_fav3 = customtkinter.CTkEntry(master=self.tab("Favoritos"), width=200, height=30)
        self.camp_fav3.grid(row=3, column=1, padx=(10, 5), pady=(5, 5), sticky="e")
        self.button_fav1 = customtkinter.CTkButton(master=self.tab("Favoritos"), text="Conectar",
                                                   command=lambda: self.conectar_favorito(1), fg_color="transparent",
                                                   width=100, height=30)
        self.button_fav1.grid(row=1, column=1, padx=(0, 5), pady=(10, 5), sticky="w")
        self.button_fav2 = customtkinter.CTkButton(master=self.tab("Favoritos"), text="Conectar",
                                                   command=lambda: self.conectar_favorito(2), fg_color="transparent",
                                                   width=100, height=30)
        self.button_fav2.grid(row=2, column=1, padx=(0, 5), pady=(10, 5), sticky="w")
        self.button_fav3 = customtkinter.CTkButton(master=self.tab("Favoritos"), text="Conectar",
                                                   command=lambda: self.conectar_favorito(3), fg_color="transparent",
                                                   width=100, height=30)
        self.button_fav3.grid(row=3, column=1, padx=(0, 5), pady=(10, 5), sticky="w")
        self.info = customtkinter.CTkButton(master=self.tab("Favoritos"), text="?", command=self.informacao, width=20,
                                            height=20,
                                            corner_radius=15, hover_color="#3E3E63", fg_color="#c75416")
        self.info.grid(row=4, column=1, padx=(20, 5), pady=(130, 0), sticky="e")

        self.tab1 = customtkinter.CTkFrame(master=self.tab("Favoritos"), fg_color="transparent", width=330, height=330)
        self.tab1.grid(row=5, column=1, padx=0, pady=(5, 0), sticky="ew")

        self.tab2 = customtkinter.CTkTextbox(master=self.tab("Anotações"), width=330, height=300)
        self.tab2.grid(row=1, column=1, padx=0, pady=(5, 0), sticky="ew")
        self.button_save = customtkinter.CTkButton(master=self.tab("Anotações"), text="Salvar",
                                                   command=self.salvar_anotacoes, font=("Calibri Bold", 15),
                                                   hover_color="#3E3E63", fg_color="#c75416", text_color="white",
                                                   corner_radius=15)
        self.button_save.grid(row=2, column=1, padx=0, pady=(8, 2))

    def informacao(self):
        self.tela_de_informacao = customtkinter.CTkToplevel(self)
        self.tela_de_informacao.title("Informações")
        self.tela_de_informacao.focus_set()
        self.tela_de_informacao.grab_set()
        self.tela_de_informacao.resizable(width=False, height=False)
        self.tela_de_informacao.overrideredirect(True)
<<<<<<< HEAD
        self.versao = '0.0.50'
=======
>>>>>>> 544f86ee3f06642d711208d3e5366242d200598e

        largura_janela = 500
        altura_janela = 180

        # ajuste para aparecer no centro da tela principal
        largura_tela = self.tela_de_informacao.winfo_screenwidth()
        altura_tela = self.tela_de_informacao.winfo_screenheight()
        pos_x = (largura_tela // 2) - (largura_janela // 2)
        pos_y = (altura_tela // 2) - (altura_janela // 2)
        self.tela_de_informacao.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")
        self.frame = customtkinter.CTkFrame(self.tela_de_informacao, width=460, height=115)
        self.frame.grid(row=0, column=0, padx=15, pady=15)

        self.titulo = customtkinter.CTkLabel(self.tela_de_informacao,
<<<<<<< HEAD
                                             text=f"Versão: {self.versao}, desenvolvido por Gabriel Aragão",
=======
                                             text="Versão: 0.0.48, desenvolvido por Gabriel Aragão",
>>>>>>> 544f86ee3f06642d711208d3e5366242d200598e
                                             font=("Calibri", 13), fg_color="#2B2B2B")
        self.titulo.grid(row=0, column=0, padx=15, pady=(0, 50))
        self.dados = customtkinter.CTkLabel(self.tela_de_informacao,
                                            text="Sistema de uso comercial livre, para acesso à licença e ao código, clique",
                                            font=("Calibri", 13), fg_color="#2B2B2B")
        self.dados.grid(row=0, column=0, padx=(0, 25), pady=(30, 0))
        self.hyperlink = customtkinter.CTkLabel(self.tela_de_informacao, text="aqui", text_color="#E4621B",
                                                cursor="hand2", fg_color="#2B2B2B",
                                                font=("Calibri Black", 13))
        self.hyperlink.grid(row=0, column=0, padx=(0, 30), pady=(30, 0), sticky="e")
        self.hyperlink.bind("<Button-1>", lambda event: self.link_licenca())

        self.but_ok = customtkinter.CTkButton(self.tela_de_informacao, text="OK",
                                              command=self.tela_de_informacao.destroy,
                                              corner_radius=15)
        self.but_ok.grid(row=3, column=0, padx=0, pady=0)

        return

    def link_licenca(self):
        self.link = webbrowser.open_new("https://github.com/GabrielGoncalves/AcessoRemoto.git")

    def gerenciar_edicao(self):
        self.cor_texto_padrao = "gray"
        self.cor_fundo_padrao = "gray10"
        self.cor_texto_alternativa = "white"
        self.cor_fundo_alternativa = "#333537"

        if self.button_add.cget("text") == "Editar":
            self.button_add.configure(text="Salvar")
            self.camp_fav1.configure(state="normal", text_color=self.cor_texto_padrao, fg_color=self.cor_fundo_padrao)
            self.camp_fav2.configure(state="normal", text_color=self.cor_texto_padrao, fg_color=self.cor_fundo_padrao)
            self.camp_fav3.configure(state="normal", text_color=self.cor_texto_padrao, fg_color=self.cor_fundo_padrao)
        else:
            self.salvar_favoritos()
            self.button_add.configure(text="Editar")
            self.camp_fav1.configure(state="disabled", text_color=self.cor_texto_alternativa,
                                     fg_color=self.cor_fundo_alternativa)
            self.camp_fav2.configure(state="disabled", text_color=self.cor_texto_alternativa,
                                     fg_color=self.cor_fundo_alternativa)
            self.camp_fav3.configure(state="disabled", text_color=self.cor_texto_alternativa,
                                     fg_color=self.cor_fundo_alternativa)

    def salvar_anotacoes(self):
        pasta_anotacoes = "C:\\AcessoRemoto\\Dados"
        arquivo_anotacoes = os.path.join(pasta_anotacoes, "anotacoes.json")

        texto = self.tab2.get("1.0", "end-1c")

        with open(arquivo_anotacoes, "w") as file:
            json.dump({"anotacoes": texto}, file)

    @staticmethod
    def exibir_anotacoes(self):
        texto_anotacoes = self.ler_arquivo_anotacoes()

        if texto_anotacoes:
            self.tab2.delete(1.0, "end")
            self.tab2.insert("end", texto_anotacoes)

    @staticmethod
    def ler_arquivo_anotacoes():
        pasta_anotacoes = "C:\\AcessoRemoto\\Dados"
        arquivo_anotacoes = os.path.join(pasta_anotacoes, "anotacoes.json")

        if os.path.exists(arquivo_anotacoes):
            with open(arquivo_anotacoes, "r") as file:
                dados = json.load(file)
            return dados['anotacoes']
        return None

    def salvar_favoritos(self):
        pasta_favoritos = "C:\\AcessoRemoto\\Dados"
        arquivo_favoritos = os.path.join(pasta_favoritos, "config.json")

        texto1 = self.camp_fav1.get()
        texto2 = self.camp_fav2.get()
        texto3 = self.camp_fav3.get()

        dados = {
            "fav1": texto1,
            "fav2": texto2,
            "fav3": texto3}

        with open(arquivo_favoritos, "w") as file:
            json.dump(dados, file)

    @staticmethod
    def exibir_favoritos(self):
        dados_favoritos = self.ler_arquivo_favoritos()

        if dados_favoritos:
            if "fav1" in dados_favoritos:
                self.camp_fav1.delete(0, "end")
                self.camp_fav1.insert(0, dados_favoritos["fav1"])
                self.camp_fav1.configure(state="disabled")

            if "fav2" in dados_favoritos:
                self.camp_fav2.delete(0, "end")
                self.camp_fav2.insert(0, dados_favoritos["fav2"])
                self.camp_fav2.configure(state="disabled")

            if "fav3" in dados_favoritos:
                self.camp_fav3.delete(0, "end")
                self.camp_fav3.insert(0, dados_favoritos["fav3"])
                self.camp_fav3.configure(state="disabled")

    @staticmethod
    def ler_arquivo_favoritos():
        pasta_favoritos = "C:\\AcessoRemoto\\Dados"
        arquivo_favoritos = os.path.join(pasta_favoritos, "config.json")

        if os.path.exists(arquivo_favoritos):
            with open(arquivo_favoritos, "r") as file:
                dados = json.load(file)
            return dados
        return None

    def conectar_favorito(self, numero):
        global senha
        if self.frame_lateral:
            usuario = self.frame_lateral.entry_usuario.get()
            senha = self.frame_lateral.entry_senha.get()

            if not (usuario and senha):
                self.CriaInterface.mensagem_de_alertas()
            else:
                if numero == 1:
                    ip = self.camp_fav1.get()
                elif numero == 2:
                    ip = self.camp_fav2.get()
                elif numero == 3:
                    ip = self.camp_fav3.get()
                else:
                    ip = ""

<<<<<<< HEAD
                if ip and ip.startswith("172.16."):
=======
                if ip and ip.startswith("162.78"):
>>>>>>> 544f86ee3f06642d711208d3e5366242d200598e
                    try:
                        self.frame_lateral.remover_aviso_certificado(ip)
                        arquivo_rdp = self.frame_lateral.criar_arquivo_rdp(ip, usuario)
                        subprocess.Popen(['mstsc', arquivo_rdp])
                        app.lower()

                        tempo_rdp = self.Frame_Superior.exibir_tempo()
                        sleep(float(tempo_rdp))
                        pyautogui.write(senha)
                        pyautogui.press("enter")

                    except Exception as e:
                        print(f"Erro ao conectar: {e}")
                else:
                    self.tela_de_notificacao = customtkinter.CTkToplevel(self)
                    self.tela_de_notificacao.title("Informações")
                    self.tela_de_notificacao.focus_set()
                    self.tela_de_notificacao.grab_set()
                    self.tela_de_notificacao.resizable(width=False, height=False)
                    self.tela_de_notificacao.overrideredirect(True)

                    largura_janela = 280
                    altura_janela = 110

                    # ajuste para aparecer no centro da tela principal
                    largura_tela = self.tela_de_notificacao.winfo_screenwidth()
                    altura_tela = self.tela_de_notificacao.winfo_screenheight()
                    pos_x = (largura_tela // 2) - (largura_janela // 2)
                    pos_y = (altura_tela // 2) - (altura_janela // 2)
                    self.tela_de_notificacao.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

                    self.mensagem_fav = customtkinter.CTkLabel(self.tela_de_notificacao,
                                                               text="Favorito não configurado corretamente",
                                                               font=("Calibri", 16))
                    self.mensagem_fav.grid(row=0, column=0, padx=15, pady=20)
                    self.bnt_mensagem_fav = customtkinter.CTkButton(self.tela_de_notificacao, text="OK",
                                                                    command=self.tela_de_notificacao.destroy,
                                                                    corner_radius=15, hover_color="#3E3E63",
                                                                    fg_color="#c75416")
                    self.bnt_mensagem_fav.grid(row=1, column=0, padx=15, pady=(0, 10))


class CriarInterface(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.mensagem = None
        self.title("Acesso Remoto")
        self.geometry("600x440")
        self.resizable(width=False, height=False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.attributes('-alpha', 0.96)
        customtkinter.set_appearance_mode("Dark")

        self.sidebar_frameL = FrameLateral(self)
        self.sidebar_frameL.CriaInterface = self
        self.sidebar_frameL.grid(row=1, column=0, padx=(15, 0), pady=(18, 15), sticky="nsw")
        self.sidebar_frameS = FrameSuperior(self)
        self.sidebar_frameS.grid(row=0, column=0)
        self.sidebar_frameS.configure(fg_color="transparent")
        self.sidebar_frameP = FramePrincipal(self)
        self.sidebar_frameP.CriaInterface = self
        self.sidebar_frameP.frame_lateral = self.sidebar_frameL
        self.sidebar_frameP.configure(segmented_button_selected_color="#c75416",
                                      segmented_button_selected_hover_color="#3E3E63")
        self.sidebar_frameP.grid(row=1, column=1, padx=(5, 15), pady=(0, 15), sticky="nswe")
        self.sidebar_frameL.Frame_Superior = self.sidebar_frameS
        self.sidebar_frameP.Frame_Superior = self.sidebar_frameS

        # chamadas
        self.criar_pastas()
        FramePrincipal.exibir_anotacoes(self.sidebar_frameP)
        FramePrincipal.exibir_favoritos(self.sidebar_frameP)
        FrameSuperior.exibir_tempo(self.sidebar_frameS)

    def mensagem_de_alertas(self):
        self.tela_de_alerta = customtkinter.CTkToplevel(self)
        self.tela_de_alerta.title("AVISO")
        self.tela_de_alerta.focus_set()
        self.tela_de_alerta.grab_set()
        self.tela_de_alerta.resizable(width=False, height=False)
        self.tela_de_alerta.overrideredirect(True)

        largura_janela = 245
        altura_janela = 100

        # ajuste para aparecer no centro da tela principal
        largura_tela = self.tela_de_alerta.winfo_screenwidth()
        altura_tela = self.tela_de_alerta.winfo_screenheight()
        pos_x = (largura_tela // 2) - (largura_janela // 2)
        pos_y = (altura_tela // 2) - (altura_janela // 2)
        self.tela_de_alerta.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

        self.mensagem = customtkinter.CTkLabel(self.tela_de_alerta, text="Revise os dados digitados",
                                               font=("Calibri", 20),
                                               justify="center")
        self.mensagem.grid(row=0, column=0, padx=15, pady=15)
        self.but_ok = customtkinter.CTkButton(self.tela_de_alerta, text="OK", command=self.tela_de_alerta.destroy,
                                              corner_radius=15)
        self.but_ok.grid(row=1, column=0, padx=0, pady=0)
        return

    @staticmethod
    def criar_pastas():
        pasta_acesso_remoto = "C:\\AcessoRemoto\\Dados"

        # Verifica se a pasta não existe
        if not os.path.exists(pasta_acesso_remoto):
            os.makedirs(pasta_acesso_remoto)


if __name__ == "__main__":
    app = CriarInterface()
    app.mainloop()
