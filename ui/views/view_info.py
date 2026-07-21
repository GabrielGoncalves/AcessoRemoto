import flet as ft
import os
import sys
import platform
from database.db_manager import DatabaseManager

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
    # CARD 1: IDENTIDADE E VERSÃO
    # ==========================================
    def _criar_card_versao(self):
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.TERMINAL, size=32, color=ft.Colors.PRIMARY),
                        ft.Column([
                            ft.Text("Remote Craft", size=20, weight=ft.FontWeight.BOLD),
                            ft.Text("Versão 1.2.0 • Build Estável", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
                        ], spacing=2, expand=True),
                        ft.Container(
                            content=ft.Text("Sistema Operacional", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_PRIMARY),
                            bgcolor=ft.Colors.PRIMARY,
                            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                            border_radius=12
                        )
                    ]),
                    ft.Divider(color=ft.Colors.SECONDARY),
                    ft.Text(
                        "Gerenciador moderno e centralizado de conexões de Área de Trabalho Remota (RDP) focado em alta produtividade e organização corporativa.",
                        size=13, color=ft.Colors.ON_SURFACE_VARIANT
                    )
                ]), padding=15
            ), bgcolor=ft.Colors.SURFACE_CONTAINER
        )

    # ==========================================
    # CARD 2: DIAGNÓSTICO E SAÚDE DO SISTEMA
    # ==========================================
    def _criar_card_diagnostico(self):
        # 1. Coleta dados do banco
        tamanho_db_kb = 0
        if os.path.exists("autordp.db"):
            tamanho_db_kb = round(os.path.getsize("autordp.db") / 1024, 2)

        qtd_favs = len(self.db.listar_favoritos())
        qtd_ambientes = len(self.db.listar_ambientes())
        qtd_users = len(self.db.listar_usuarios())
        qtd_historico = len(self.db.listar_historico(limite=999))

        # 2. Coleta dados do sistema
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
                        # Coluna do Banco de Dados
                        ft.Column([
                            ft.Text("Métricas do Banco de Dados", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY),
                            ft.Row([ft.Icon(ft.Icons.STORAGE, size=16), ft.Text(f"Arquivo SQLite: {tamanho_db_kb} KB")]),
                            ft.Row([ft.Icon(ft.Icons.STAR_OUTLINE, size=16), ft.Text(f"Favoritos Salvos: {qtd_favs}")]),
                            ft.Row([ft.Icon(ft.Icons.FOLDER_OUTLINED, size=16), ft.Text(f"Ambientes Cadastrados: {qtd_ambientes}")]),
                            ft.Row([ft.Icon(ft.Icons.PEOPLE_OUTLINE, size=16), ft.Text(f"Identidades/Usuários: {qtd_users}")]),
                            ft.Row([ft.Icon(ft.Icons.HISTORY, size=16), ft.Text(f"Registros no Histórico: {qtd_historico}")]),
                        ], col={"sm": 12, "md": 6}, spacing=6),

                        # Coluna do Executável e Engine
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
    # CARD 4: CRÉDITOS E SUPORTE
    # ==========================================
    def _criar_card_creditos(self):
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.INFO_OUTLINE, color=ft.Colors.PRIMARY),
                        ft.Text("Créditos e Suporte", size=16, weight=ft.FontWeight.BOLD)
                    ]),
                    ft.Divider(color=ft.Colors.SECONDARY),
                    ft.Text("Remote Craft • Desenvolvido com Python & Flet UI Engine.", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Text("Licença: Uso Corporativo / Pessoal.", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
                ]), padding=15
            ), bgcolor=ft.Colors.SURFACE_CONTAINER
        )