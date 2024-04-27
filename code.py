import getpass
import json
import os
import subprocess
from time import sleep
import customtkinter
import pyautogui
import webbrowser
import atexit
import requests
import html
import secrets
import string
from datetime import datetime


class FrameLateral(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.Frame_Principal = None
        self.CriaInterface = None
        self.FrameSuperior = None

        self.label_titulo = customtkinter.CTkLabel(
            self, text="Acesso Remoto", font=("Calibri Bold", 25), justify="center"
        )
        self.label_titulo.grid(row=5, column=0, padx=30, pady=(18, 10), sticky="ew")
        self.label_ip = customtkinter.CTkLabel(self, text="IP do Servidor:")
        self.label_ip.grid(row=6, column=0, padx=30, pady=(13, 0), sticky="ew")
        self.entry_ip = customtkinter.CTkEntry(self, corner_radius=25, justify="center")
        self.entry_ip.grid(row=7, column=0, padx=5, pady=(13, 0), sticky="ew")
        self.label_usuario = customtkinter.CTkLabel(self, text="Nome de Usuário:")
        self.label_usuario.grid(row=8, column=0, padx=30, pady=(13, 0), sticky="ew")
        self.entry_usuario = customtkinter.CTkEntry(
            self, corner_radius=25, justify="center"
        )
        self.entry_usuario.grid(row=9, column=0, padx=5, pady=(13, 0), sticky="ew")
        self.label_senha = customtkinter.CTkLabel(self, text="Senha:")
        self.label_senha.grid(row=10, column=0, padx=30, pady=(13, 0), sticky="ew")
        self.entry_senha = customtkinter.CTkEntry(
            self, corner_radius=25, show="*", justify="center"
        )
        self.entry_senha.grid(row=11, column=0, padx=5, pady=(13, 0), sticky="ew")
        self.button_conectar = customtkinter.CTkButton(
            self,
            text="Conectar",
            command=self.conectar,
            text_color="white",
            corner_radius=15,
            fg_color="#E4621B",
            hover_color="#3E3E63",
        )
        self.button_conectar.grid(row=12, column=0, padx=30, pady=(15, 0), sticky="ew")

        # Configura o enter para validar a conexão
        self.entry_senha.bind("<Return>", lambda event: self.conectar())
        self.entry_usuario.bind("<Return>", lambda event: self.conectar())
        self.entry_ip.bind("<Return>", lambda event: self.conectar())

    def conectar(self):
        ip = self.entry_ip.get()
        usuario = self.entry_usuario.get()
        senha = self.entry_senha.get()

        if not (ip and usuario and senha):
            self.CriaInterface.mensagem_de_alertas()
        elif ip.startswith("123.32."):  # regra para validação do IP
            try:
                self.remover_aviso_certificado(ip)
                arquivo_rdp = self.criar_arquivo_rdp(ip, usuario)
                subprocess.Popen(["mstsc", arquivo_rdp])
                app.lower()
                self.entry_ip.delete(0, "end")
                self.entry_senha.delete(0, "end")
                self.entry_senha.insert(0, senha)
                self.entry_ip.focus()

            except Exception as e:
                print(f"Erro ao conectar: {e}")

            tempo_rdp = self.Frame_Principal.exibir_tempo()
            sleep(float(tempo_rdp))
            pyautogui.write(senha)
            pyautogui.press("enter")
            self.Frame_Principal.adicionar_botao(ip)
        else:
            self.CriaInterface.mensagem_de_alertas()

    @staticmethod
    def remover_aviso_certificado(ip):
        try:
            subprocess.run(
                'reg add "HKLM\\Software\\Microsoft\\Terminal Server Client" /v AuthenticationLevelOverride /t REG_DWORD /d 0 /f >nul 2>&1',
                shell=True,
            )
            subprocess.run(
                f'reg add "HKCU\\SOFTWARE\\Microsoft\\Terminal Server Client\\LocalDevices" /v "{ip}" /t REG_DWORD /d 0x0000006f /f >nul 2>&1',
                shell=True,
            )
        except Exception as e:
            print(f"Erro ao remover aviso de certificado: {e}")

    @staticmethod
    def criar_arquivo_rdp(ip, usuario):
        pasta_acesso_remoto = "C:\\AcessoRemoto"
        filename = os.path.join(pasta_acesso_remoto, f"{ip}_conexao_remota.rdp")
        with open(filename, "w") as file:
            file.write(f"full address:s:{ip}\n")
            file.write(f"username:s:{usuario}\n")
            file.write("prompt for credentials:i:0\n")

        return filename


class FrameSuperior(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        # faz a exlusão dos arquivo rdp quando finalizar a tela
        atexit.register(self.remover_arquivos_rdp)

    @staticmethod
    def remover_arquivos_rdp():
        pasta_acesso_remoto = "C:\\AcessoRemoto"
        for arquivo in os.listdir(pasta_acesso_remoto):
            if arquivo.endswith(".rdp"):
                os.remove(os.path.join(pasta_acesso_remoto, arquivo))


class FramePrincipal(customtkinter.CTkTabview):
    def __init__(self, master):
        super().__init__(master)
        self.Frame_Principal = None
        self.frame_lateral = None
        self.tela_de_informacao = None
        self.CriaInterface = None
        self.variavel_opcao = customtkinter.StringVar(self)
        self.resultado_ambiente_servidores = customtkinter.StringVar(self)
        self.conexao_ambiente_servidores = customtkinter.StringVar(self)
        self.conexao_servidor_servidores = customtkinter.StringVar(self)

        self.add("Favoritos")
        self.add("Ambiente")
        self.add("Histórico")
        self.add("API")
        self.add("Configurações")

        # tab favoritos
        self.button_edicao_fav_ip = customtkinter.CTkButton(
            master=self.tab("Favoritos"),
            text="Editar IP",
            font=("Calibri Bold", 13),
            command=self.gerenciar_edicao_ip,
            hover_color="#3E3E63",
            fg_color="transparent",
            border_color="#AA4813",
            border_width=1,
            text_color="white",
            corner_radius=15,
            width=50,
            height=25,
        )
        self.button_edicao_fav_ip.grid(
            row=0, column=1, padx=(10, 8), pady=10, sticky="e"
        )
        self.button_edicao_fav_button = customtkinter.CTkButton(
            master=self.tab("Favoritos"),
            text="Editar Descrição",
            font=("Calibri Bold", 13),
            command=self.gerenciar_edicao_button,
            hover_color="#3E3E63",
            fg_color="transparent",
            border_color="#AA4813",
            border_width=1,
            text_color="white",
            corner_radius=15,
            width=50,
            height=25,
        )
        self.button_edicao_fav_button.grid(
            row=0, column=1, padx=(0, 85), pady=10, sticky="e"
        )
        self.button_fav1 = customtkinter.CTkButton(
            master=self.tab("Favoritos"),
            text="Campo 01",
            width=130,
            height=30,
            corner_radius=20,
            command=lambda: self.conectar_favorito(1),
            fg_color="transparent",
            border_color="#2B2B2B",
            hover_color="#3E3E63",
        )
        self.button_fav1.grid(row=1, column=1, padx=(10, 5), pady=(5, 5), sticky="w")
        self.entry_fav1 = customtkinter.CTkEntry(
            master=self.tab("Favoritos"), width=130, height=30, justify="center"
        )
        self.entry_fav1.grid(row=2, column=1, padx=(10, 5), pady=(0, 5), sticky="w")
        self.button_fav2 = customtkinter.CTkButton(
            master=self.tab("Favoritos"),
            text="Campo 02",
            width=130,
            height=30,
            corner_radius=20,
            command=lambda: self.conectar_favorito(2),
            fg_color="transparent",
            border_color="#2B2B2B",
            hover_color="#3E3E63",
        )
        self.button_fav2.grid(row=3, column=1, padx=(10, 5), pady=(10, 5), sticky="w")
        self.entry_fav2 = customtkinter.CTkEntry(
            master=self.tab("Favoritos"), width=130, height=30, justify="center"
        )
        self.entry_fav2.grid(row=4, column=1, padx=(10, 5), pady=(0, 5), sticky="w")
        self.button_fav3 = customtkinter.CTkButton(
            master=self.tab("Favoritos"),
            text="Campo 03",
            width=130,
            height=30,
            corner_radius=20,
            command=lambda: self.conectar_favorito(3),
            fg_color="transparent",
            border_color="#2B2B2B",
            hover_color="#3E3E63",
        )
        self.button_fav3.grid(row=5, column=1, padx=(10, 5), pady=(10, 5), sticky="w")
        self.entry_fav3 = customtkinter.CTkEntry(
            master=self.tab("Favoritos"), width=130, height=30, justify="center"
        )
        self.entry_fav3.grid(row=6, column=1, padx=(10, 5), pady=(0, 5), sticky="w")
        self.button_fav4 = customtkinter.CTkButton(
            master=self.tab("Favoritos"),
            text="Campo 04",
            width=130,
            height=30,
            corner_radius=20,
            command=lambda: self.conectar_favorito(4),
            fg_color="transparent",
            border_color="#2B2B2B",
            hover_color="#3E3E63",
        )
        self.button_fav4.grid(row=7, column=1, padx=(10, 5), pady=(10, 5), sticky="w")
        self.entry_fav4 = customtkinter.CTkEntry(
            master=self.tab("Favoritos"), width=130, height=30, justify="center"
        )
        self.entry_fav4.grid(row=8, column=1, padx=(10, 5), pady=(0, 5), sticky="w")
        self.button_fav5 = customtkinter.CTkButton(
            master=self.tab("Favoritos"),
            text="Campo 05",
            width=130,
            height=30,
            corner_radius=20,
            command=lambda: self.conectar_favorito(5),
            fg_color="transparent",
            border_color="#2B2B2B",
            hover_color="#3E3E63",
        )
        self.button_fav5.grid(row=1, column=1, padx=(10, 5), pady=(5, 5), sticky="e")
        self.entry_fav5 = customtkinter.CTkEntry(
            master=self.tab("Favoritos"), width=130, height=30, justify="center"
        )
        self.entry_fav5.grid(row=2, column=1, padx=(10, 5), pady=(0, 5), sticky="e")
        self.button_fav6 = customtkinter.CTkButton(
            master=self.tab("Favoritos"),
            text="Campo 06",
            width=130,
            height=30,
            corner_radius=20,
            command=lambda: self.conectar_favorito(6),
            fg_color="transparent",
            border_color="#2B2B2B",
            hover_color="#3E3E63",
        )
        self.button_fav6.grid(row=3, column=1, padx=(10, 5), pady=(10, 5), sticky="e")
        self.entry_fav6 = customtkinter.CTkEntry(
            master=self.tab("Favoritos"), width=130, height=30, justify="center"
        )
        self.entry_fav6.grid(row=4, column=1, padx=(10, 5), pady=(0, 5), sticky="e")
        self.button_fav7 = customtkinter.CTkButton(
            master=self.tab("Favoritos"),
            text="Campo 07",
            width=130,
            height=30,
            corner_radius=20,
            command=lambda: self.conectar_favorito(7),
            fg_color="transparent",
            border_color="#2B2B2B",
            hover_color="#3E3E63",
        )
        self.button_fav7.grid(row=5, column=1, padx=(10, 5), pady=(10, 5), sticky="e")
        self.entry_fav7 = customtkinter.CTkEntry(
            master=self.tab("Favoritos"), width=130, height=30, justify="center"
        )
        self.entry_fav7.grid(row=6, column=1, padx=(10, 5), pady=(0, 5), sticky="e")
        self.button_fav8 = customtkinter.CTkButton(
            master=self.tab("Favoritos"),
            text="Campo 08",
            width=130,
            height=30,
            corner_radius=20,
            command=lambda: self.conectar_favorito(8),
            fg_color="transparent",
            border_color="#2B2B2B",
            hover_color="#3E3E63",
        )
        self.button_fav8.grid(row=7, column=1, padx=(10, 5), pady=(10, 5), sticky="e")
        self.entry_fav8 = customtkinter.CTkEntry(
            master=self.tab("Favoritos"), width=130, height=30, justify="center"
        )
        self.entry_fav8.grid(row=8, column=1, padx=(10, 5), pady=(0, 5), sticky="e")
        self.frame_fav = customtkinter.CTkFrame(
            master=self.tab("Favoritos"), fg_color="transparent", width=330, height=330
        )
        self.frame_fav.grid(row=90, column=1, padx=0, pady=(5, 0), sticky="ew")

        # tab servidores
        self.label_servidores_ambiente = customtkinter.CTkLabel(
            master=self.tab("Ambiente"), text="Ambiente:"
        )
        self.label_servidores_ambiente.grid(
            row=0, column=1, padx=(10, 0), pady=(20, 0), sticky="w"
        )
        self.option_conecta_servidores_ambiente = customtkinter.CTkOptionMenu(
            master=self.tab("Ambiente"),
            dropdown_fg_color="#3F5663",
            width=23,
            height=20,
            button_color="#3E3E63",
            fg_color="#3E3E63",
            button_hover_color="#3F4A63",
            values=("Selecione"),
            variable=self.conexao_ambiente_servidores,
            command=self.exibe_conecta_servidor_servidores,
        )
        self.option_conecta_servidores_ambiente.grid(
            row=0, column=1, padx=(20, 65), pady=(20, 0)
        )
        self.label_servidores_servidor = customtkinter.CTkLabel(
            master=self.tab("Ambiente"), text="Servidor:"
        )
        self.label_servidores_servidor.grid(
            row=1, column=1, padx=(10, 0), pady=(0, 0), sticky="w"
        )
        self.option_conecta_servidores_servidor = customtkinter.CTkOptionMenu(
            master=self.tab("Ambiente"),
            dropdown_fg_color="#3F5663",
            width=23,
            height=20,
            button_color="#3E3E63",
            fg_color="#3E3E63",
            button_hover_color="#3F4A63",
            values=[""],
            variable=self.conexao_servidor_servidores,
            command=self.exibe_conecta_servidor_servidores,
        )
        self.option_conecta_servidores_servidor.grid(
            row=1, column=1, padx=(30, 75), pady=(0, 0)
        )
        self.button_servidores_acesso = customtkinter.CTkButton(
            master=self.tab("Ambiente"),
            text="Conectar",
            command=self.conecta_ambiente_servidores,
            font=("Calibri Bold", 13),
            hover_color="#3E3E63",
            fg_color="transparent",
            border_color="#AA4813",
            border_width=1,
            text_color="white",
        )
        self.button_servidores_acesso.grid(row=2, column=1, padx=(0, 0), pady=(10, 10))
        self.label_servidores_separador = customtkinter.CTkLabel(
            master=self.tab("Ambiente"),
            text="CADASTRO DE SERVIDORES",
            text_color="gray",
        )
        self.label_servidores_separador.grid(row=3, column=1, padx=(0, 0), pady=(10, 5))
        self.label_servidores_cadambiente = customtkinter.CTkLabel(
            master=self.tab("Ambiente"), text="Ambiente:"
        )
        self.label_servidores_cadambiente.grid(
            row=4, column=1, padx=(10, 0), pady=(0, 0), sticky="w"
        )
        self.option_servidores_cadambiente = customtkinter.CTkOptionMenu(
            master=self.tab("Ambiente"),
            dropdown_fg_color="#3F5663",
            width=23,
            height=20,
            button_color="#3E3E63",
            fg_color="#3E3E63",
            button_hover_color="#3F4A63",
            values=[""],
            variable=self.resultado_ambiente_servidores,
        )
        self.option_servidores_cadambiente.grid(
            row=4, column=1, padx=(0, 10), pady=(0, 0), sticky="e"
        )
        self.label_servidores_cadnome = customtkinter.CTkLabel(
            master=self.tab("Ambiente"), text="Nome do Servidor:"
        )
        self.label_servidores_cadnome.grid(
            row=5, column=1, padx=(10, 0), pady=(0, 0), sticky="w"
        )
        self.entry_servidores_cadnome = customtkinter.CTkEntry(
            master=self.tab("Ambiente"),
            border_color="#2B2B2B",
            width=200,
            corner_radius=5,
        )
        self.entry_servidores_cadnome.grid(
            row=5, column=1, padx=(0, 10), pady=(0, 0), sticky="e"
        )
        self.label_servidores_cadip = customtkinter.CTkLabel(
            master=self.tab("Ambiente"), text="IP do Servidor:"
        )
        self.label_servidores_cadip.grid(
            row=6, column=1, padx=(10, 0), pady=(0, 0), sticky="w"
        )
        self.entry_servidores_cadip = customtkinter.CTkEntry(
            master=self.tab("Ambiente"),
            border_color="#2B2B2B",
            width=200,
            corner_radius=5,
        )
        self.entry_servidores_cadip.grid(
            row=6, column=1, padx=(0, 10), pady=(0, 0), sticky="e"
        )
        self.button_servidores_cadastrar = customtkinter.CTkButton(
            master=self.tab("Ambiente"),
            text="Salvar",
            width=60,
            height=25,
            command=self.salva_servidor_servidores,
            font=("Calibri Bold", 13),
            hover_color="#3E3E63",
            fg_color="#3E3E63",
            text_color="white",
        )
        self.button_servidores_cadastrar.grid(
            row=7, column=1, padx=(0, 70), pady=(15, 0)
        )
        self.button_servidores_apagar = customtkinter.CTkButton(
            master=self.tab("Ambiente"),
            text="Deletar",
            width=60,
            height=25,
            command=self.deletar_servidor_servidores,
            font=("Calibri Bold", 13),
            hover_color="#3E3E63",
            fg_color="#3E3E63",
            text_color="white",
        )
        self.button_servidores_apagar.grid(row=7, column=1, padx=(70, 0), pady=(15, 0))
        self.button_servidores_lista = customtkinter.CTkButton(
            master=self.tab("Ambiente"),
            text="Listar",
            width=60,
            height=25,
            command=self.listar_servidor_servidores,
            font=("Calibri Bold", 13),
            hover_color="#3E3E63",
            fg_color="#3E3E63",
            text_color="white",
        )
        self.button_servidores_lista.grid(
            row=7, column=1, padx=(0, 30), pady=(15, 0), sticky="e"
        )
        self.button_servidores_atualiza = customtkinter.CTkButton(
            master=self.tab("Ambiente"),
            text="Atualizar",
            width=12,
            height=25,
            command=self.atualiza_ambiente_servidores,
            font=("Calibri Bold", 13),
            hover_color="#3E3E63",
            fg_color="#3E3E63",
            text_color="white",
        )
        self.button_servidores_atualiza.grid(
            row=7, column=1, padx=(30, 0), pady=(15, 0), sticky="w"
        )
        self.button_servidores_cadastrar_ambiente = customtkinter.CTkButton(
            master=self.tab("Ambiente"),
            text="Cadastrar Ambiente",
            command=self.cria_ambiente_servidores,
            font=("Calibri Bold", 13),
            hover_color="#3E3E63",
            fg_color="transparent",
            border_color="#AA4813",
            border_width=1,
            text_color="white",
        )
        self.button_servidores_cadastrar_ambiente.grid(
            row=8, column=1, padx=(5, 0), pady=(15, 5)
        )
        self.label_resultado_cria_servidores = customtkinter.CTkLabel(
            master=self.tab("Ambiente"), text=""
        )
        self.label_resultado_cria_servidores.grid(
            row=9, column=1, padx=(0, 0), pady=(5, 15)
        )
        self.frame_servidores = customtkinter.CTkFrame(
            master=self.tab("Ambiente"), fg_color="transparent", width=330, height=300
        )
        self.frame_servidores.grid(row=10, column=1, padx=0, pady=(5, 0), sticky="ew")

        # tab histórico
        self.label_hist_titulo = customtkinter.CTkLabel(
            master=self.tab("Histórico"),
            text="Histórico de Acesso",
            font=("Calibri Bold", 18),
        )
        self.label_hist_titulo.grid(row=0, column=0, padx=0, pady=0)
        self.scrollable_frame_hist = customtkinter.CTkScrollableFrame(
            master=self.tab("Histórico"), fg_color="transparent", width=308, height=330
        )
        self.scrollable_frame_hist.grid(
            row=1, column=0, padx=0, pady=(5, 0), sticky="nsew"
        )
        self.contador_linhas = 1

        # tab api
        self.button_entrada_api = customtkinter.CTkButton(
            master=self.tab("API"),
            text="Buscar",
            width=20,
            command=self.busca_api,
            corner_radius=7,
            hover_color="#3E3E63",
            fg_color="transparent",
            border_color="#AA4813",
            border_width=1,
            text_color="white",
        )
        self.button_entrada_api.grid(
            row=0, column=1, padx=(17, 0), pady=(10, 0), sticky="w"
        )
        self.button_saida_api = customtkinter.CTkButton(
            master=self.tab("API"),
            text="Limpar",
            width=20,
            command=self.limpa_api,
            corner_radius=7,
            hover_color="#3E3E63",
            fg_color="transparent",
            border_color="#AA4813",
            border_width=1,
            text_color="white",
        )
        self.button_saida_api.grid(
            row=0, column=1, padx=(75, 0), pady=(10, 0), sticky="w"
        )
        self.entry_api = customtkinter.CTkEntry(master=self.tab("API"))
        self.entry_api.grid(row=0, column=1, padx=(0, 15), pady=(10, 0), sticky="e")
        self.textbox_result = customtkinter.CTkTextbox(
            master=self.tab("API"), width=300, height=320, fg_color="gray20"
        )
        self.textbox_result.grid(row=1, column=1, padx=(0, 0), pady=(13, 0))
        self.textbox_result.configure(state="disabled")
        self.tab_api = customtkinter.CTkFrame(
            master=self.tab("API"), fg_color="transparent", width=330, height=300
        )
        self.tab_api.grid(row=9, column=1, padx=0, pady=(5, 0), sticky="ew")
        self.entry_api.bind("<Return>", lambda event: self.busca_api())

        # tab configurações
        self.label_seletor_de_tempo = customtkinter.CTkLabel(
            master=self.tab("Configurações"),
            text="Tempo do login:",
            width=10,
            height=15,
            font=("Calibri", 16),
        )
        self.label_seletor_de_tempo.grid(
            row=0, column=1, padx=(5, 0), pady=(50, 0), sticky="w"
        )
        self.seletor_de_tempo = customtkinter.CTkOptionMenu(
            master=self.tab("Configurações"),
            variable=self.variavel_opcao,
            dropdown_fg_color="#3F5663",
            width=23,
            height=20,
            button_color="#3E3E63",
            fg_color="#3E3E63",
            button_hover_color="#3F4A63",
            values=("0.5", "1.0", "1.5", "2.0", "2.5", "3.0", "3.5"),
        )
        self.seletor_de_tempo.grid(row=0, column=1, padx=(0, 46), pady=(50, 0))
        self.seletor_de_tempo.configure(
            command=lambda value: self.atualiza_opcoes(
                self.variavel_opcao, self.salvar_tempo
            )
        )
        self.bottom_gera_senha = customtkinter.CTkButton(
            master=self.tab("Configurações"),
            text="Gerar Senha",
            width=100,
            height=30,
            font=("Calibri", 16),
            corner_radius=7,
            hover_color="#3E3E63",
            fg_color="transparent",
            border_color="#AA4813",
            border_width=1,
            command=self.gerar_senha,
        )
        self.bottom_gera_senha.grid(
            row=1, column=1, padx=(5, 0), pady=(10, 0), sticky="w"
        )
        self.label_resultado_senha = customtkinter.CTkLabel(
            master=self.tab("Configurações"),
            text="",
            fg_color="gray20",
            width=170,
            height=30,
            corner_radius=5,
            font=("Calibri", 15),
        )
        self.label_resultado_senha.grid(row=1, column=1, padx=(74, 0), pady=(10, 0))
        self.button_pega_senha = customtkinter.CTkButton(
            master=self.tab("Configurações"),
            text="OK",
            width=30,
            height=30,
            font=("Calibri", 13),
            corner_radius=7,
            hover_color="#3E3E63",
            fg_color="transparent",
            border_color="#AA4813",
            border_width=1,
            command=self.pega_senha,
        )
        self.button_pega_senha.grid(
            row=1, column=1, padx=(0, 5), pady=(10, 0), sticky="e"
        )
        self.info_config = customtkinter.CTkButton(
            master=self.tab("Configurações"),
            text="Informações da Versão",
            command=self.informacao,
            width=20,
            height=25,
            corner_radius=7,
            hover_color="#3E3E63",
            fg_color="#AA4813",
            text_color="white",
        )
        self.info_config.grid(row=2, column=1, padx=(15, 0), pady=(220, 0))
        self.frame_config = customtkinter.CTkFrame(
            master=self.tab("Configurações"),
            fg_color="transparent",
            width=330,
            height=300,
        )
        self.frame_config.grid(row=9, column=1, padx=0, pady=(0, 0), sticky="ew")

    def adicionar_botao(self, ip):
        self.button_acesso_hist = customtkinter.CTkButton(
            self.scrollable_frame_hist,
            text=f"{ip}",
            corner_radius=7,
            hover_color="#3E3E63",
            fg_color="transparent",
            width=55,
            border_color="#AA4813",
            border_width=1,
            text_color="white",
            command=self.conecta_Histórico,
        )
        self.button_acesso_hist.grid(
            row=self.contador_linhas, column=0, padx=(5, 5), pady=10, sticky="w"
        )

        data, hora = self.busca_hora_data()
        label_horadata_hist = customtkinter.CTkLabel(
            self.scrollable_frame_hist,
            text=f"Dia: {data} - Hora: {hora}",
            fg_color="transparent",
        )
        label_horadata_hist.grid(
            row=self.contador_linhas, column=1, padx=(0, 0), pady=10, sticky="e"
        )
        self.contador_linhas += 1

    def busca_hora_data(self):
        data_hora_atual = datetime.now()
        data = data_hora_atual.strftime("%d/%m/%Y")
        hora = data_hora_atual.strftime("%H:%M:%S")
        return data, hora

        print("Data formatada:", data)
        print("Hora formatada:", hora)

    def conecta_Histórico(self):
        ip = self.button_acesso_hist.cget("text")

        if self.frame_lateral:
            usuario = self.frame_lateral.entry_usuario.get()
            senha = self.frame_lateral.entry_senha.get()

        if not (ip and usuario and senha):
            self.CriaInterface.mensagem_de_alertas()
        elif ip.startswith("123.32."):  # regra para validação do IP
            try:
                arquivo_rdp = self.frame_lateral.criar_arquivo_rdp(ip, usuario)
                subprocess.Popen(["mstsc", arquivo_rdp])
                app.lower()
            except Exception as e:
                print(f"Erro ao conectar: {e}")

            tempo_rdp = self.exibir_tempo()
            sleep(float(tempo_rdp))
            pyautogui.write(senha)
            pyautogui.press("enter")
            self.adicionar_botao(ip)
        else:
            self.CriaInterface.mensagem_de_alertas()

    def gerar_senha(self, tamanho_min=10, tamanho_max=40):
        tamanho = secrets.randbelow(tamanho_max - tamanho_min + 1) + tamanho_min
        caracteres_especiais = ["@", "#", "*"]
        primeiro_caractere = secrets.choice(string.ascii_letters + string.digits)
        caractere_especial = secrets.choice(caracteres_especiais)
        senha = primeiro_caractere + caractere_especial

        for _ in range(tamanho - 2):
            if senha[-1] in string.ascii_letters + string.digits:
                senha += secrets.choice(
                    string.ascii_letters + "".join(caracteres_especiais) + string.digits
                )
            else:
                senha += secrets.choice(string.ascii_letters + string.digits)
        self.label_resultado_senha.configure(text=senha)

    def pega_senha(self):
        senha = self.label_resultado_senha.cget("text")
        subprocess.run("echo " + senha.strip() + "| clip", shell=True)
        self.label_resultado_senha.configure(text="")

    def conecta_ambiente_servidores(self):
        global senha
        ambiente = self.option_conecta_servidores_ambiente.get()
        id_servidor = self.option_conecta_servidores_servidor.get()

        if self.frame_lateral:
            usuario = self.frame_lateral.entry_usuario.get()
            senha = self.frame_lateral.entry_senha.get()

            if not (usuario and senha and ambiente and id_servidor):
                self.CriaInterface.mensagem_de_alertas()
                return

            ip = None
            arquivo_path = os.path.join(
                "C:\\AcessoRemoto\\Dados\\servidores", f"{ambiente}.json"
            )

            if os.path.exists(arquivo_path):
                with open(arquivo_path, "r") as f:
                    data = json.load(f)

                for servidor, id in data.items():
                    if servidor == id_servidor:
                        ip = id
                        break

            if ip and ip.startswith("123.32."):  # regra para validação do IP
                try:
                    self.frame_lateral.remover_aviso_certificado(ip)
                    arquivo_rdp = self.frame_lateral.criar_arquivo_rdp(ip, usuario)
                    subprocess.Popen(["mstsc", arquivo_rdp])
                    app.lower()
                    tempo_rdp = self.exibir_tempo()
                    sleep(float(tempo_rdp))
                    pyautogui.write(senha)
                    pyautogui.press("enter")
                    self.adicionar_botao(ip)
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
                # Ajuste para aparecer no centro da tela principal
                largura_tela = self.tela_de_notificacao.winfo_screenwidth()
                altura_tela = self.tela_de_notificacao.winfo_screenheight()
                pos_x = (largura_tela // 2) - (largura_janela // 2)
                pos_y = (altura_tela // 2) - (altura_janela // 2)
                self.tela_de_notificacao.geometry(
                    f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}"
                )
                self.mensagem_fav = customtkinter.CTkLabel(
                    self.tela_de_notificacao,
                    text="Ambiente não configurado corretamente",
                    font=("Calibri", 16),
                )
                self.mensagem_fav.grid(row=0, column=0, padx=15, pady=20)
                self.bnt_mensagem_fav = customtkinter.CTkButton(
                    self.tela_de_notificacao,
                    text="OK",
                    command=self.tela_de_notificacao.destroy,
                    corner_radius=15,
                    hover_color="#3E3E63",
                    fg_color="#c75416",
                )
                self.bnt_mensagem_fav.grid(row=1, column=0, padx=15, pady=(0, 10))

    def exibe_conecta_ambiente_servidores(self):
        valores = self.ler_ambiente_servidores()
        self.option_conecta_servidores_ambiente.configure(values=valores)

    def exibe_conecta_servidor_servidores(self, event):
        self.option_conecta_servidores_servidor.configure(values=[""])
        ambiente_selecionado = self.option_conecta_servidores_ambiente.get()
        if ambiente_selecionado:
            arquivo_path = (
                f"C:\\AcessoRemoto\\Dados\\servidores\\{ambiente_selecionado}.json"
            )
            if os.path.exists(arquivo_path):
                with open(arquivo_path, "r") as f:
                    data = json.load(f)
                chaves_servidores = list(data.keys())
                self.option_conecta_servidores_servidor.configure(
                    values=chaves_servidores
                )
            else:
                print(
                    f"Arquivo correspondente ao ambiente '{ambiente_selecionado}' não encontrado."
                )
        else:
            print("Nenhum ambiente selecionado.")

    def cria_ambiente_servidores(self):
        self.cria_ambiente = customtkinter.CTkToplevel(self)
        self.cria_ambiente.title("Cadastro de Ambientes do Ambiente")
        self.cria_ambiente.focus_set()
        self.cria_ambiente.grab_set()
        self.cria_ambiente.resizable(width=False, height=False)
        self.cria_ambiente.grid_columnconfigure(0, weight=1)

        largura_janela = 410
        altura_janela = 260
        largura_tela = self.cria_ambiente.winfo_screenwidth()
        altura_tela = self.cria_ambiente.winfo_screenheight()
        pos_x = (largura_tela // 2) - (largura_janela // 2)
        pos_y = (altura_tela // 2) - (altura_janela // 2)
        self.cria_ambiente.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

        self.label_nome_ambiente = customtkinter.CTkLabel(
            self.cria_ambiente,
            text="Nome do Ambiente:",
            corner_radius=7,
            fg_color="#2B2B2B",
            font=("Calibri", 17),
        )
        self.label_nome_ambiente.grid(
            row=0, column=0, padx=(30, 0), pady=(30, 0), sticky="w"
        )
        self.entry_nome_ambiente = customtkinter.CTkEntry(self.cria_ambiente, width=170)
        self.entry_nome_ambiente.grid(
            row=0, column=0, padx=(0, 30), pady=(30, 0), sticky="e"
        )
        self.button_salvar_ambiente = customtkinter.CTkButton(
            self.cria_ambiente,
            text="Salvar",
            corner_radius=7,
            command=self.salva_ambiente_servidores,
            hover_color="#3E3E63",
            fg_color="#c75416",
        )
        self.button_salvar_ambiente.grid(
            row=1, column=0, padx=(55, 0), pady=(15, 0), sticky="w"
        )
        self.button_apagar_ambiente = customtkinter.CTkButton(
            self.cria_ambiente,
            text="Apagar",
            corner_radius=7,
            command=self.apaga_ambiente_servidores,
            hover_color="#3E3E63",
            fg_color="#c75416",
        )
        self.button_apagar_ambiente.grid(
            row=1, column=0, padx=(0, 55), pady=(15, 0), sticky="e"
        )
        self.label_retorno_ambiente = customtkinter.CTkLabel(
            self.cria_ambiente,
            text="",
            width=390,
            height=130,
            font=("Arial Black", 25),
            fg_color="gray20",
            corner_radius=5,
        )
        self.label_retorno_ambiente.grid(row=2, column=0, padx=(0, 0), pady=(20, 0))
        return

    def salva_ambiente_servidores(self):
        codigo = self.entry_nome_ambiente.get()
        pasta_salva_ambiente = "C:\\AcessoRemoto\\Dados\\servidores"
        arquivo_salva_ambiente = os.path.join(pasta_salva_ambiente, f"{codigo}.json")

        retorno = ""
        cor_texto = ""

        try:
            if os.path.exists(arquivo_salva_ambiente):
                retorno = "Ambiente já criado."
                cor_texto = "#ff8b26"
            else:
                with open(arquivo_salva_ambiente, "w") as file:
                    pass  # Cria um arquivo vazio

                retorno = "Cadastro feito\ncom sucesso!"
                cor_texto = "#42f551"
        except Exception as e:
            print(f"Erro ao salvar ambiente: {e}")
            retorno = "Erro no cadastro,\n verifique os dados digitados."
            cor_texto = "#c70c12"
        self.label_retorno_ambiente.configure(text=retorno, text_color=cor_texto)

    def apaga_ambiente_servidores(self):
        codigo = self.entry_nome_ambiente.get()
        pasta_salva_ambiente = "C:\\AcessoRemoto\\Dados\\servidores"
        arquivo_apaga_ambiente = os.path.join(pasta_salva_ambiente, f"{codigo}.json")

        retorno = ""
        cor_texto = ""

        try:
            if os.path.exists(arquivo_apaga_ambiente):
                os.remove(arquivo_apaga_ambiente)
                retorno = "Ambiente removido \n com sucesso!"
                cor_texto = "#42f551"
            else:
                retorno = "Ambiente não encontrado."
                cor_texto = "#ff8b26"
        except Exception as e:
            print(f"Erro ao remover ambiente: {e}")
            retorno = "Erro ao remover ambiente."
            cor_texto = "#c70c12"

        self.label_retorno_ambiente.configure(text=retorno, text_color=cor_texto)

    @staticmethod
    def ler_ambiente_servidores():
        pasta_servidores = "C:\\AcessoRemoto\\Dados\\servidores"
        nomes_arquivos = []

        if os.path.exists(pasta_servidores):
            arquivos = os.listdir(pasta_servidores)
            for arquivo in arquivos:
                if arquivo.endswith(".json"):
                    nomes_arquivos.append(arquivo[:-5])  # Remove a extensão .json
        return nomes_arquivos

    def exibe_ambiente_servidores(self):
        valores = self.ler_ambiente_servidores()
        self.option_servidores_cadambiente.configure(values=valores)

    def salva_servidor_servidores(self):
        ambiente = self.resultado_ambiente_servidores.get()
        nome = self.entry_servidores_cadnome.get()
        ip = self.entry_servidores_cadip.get()

        nomes_arquivos = self.ler_ambiente_servidores()
        if ambiente in nomes_arquivos:
            arquivo_path = os.path.join(
                "C:\\AcessoRemoto\\Dados\\servidores", f"{ambiente}.json"
            )

            if os.path.exists(arquivo_path) and os.path.getsize(arquivo_path) > 0:
                with open(arquivo_path, "r") as f:
                    data = json.load(f)
            else:
                data = {}

            if nome in data.values() or ip in data.values():
                self.label_resultado_cria_servidores.configure(
                    text=f"O nome '{nome}' ou o IP '{ip}' já existem no arquivo.",
                    text_color="#ff8b26",
                )
                return

            data[nome] = ip

            with open(arquivo_path, "w") as f:
                json.dump(data, f)
            self.entry_servidores_cadip.delete(0, "end")
            self.entry_servidores_cadip.focus()
            self.label_resultado_cria_servidores.configure(
                text=f"Servidor '{nome}' salvo com sucesso.", text_color="#42f551"
            )
        else:
            self.entry_servidores_cadnome.delete(0, "end")
            self.entry_servidores_cadip.delete(0, "end")
            self.entry_servidores_cadnome.focus()
            self.label_resultado_cria_servidores.configure(
                text=f"Arquivo do ambiente '{ambiente}' não encontrado.",
                text_color="#c70c12",
            )

    def deletar_servidor_servidores(self):
        ambiente = self.resultado_ambiente_servidores.get()
        nome = self.entry_servidores_cadnome.get()
        ip = self.entry_servidores_cadip.get()

        nomes_arquivos = self.ler_ambiente_servidores()
        if ambiente in nomes_arquivos:
            arquivo_path = os.path.join(
                "C:\\AcessoRemoto\\Dados\\servidores", f"{ambiente}.json"
            )

            if os.path.exists(arquivo_path) and os.path.getsize(arquivo_path) > 0:
                with open(arquivo_path, "r") as f:
                    data = json.load(f)
            else:
                self.label_resultado_cria_servidores.configure(
                    text=f"Arquivo correspondente ao ambiente '{ambiente}' está vazio.",
                    text_color="#ff8b26",
                )
                return

            if nome not in data and ip not in data.values():
                self.label_resultado_cria_servidores.configure(
                    text=f"O nome '{nome}' ou o IP '{ip}' não existem no arquivo.",
                    text_color="#c70c12",
                )
                return

            for nome_servidor, ip_servidor in list(data.items()):
                if nome_servidor == nome or ip_servidor == ip:
                    del data[nome_servidor]

            with open(arquivo_path, "w") as f:
                json.dump(data, f)

            self.entry_servidores_cadnome.delete(0, "end")
            self.entry_servidores_cadip.delete(0, "end")
            self.entry_servidores_cadnome.focus()
            self.label_resultado_cria_servidores.configure(
                text=f"Servidor {nome} deletado com sucesso.", text_color="#42f551"
            )
        else:
            self.label_resultado_cria_servidores.configure(
                text=f"Arquivo correspondente ao ambiente '{ambiente}' não encontrado.",
                text_color="#ff8b26",
            )

    def listar_servidor_servidores(self):
        diretorio = "C:\\AcessoRemoto\\Dados\\servidores"
        # Lista para armazenar todas as informações dos servidores
        informacoes_servidores = []
        try:
            for arquivo in os.listdir(diretorio):
                if arquivo.endswith(".json"):
                    arquivo_path = os.path.join(diretorio, arquivo)

                    with open(arquivo_path, "r") as f:
                        try:
                            data = json.load(f)
                        except json.JSONDecodeError:
                            continue

                    informacoes_servidores.append(
                        f"Informações do arquivo: {arquivo}\n"
                    )
                    for nome, ip in data.items():
                        informacoes_servidores.append(f"Nome: {nome}, IP: {ip}\n")
                    informacoes_servidores.append("\n")

            if not informacoes_servidores:
                self.label_resultado_cria_servidores.configure(text_color="#ff8b26")
                self.label_resultado_cria_servidores.configure(
                    text="Não foram encontrados arquivos no diretório."
                )
                return

            output_path = os.path.join(
                os.path.expanduser("~"), "Desktop", "todos_os_servidoress.txt"
            )
            with open(output_path, "w") as output_file:
                output_file.writelines(informacoes_servidores)

            self.label_resultado_cria_servidores.configure(text_color="#42f551")
            self.label_resultado_cria_servidores.configure(
                text="Arquivo 'todos_os_servidoress.txt' criado na área de trabalho."
            )

        except Exception as e:
            self.label_resultado_cria_servidores.configure(text_color="#c70c12")
            self.label_resultado_cria_servidores.configure(
                text=f"Ocorreu um erro ao criar o arquivo: {str(e)}"
            )

    def atualiza_ambiente_servidores(self, event=None):
        # ajusta a lista de ambientes e limpa o label do cadastro
        self.option_servidores_cadambiente.configure(values=[])
        self.exibe_ambiente_servidores()
        self.exibe_conecta_ambiente_servidores()
        self.label_resultado_cria_servidores.configure(text="")

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
    def link_licenca():
        link = webbrowser.open_new(
            "https://github.com/GabrielGoncalves/AcessoRemoto.git"
        )

    def informacao(self):
        self.tela_de_informacao = customtkinter.CTkToplevel(self)
        self.tela_de_informacao.title("Informações")
        self.tela_de_informacao.focus_set()
        self.tela_de_informacao.grab_set()
        self.tela_de_informacao.resizable(width=False, height=False)
        self.tela_de_informacao.overrideredirect(True)
        self.versao = "0.3.105"

        largura_janela = 500
        altura_janela = 180

        # ajuste para aparecer no centro da tela principal
        largura_tela = self.tela_de_informacao.winfo_screenwidth()
        altura_tela = self.tela_de_informacao.winfo_screenheight()
        pos_x = (largura_tela // 2) - (largura_janela // 2)
        pos_y = (altura_tela // 2) - (altura_janela // 2)
        self.tela_de_informacao.geometry(
            f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}"
        )
        self.frame = customtkinter.CTkFrame(
            self.tela_de_informacao, width=460, height=115
        )
        self.frame.grid(row=0, column=0, padx=15, pady=15)

        self.titulo = customtkinter.CTkLabel(
            self.tela_de_informacao,
            text=f"Versão: {self.versao}, desenvolvido por Gabriel Aragão",
            font=("Calibri", 13),
            fg_color="#2B2B2B",
        )
        self.titulo.grid(row=0, column=0, padx=15, pady=(0, 50))
        self.dados = customtkinter.CTkLabel(
            self.tela_de_informacao,
            text="Sistema de uso comercial livre, para acesso à licença e ao código, clique",
            font=("Calibri", 13),
            fg_color="#2B2B2B",
        )
        self.dados.grid(row=0, column=0, padx=(0, 25), pady=(30, 0))
        self.hyperlink = customtkinter.CTkLabel(
            self.tela_de_informacao,
            text="aqui",
            text_color="#E4621B",
            cursor="hand2",
            fg_color="#2B2B2B",
            font=("Calibri Black", 13),
        )
        self.hyperlink.grid(row=0, column=0, padx=(0, 30), pady=(30, 0), sticky="e")
        self.hyperlink.bind("<Button-1>", lambda event: self.link_licenca())

        self.but_ok = customtkinter.CTkButton(
            self.tela_de_informacao,
            text="OK",
            command=self.tela_de_informacao.destroy,
            corner_radius=15,
            fg_color="#AA4813",
            hover_color="#3E3E63",
        )
        self.but_ok.grid(row=3, column=0, padx=0, pady=0)

        return

    def limpa_api(self, limpar_entrada=True):
        self.textbox_result.configure(state="normal")
        self.textbox_result.delete("0.0", "end")
        self.textbox_result.configure(state="disabled")

        if limpar_entrada:
            self.entry_api.delete(0, "end")

    def busca_api(self):
        self.limpa_api(limpar_entrada=False)
        self.codigo_pesquisa = self.entry_api.get()
        self.textbox_result.configure(state="normal")

        def inclui_codigo():
            url = ""  # adicionar o url da API
            crm = self.codigo_pesquisa
            codigo = html.escape(crm)

            return codigo, url

        def validar_codigo(codigo):
            if not codigo.isdigit():
                return False

            codigo = codigo.replace(" ", "")

            if len(codigo) == 0:
                return False

            return True

        def gerar_visualizacao(codigo, url):
            resultado = ""
            if validar_codigo(codigo):
                api = url + codigo
                response = requests.get(api)

                if response.status_code == 200:
                    data = response.json()
                    for item in data:
                        # Conversão dos dados
                        date_backup = datetime.strptime(
                            item["dateBackup"], "%Y-%m-%dT%H:%M:%S.%fZ"
                        )
                        date_upload = datetime.strptime(
                            item["dateUpload"], "%Y-%m-%dT%H:%M:%S.%fZ"
                        )
                        # Conversão para o formato pt-BR
                        date_backup_br = date_backup.strftime("%d/%m/%Y %H:%M:%S")
                        date_upload_br = date_upload.strftime("%d/%m/%Y %H:%M:%S")
                        # Sanitiza a saída antes de exibir
                        basename = html.escape(item["basename"])
                        resultado += f"Nome do arquivo: {basename}\n"
                        resultado += f"Data do backup: {date_backup_br}\n"
                        resultado += f"Data do upload: {date_upload_br}\n"
                        resultado += f"----------------------------------------------------------\n\n"
                else:
                    resultado = f"Erro ao consultar a API. Código de status: {response.status_code}"
            else:
                resultado = "Código inválido, verifique o código digitado."

            return resultado

        codigo, url = inclui_codigo()
        resultado = gerar_visualizacao(codigo, url)
        self.textbox_result.insert("0.0", resultado)
        self.textbox_result.configure(state="disabled")

    def gerenciar_edicao_button(self):
        self.frame_edit_button = customtkinter.CTkToplevel(self)
        self.frame_edit_button.title("Edição da Descrição")
        self.frame_edit_button.focus_set()
        self.frame_edit_button.grab_set()
        self.frame_edit_button.resizable(width=False, height=False)
        self.frame_edit_button.grid_columnconfigure(0, weight=1)
        self.frame_edit_button.attributes("-alpha", 0.96)

        largura_janela = 480
        altura_janela = 430

        largura_tela = self.frame_edit_button.winfo_screenwidth()
        altura_tela = self.frame_edit_button.winfo_screenheight()
        pos_x = (largura_tela // 2) - (largura_janela // 2)
        pos_y = (altura_tela // 2) - (altura_janela // 2)
        self.frame_edit_button.geometry(
            f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}"
        )

        campos = [
            "Campo 1",
            "Campo 2",
            "Campo 3",
            "Campo 4",
            "Campo 5",
            "Campo 6",
            "Campo 7",
            "Campo 8",
        ]
        posicoes = [(0, 0), (2, 0), (4, 0), (6, 0), (0, 0), (2, 0), (4, 0), (6, 0)]
        sticky_posicoes = ["w", "w", "w", "w", "e", "e", "e", "e"]

        for i in range(8):
            label = customtkinter.CTkLabel(
                self.frame_edit_button, text=campos[i], width=200, justify="center"
            )
            label.grid(
                row=posicoes[i][0],
                column=posicoes[i][1],
                padx=15,
                pady=(15, 5),
                sticky=sticky_posicoes[i],
            )

            entry = customtkinter.CTkEntry(self.frame_edit_button, width=200)
            entry.grid(
                row=posicoes[i][0] + 1,
                column=posicoes[i][1],
                padx=15,
                pady=5,
                sticky=sticky_posicoes[i],
            )
            setattr(self, f"entry_edit_button{i+1}", entry)

        self.button_edit_button = customtkinter.CTkButton(
            self.frame_edit_button,
            text="Salvar",
            corner_radius=7,
            command=self.alterar_edit_button,
            fg_color="#AA4813",
            hover_color="#3E3E63",
        )
        self.button_edit_button.grid(row=8, column=0, padx=0, pady=(20, 5))

    def alterar_edit_button(self):
        valores_campos = [
            entry.get()
            for entry in (
                self.entry_edit_button1,
                self.entry_edit_button2,
                self.entry_edit_button3,
                self.entry_edit_button4,
                self.entry_edit_button5,
                self.entry_edit_button6,
                self.entry_edit_button7,
                self.entry_edit_button8,
            )
        ]

        # Atualiza o texto dos botões apenas para os campos não vazios
        for i, valor in enumerate(valores_campos):
            if valor:
                getattr(self, f"button_fav{i+1}").configure(text=valor)

        self.salvar_button_fav()
        self.frame_edit_button.destroy()

    @staticmethod
    def exibir_button_favoritos(self):
        dados_favoritos = self.ler_arquivo_favoritos()

        if dados_favoritos:
            if "button_fav1" in dados_favoritos:
                self.button_fav1.configure(text=dados_favoritos["button_fav1"])
            if "button_fav2" in dados_favoritos:
                self.button_fav2.configure(text=dados_favoritos["button_fav2"])
            if "button_fav3" in dados_favoritos:
                self.button_fav3.configure(text=dados_favoritos["button_fav3"])
            if "button_fav4" in dados_favoritos:
                self.button_fav4.configure(text=dados_favoritos["button_fav4"])
            if "button_fav5" in dados_favoritos:
                self.button_fav5.configure(text=dados_favoritos["button_fav5"])
            if "button_fav6" in dados_favoritos:
                self.button_fav6.configure(text=dados_favoritos["button_fav6"])
            if "button_fav7" in dados_favoritos:
                self.button_fav7.configure(text=dados_favoritos["button_fav7"])
            if "button_fav8" in dados_favoritos:
                self.button_fav8.configure(text=dados_favoritos["button_fav8"])

    def salvar_button_fav(self):
        pasta_favoritos = "C:\\AcessoRemoto\\Dados"
        arquivo_favoritos = os.path.join(pasta_favoritos, "favoritos.json")

        # Lendo o conteúdo atual do arquivo JSON, se existir
        dados_existentes = {}
        if os.path.exists(arquivo_favoritos):
            with open(arquivo_favoritos, "r") as file:
                dados_existentes = json.load(file)

        # Obtendo os novos dados dos botões
        novos_dados = {
            "button_fav1": self.button_fav1.cget("text"),
            "button_fav2": self.button_fav2.cget("text"),
            "button_fav3": self.button_fav3.cget("text"),
            "button_fav4": self.button_fav4.cget("text"),
            "button_fav5": self.button_fav5.cget("text"),
            "button_fav6": self.button_fav6.cget("text"),
            "button_fav7": self.button_fav7.cget("text"),
            "button_fav8": self.button_fav8.cget("text"),
        }

        # Mesclando os dados existentes com os novos dados
        dados_completos = {**dados_existentes, **novos_dados}

        # Escrevendo os dados combinados de volta no arquivo JSON
        with open(arquivo_favoritos, "w") as file:
            json.dump(dados_completos, file)

    def gerenciar_edicao_ip(self):
        self.cor_texto_padrao = "gray"
        self.cor_fundo_padrao = "gray10"
        self.cor_texto_alternativa = "white"
        self.cor_fundo_alternativa = "#333537"

        if self.button_edicao_fav_ip.cget("text") == "Editar IP":
            self.button_edicao_fav_ip.configure(text="Salvar")
            self.entry_fav1.configure(
                state="normal",
                text_color=self.cor_texto_padrao,
                fg_color=self.cor_fundo_padrao,
            )
            self.entry_fav2.configure(
                state="normal",
                text_color=self.cor_texto_padrao,
                fg_color=self.cor_fundo_padrao,
            )
            self.entry_fav3.configure(
                state="normal",
                text_color=self.cor_texto_padrao,
                fg_color=self.cor_fundo_padrao,
            )
            self.entry_fav4.configure(
                state="normal",
                text_color=self.cor_texto_padrao,
                fg_color=self.cor_fundo_padrao,
            )
            self.entry_fav5.configure(
                state="normal",
                text_color=self.cor_texto_padrao,
                fg_color=self.cor_fundo_padrao,
            )
            self.entry_fav6.configure(
                state="normal",
                text_color=self.cor_texto_padrao,
                fg_color=self.cor_fundo_padrao,
            )
            self.entry_fav7.configure(
                state="normal",
                text_color=self.cor_texto_padrao,
                fg_color=self.cor_fundo_padrao,
            )
            self.entry_fav8.configure(
                state="normal",
                text_color=self.cor_texto_padrao,
                fg_color=self.cor_fundo_padrao,
            )
        else:
            self.salvar_favoritos()
            self.button_edicao_fav_ip.configure(text="Editar IP")
            self.entry_fav1.configure(
                state="disabled",
                text_color=self.cor_texto_alternativa,
                fg_color=self.cor_fundo_alternativa,
            )
            self.entry_fav2.configure(
                state="disabled",
                text_color=self.cor_texto_alternativa,
                fg_color=self.cor_fundo_alternativa,
            )
            self.entry_fav3.configure(
                state="disabled",
                text_color=self.cor_texto_alternativa,
                fg_color=self.cor_fundo_alternativa,
            )
            self.entry_fav4.configure(
                state="disabled",
                text_color=self.cor_texto_alternativa,
                fg_color=self.cor_fundo_alternativa,
            )
            self.entry_fav5.configure(
                state="disabled",
                text_color=self.cor_texto_alternativa,
                fg_color=self.cor_fundo_alternativa,
            )
            self.entry_fav6.configure(
                state="disabled",
                text_color=self.cor_texto_alternativa,
                fg_color=self.cor_fundo_alternativa,
            )
            self.entry_fav7.configure(
                state="disabled",
                text_color=self.cor_texto_alternativa,
                fg_color=self.cor_fundo_alternativa,
            )
            self.entry_fav8.configure(
                state="disabled",
                text_color=self.cor_texto_alternativa,
                fg_color=self.cor_fundo_alternativa,
            )

    def salvar_favoritos(self):
        pasta_favoritos = "C:\\AcessoRemoto\\Dados"
        arquivo_favoritos = os.path.join(pasta_favoritos, "favoritos.json")

        texto1 = self.entry_fav1.get()
        texto2 = self.entry_fav2.get()
        texto3 = self.entry_fav3.get()
        texto4 = self.entry_fav4.get()
        texto5 = self.entry_fav5.get()
        texto6 = self.entry_fav6.get()
        texto7 = self.entry_fav7.get()
        texto8 = self.entry_fav8.get()

        dados = {
            "fav1": texto1,
            "fav2": texto2,
            "fav3": texto3,
            "fav4": texto4,
            "fav5": texto5,
            "fav6": texto6,
            "fav7": texto7,
            "fav8": texto8,
        }

        with open(arquivo_favoritos, "w") as file:
            json.dump(dados, file)

    @staticmethod
    def exibir_favoritos(self):
        dados_favoritos = self.ler_arquivo_favoritos()

        if dados_favoritos:
            if "fav1" in dados_favoritos:
                self.entry_fav1.delete(0, "end")
                self.entry_fav1.insert(0, dados_favoritos["fav1"])
                self.entry_fav1.configure(state="disabled")

            if "fav2" in dados_favoritos:
                self.entry_fav2.delete(0, "end")
                self.entry_fav2.insert(0, dados_favoritos["fav2"])
                self.entry_fav2.configure(state="disabled")

            if "fav3" in dados_favoritos:
                self.entry_fav3.delete(0, "end")
                self.entry_fav3.insert(0, dados_favoritos["fav3"])
                self.entry_fav3.configure(state="disabled")

            if "fav4" in dados_favoritos:
                self.entry_fav4.delete(0, "end")
                self.entry_fav4.insert(0, dados_favoritos["fav4"])
                self.entry_fav4.configure(state="disabled")

            if "fav5" in dados_favoritos:
                self.entry_fav5.delete(0, "end")
                self.entry_fav5.insert(0, dados_favoritos["fav5"])
                self.entry_fav5.configure(state="disabled")

            if "fav6" in dados_favoritos:
                self.entry_fav6.delete(0, "end")
                self.entry_fav6.insert(0, dados_favoritos["fav6"])
                self.entry_fav6.configure(state="disabled")

            if "fav7" in dados_favoritos:
                self.entry_fav7.delete(0, "end")
                self.entry_fav7.insert(0, dados_favoritos["fav7"])
                self.entry_fav7.configure(state="disabled")

            if "fav8" in dados_favoritos:
                self.entry_fav8.delete(0, "end")
                self.entry_fav8.insert(0, dados_favoritos["fav8"])
                self.entry_fav8.configure(state="disabled")

    @staticmethod
    def ler_arquivo_favoritos():
        pasta_favoritos = "C:\\AcessoRemoto\\Dados"
        arquivo_favoritos = os.path.join(pasta_favoritos, "favoritos.json")

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
                    ip = self.entry_fav1.get()
                elif numero == 2:
                    ip = self.entry_fav2.get()
                elif numero == 3:
                    ip = self.entry_fav3.get()
                elif numero == 4:
                    ip = self.entry_fav4.get()
                elif numero == 5:
                    ip = self.entry_fav5.get()
                elif numero == 6:
                    ip = self.entry_fav6.get()
                elif numero == 7:
                    ip = self.entry_fav7.get()
                elif numero == 8:
                    ip = self.entry_fav8.get()
                else:
                    ip = ""

                if ip and ip.startswith("123.32."):  # regra para validação do IP
                    try:
                        self.frame_lateral.remover_aviso_certificado(ip)
                        arquivo_rdp = self.frame_lateral.criar_arquivo_rdp(ip, usuario)
                        subprocess.Popen(["mstsc", arquivo_rdp])
                        app.lower()

                        tempo_rdp = self.exibir_tempo()
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
                    self.tela_de_notificacao.geometry(
                        f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}"
                    )

                    self.mensagem_fav = customtkinter.CTkLabel(
                        self.tela_de_notificacao,
                        text="Favorito não configurado corretamente",
                        font=("Calibri", 16),
                    )
                    self.mensagem_fav.grid(row=0, column=0, padx=15, pady=20)
                    self.bnt_mensagem_fav = customtkinter.CTkButton(
                        self.tela_de_notificacao,
                        text="OK",
                        command=self.tela_de_notificacao.destroy,
                        corner_radius=15,
                        hover_color="#3E3E63",
                        fg_color="#c75416",
                    )
                    self.bnt_mensagem_fav.grid(row=1, column=0, padx=15, pady=(0, 10))


class CriarInterface(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.mensagem = None
        self.title("RemoteCraft")
        self.geometry("600x440")
        self.resizable(width=False, height=False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.attributes("-alpha", 0.96)
        customtkinter.set_appearance_mode("dark")

        self.sidebar_frameL = FrameLateral(self)
        self.sidebar_frameL.CriaInterface = self
        self.sidebar_frameL.grid(
            row=1, column=0, padx=(15, 0), pady=(18, 15), sticky="nsw"
        )
        self.sidebar_frameS = FrameSuperior(self)
        self.sidebar_frameS.configure(fg_color="transparent")
        self.sidebar_frameP = FramePrincipal(self)
        self.sidebar_frameP.CriaInterface = self
        self.sidebar_frameP.frame_lateral = self.sidebar_frameL
        self.sidebar_frameP.configure(
            segmented_button_selected_color="#AA4813",
            segmented_button_selected_hover_color="#3E3E63",
        )
        self.sidebar_frameP.grid(
            row=1, column=1, padx=(5, 15), pady=(0, 15), sticky="nswe"
        )
        self.sidebar_frameL.Frame_Principal = self.sidebar_frameP

        # chamadas
        self.criar_pastas()
        FramePrincipal.exibir_favoritos(self.sidebar_frameP)
        FramePrincipal.exibir_button_favoritos(self.sidebar_frameP)
        FramePrincipal.exibir_tempo(self.sidebar_frameP)
        FramePrincipal.exibe_ambiente_servidores(self.sidebar_frameP)
        FramePrincipal.exibe_conecta_ambiente_servidores(self.sidebar_frameP)

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
        self.tela_de_alerta.geometry(
            f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}"
        )

        self.mensagem = customtkinter.CTkLabel(
            self.tela_de_alerta,
            text="Revise os dados digitados",
            font=("Calibri", 20),
            justify="center",
        )
        self.mensagem.grid(row=0, column=0, padx=15, pady=15)
        self.but_ok = customtkinter.CTkButton(
            self.tela_de_alerta,
            text="OK",
            command=self.tela_de_alerta.destroy,
            corner_radius=15,
            fg_color="#AA4813",
            hover_color="#3E3E63",
        )
        self.but_ok.grid(row=1, column=0, padx=0, pady=0)
        return

    @staticmethod
    def criar_pastas():
        pasta_acesso_remoto = "C:\\AcessoRemoto\\Dados"
        pasta_servidores = "C:\\AcessoRemoto\\Dados\\servidores"

        paths = [pasta_acesso_remoto, pasta_servidores]
        for path in paths:
            if not os.path.exists(path):
                os.makedirs(path)


if __name__ == "__main__":
    app = CriarInterface()
    app.mainloop()
