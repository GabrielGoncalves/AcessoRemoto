import flet as ft
import os
import platform
import urllib.request
import json
from database.db_manager import DatabaseManager
from ui.components.notifications import Notification

VERSAO_ATUAL = "2.0.5-beta"
GITHUB_USER = "GabrielGoncalves"
GITHUB_REPO = "AcessoRemoto"
URL_DOCS = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/tree/v2#README.md"

class ViewInfo(ft.Container):
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db
        self.expand = True
        self.padding = 20
        self.build_ui()

    def build_ui(self):
        self.content = ft.Column([
            ft.Text("Central de Informações e Diagnóstico", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(color=ft.Colors.SECONDARY),
            
            ft.ListView([
                self._criar_card_versao(),
                self._criar_card_diagnostico(),
                self._criar_card_atalhos(),
                self._criar_card_creditos(),
            ], spacing=15, expand=True)
        ], expand=True)

    # ==========================================
    # CARD 1: IDENTIDADE E VERIFICAÇÃO DE VERSÃO
    # ==========================================
    def _criar_card_versao(self):
        so_detectado = platform.system() # 'Darwin' (macOS), 'Windows', 'Linux'
        if so_detectado == "Darwin":
            so_detectado = "macOS"

        # Função assíncrona para abrir a documentação
        async def abrir_documentacao(e):
            await self.page.launch_url(URL_DOCS)

        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.TERMINAL, size=32, color=ft.Colors.PRIMARY),
                        ft.Column([
                            ft.Text("Remote Craft", size=20, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Versão {VERSAO_ATUAL} • Build Estável", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
                        ], spacing=2, expand=True),
                        
                        # Tag visual com o SO detectado
                        ft.Container(
                            content=ft.Text(so_detectado, size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_PRIMARY),
                            bgcolor=ft.Colors.PRIMARY,
                            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                            border_radius=12
                        )
                    ]),
                    ft.Divider(color=ft.Colors.SECONDARY),
                    ft.Text(
                        "Gerenciador moderno e centralizado de conexões de Área de Trabalho Remota (RDP) focado em alta produtividade e organização corporativa.",
                        size=13, color=ft.Colors.ON_SURFACE_VARIANT
                    ),
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    ft.Row([
                        ft.ElevatedButton(
                            "Verificar Atualizações",
                            icon=ft.Icons.UPDATE,
                            bgcolor=ft.Colors.PRIMARY,
                            color=ft.Colors.ON_PRIMARY,
                            on_click=self._verificar_atualizacoes
                        ),
                        ft.OutlinedButton(
                            "Documentação",
                            icon=ft.Icons.MENU_BOOK,
                            on_click=abrir_documentacao
                        )
                    ], spacing=10)
                ]), padding=15
            ), bgcolor=ft.Colors.SURFACE_CONTAINER
        )

    # ==========================================
    # LÓGICA DE VALIDAÇÃO DE VERSÃO ONLINE
    # ==========================================
    async def _verificar_atualizacoes(self, e):
        url_api = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"
        
        try:
            req = urllib.request.Request(url_api, headers={'User-Agent': 'RemoteCraftApp'})
            with urllib.request.urlopen(req, timeout=4) as response:
                dados = json.loads(response.read().decode())
                
                tag_online = dados.get("tag_name", "").replace("v", "").strip()
                url_download = dados.get("html_url", f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases")

                if tag_online and tag_online > VERSAO_ATUAL:
                    Notification.show_info(self.page, f"Nova versão v{tag_online} disponível! Redirecionando para download...")
                    # Como é assíncrono, agora podemos usar o await sem erro
                    await self.page.launch_url(url_download)
                else:
                    Notification.show_success(self.page, "O Remote Craft já está atualizado na versão mais recente!")

        except Exception:
            Notification.show_error(self.page, "Não foi possível consultar as atualizações. Verifique os links ou a conexão com a internet.")

    # ==========================================
    # CARD 2: DIAGNÓSTICO E SAÚDE DO SISTEMA
    # ==========================================
    def _criar_card_diagnostico(self):
        tamanho_db_kb = 0
        if os.path.exists("autordp.db"):
            tamanho_db_kb = round(os.path.getsize("autordp.db") / 1024, 2)

        qtd_favs = len(self.db.listar_favoritos())
        qtd_ambientes = len(self.db.listar_ambientes())
        qtd_users = len(self.db.listar_usuarios())
        qtd_historico = len(self.db.listar_historico(limite=999))

        so_nome = f"{platform.system()} {platform.release()} ({platform.machine()})"
        py_version = platform.python_version()
        flet_version = ft.__version__

        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.HEALTH_AND_SAFETY, color=ft.Colors.PRIMARY),
                        ft.Text("Diagnóstico e Saúde do Sistema", size=16, weight=ft.FontWeight.BOLD)
                    ]),
                    ft.Divider(color=ft.Colors.SECONDARY),
                    
                    ft.ResponsiveRow([
                        ft.Column([
                            ft.Text("Métricas do Banco de Dados", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY),
                            ft.Row([ft.Icon(ft.Icons.STORAGE, size=16), ft.Text(f"Arquivo SQLite: {tamanho_db_kb} KB")]),
                            ft.Row([ft.Icon(ft.Icons.STAR_OUTLINE, size=16), ft.Text(f"Favoritos Salvos: {qtd_favs}")]),
                            ft.Row([ft.Icon(ft.Icons.FOLDER_OUTLINED, size=16), ft.Text(f"Ambientes Cadastrados: {qtd_ambientes}")]),
                            ft.Row([ft.Icon(ft.Icons.PEOPLE_OUTLINE, size=16), ft.Text(f"Identidades/Usuários: {qtd_users}")]),
                            ft.Row([ft.Icon(ft.Icons.HISTORY, size=16), ft.Text(f"Registros no Histórico: {qtd_historico}")]),
                        ], col={"sm": 12, "md": 6}, spacing=6),

                        ft.Column([
                            ft.Text("Ambiente de Execução", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY),
                            ft.Row([ft.Icon(ft.Icons.COMPUTER, size=16), ft.Text(f"S.O.: {so_nome}")]),
                            ft.Row([ft.Icon(ft.Icons.CODE, size=16), ft.Text(f"Python: v{py_version}")]),
                            ft.Row([ft.Icon(ft.Icons.DASHBOARD_CUSTOMIZE, size=16), ft.Text(f"Flet Framework: v{flet_version}")]),
                            ft.Row([ft.Icon(ft.Icons.PLAY_CIRCLE_OUTLINE, size=16), ft.Text("Engine RDP: Ativo / Integrado")]),
                            ft.Row([ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=16, color=ft.Colors.GREEN), ft.Text("Status do Banco: Conectado (OK)", color=ft.Colors.GREEN)]),
                        ], col={"sm": 12, "md": 6}, spacing=6),
                    ], spacing=15)
                ]), padding=15
            ), bgcolor=ft.Colors.SURFACE_CONTAINER
        )

    # ==========================================
    # CARD 3: GUIA RÁPIDO & ATALHOS
    # ==========================================
    def _criar_card_atalhos(self):
        def criar_linha_atalho(tecla: str, descricao: str):
            return ft.Row([
                ft.Container(
                    content=ft.Text(tecla, size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SECONDARY_CONTAINER),
                    bgcolor=ft.Colors.SECONDARY_CONTAINER,
                    padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                    border_radius=6
                ),
                ft.Text(descricao, size=13, color=ft.Colors.ON_SURFACE_VARIANT)
            ], spacing=10)

        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.KEYBOARD, color=ft.Colors.PRIMARY),
                        ft.Text("Guia Rápido e Dicas de Navegação", size=16, weight=ft.FontWeight.BOLD)
                    ]),
                    ft.Divider(color=ft.Colors.SECONDARY),
                    
                    criar_linha_atalho("Enter", "Avança para o próximo campo no formulário ou dispara a conexão RDP no campo de Senha."),
                    criar_linha_atalho("Menu ≡", "Expande ou recolhe o menu lateral para focar mais espaço na tela."),
                    criar_linha_atalho("Ícone > / <", "Minimiza ou expande o painel de conexões recentes no Dashboard."),
                    criar_linha_atalho("Shift + Scroll / Trackpad", "Navega horizontalmente pelas abas de Configurações."),
                    criar_linha_atalho("Identidades Rápidas", "Use o ícone de crachá ao lado do Usuário para preencher credenciais recorrentes em um clique."),
                ], spacing=10), padding=15
            ), bgcolor=ft.Colors.SURFACE_CONTAINER
        )

    # ==========================================
    # CARD 4: CRÉDITOS E LICENÇA
    # ==========================================
    def _criar_card_creditos(self):
        # Função assíncrona para abrir o repositório
        async def abrir_repositorio(e):
            await self.page.launch_url(f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}")

        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.CODE_OFF, color=ft.Colors.PRIMARY),
                        ft.Text("Desenvolvimento e Licenciamento", size=16, weight=ft.FontWeight.BOLD)
                    ]),
                    ft.Divider(color=ft.Colors.SECONDARY),
                    ft.Text("Projetado e mantido por Gabriel Aragão.", size=13, weight=ft.FontWeight.W_500),
                    ft.Row([
                        ft.Text("Licença de Código Aberto:", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                        ft.Container(
                            content=ft.Text("MIT License", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY),
                            border=ft.Border.all(1, ft.Colors.PRIMARY),
                            padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                            border_radius=4
                        )
                    ]),
                    ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                    ft.TextButton(
                        "Acessar Repositório Oficial no GitHub",
                        icon=ft.Icons.OPEN_IN_NEW,
                        on_click=abrir_repositorio
                    )
                ]), padding=15
            ), bgcolor=ft.Colors.SURFACE_CONTAINER
        )