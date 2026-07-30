import flet as ft
import ssl

from database.db_manager import DatabaseManager
from core.rdp_engine import RDPAngine
from services.window_service import WindowService
from ui.views.view_dashboard import DashboardView
from ui.views.view_favorites import ViewFavoritos
from ui.views.view_environments import ViewEnvironments
from ui.views.view_settings import ViewSettings
from ui.views.view_api import ViewAPI
from ui.views.view_info import ViewInfo
from ui.layout import AppTheme

ssl._create_default_https_context = ssl._create_unverified_context

class MainApplication:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "RemoteDesk"
        self.db = DatabaseManager()
        window_service = WindowService(page, self.db)
        window_service.inicializar_janela()

        # Limpeza por retenção de histórico
        dias_retencao = int(self.db.obter_configuracao("retencao_historico_dias", "0"))
        self.db.limpar_historico_por_retencao(dias_retencao)

        # Configuração de Tema
        tema_salvo = self.db.obter_tema()
        tema_obj, tema_modo = AppTheme.get_theme(tema_salvo)
        self.page.theme = tema_obj
        self.page.theme_mode = tema_modo
        self.page.bgcolor = self.page.theme.color_scheme.surface_container

        # Consulta se o menu deve nascer recolhido segundo as preferências do banco
        nav_recolhido = self.db.obter_configuracao("nav_rail_iniciar_recolhido", "0") == "1"

        # Instanciação Única do NavigationRail
        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            extended=not nav_recolhido,
            label_type=ft.NavigationRailLabelType.NONE,
            min_width=50,
            min_extended_width=150,
            bgcolor=ft.Colors.TRANSPARENT,
            leading=ft.IconButton(icon=ft.Icons.MENU, on_click=self._toggle_nav_rail),
            on_change=self._nav_changed
        )

        # Instanciação das Views
        self.view_dashboard = DashboardView(self.db, on_connect_action=self.disparar_rdp)
        self.view_favorites = ViewFavoritos(self.db)
        self.view_environments = ViewEnvironments(
            db=self.db, 
            on_connect_action=self.disparar_rdp,
            on_redirect_action=self.redirecionar_para_dashboard
        )
        self.view_api = ViewAPI(self.db) 
        self.view_settings = ViewSettings(
            self.db, 
            window_service=window_service, 
            on_dev_mode_change=self.atualizar_menu_lateral
        )
        self.view_info = ViewInfo(self.db)
        
        self.view_container = ft.Container(expand=True)

        # Montagem do Layout
        self.atualizar_menu_lateral()
        self.build_structure()
        self._carregar_view(0)
    
    def _toggle_nav_rail(self, e):
        """Alterna entre o menu expandido (com texto) e o compactado (apenas ícones)"""
        self.nav_rail.extended = not self.nav_rail.extended
        self.page.update()

    def build_structure(self):
        self.page.add(
            ft.Row([
                self.nav_rail,
                ft.VerticalDivider(width=1, color=ft.Colors.GREY_800),
                self.view_container
            ], expand=True)
        )

    def atualizar_menu_lateral(self):
        api_module_ativo = self.db.obter_configuracao("modulo_api_ativo", "0") == "1"
        destinations = [
            ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD_OUTLINED, selected_icon=ft.Icons.DASHBOARD, label="Dashboard"),
            ft.NavigationRailDestination(icon=ft.Icons.STAR_BORDER, selected_icon=ft.Icons.STAR, label="Favoritos"),
            ft.NavigationRailDestination(icon=ft.Icons.FOLDER_OUTLINED, selected_icon=ft.Icons.FOLDER, label="Ambientes"),
        ]
        
        if api_module_ativo:
            destinations.append(ft.NavigationRailDestination(icon=ft.Icons.ACCOUNT_TREE_OUTLINED, selected_icon=ft.Icons.ACCOUNT_TREE, label="API"))
            
        destinations.extend([
            ft.NavigationRailDestination(icon=ft.CupertinoIcons.GEAR, selected_icon=ft.CupertinoIcons.GEAR_SOLID, label="Configurações"),
            ft.NavigationRailDestination(icon=ft.Icons.INFO_OUTLINE, selected_icon=ft.Icons.INFO, label="Informações")
        ])
        
        self.nav_rail.destinations = destinations
        if self.page.controls:
            self.page.update()

    def _nav_changed(self, e):
        self._carregar_view(int(e.data))

    def _carregar_view(self, index):
        try:
            selected_label = self.nav_rail.destinations[index].label
        except IndexError:
            return

        if selected_label == "Dashboard":
            self.view_container.content = self.view_dashboard
        elif selected_label == "Favoritos":
            self.view_container.content = self.view_favorites
        elif selected_label == "Ambientes":
            self.view_container.content = self.view_environments
        elif selected_label == "API":
            self.view_container.content = self.view_api
        elif selected_label == "Configurações":
            self.view_container.content = self.view_settings
        elif selected_label == "Informações":
            self.view_container.content = self.view_info
            
        self.page.update()

    async def redirecionar_para_dashboard(self, ip, user):
        conectou_direto = await self.view_dashboard.preencher_form_externo(ip, user)
        
        if not conectou_direto:
            self.nav_rail.selected_index = 0
            self.view_container.content = self.view_dashboard
            self.page.update()
            await self.view_dashboard.txt_pass.focus()

    def disparar_rdp(self, ip, user, senha):
        self.page.snack_bar = ft.SnackBar(ft.Text(f"Abrindo RDP para {ip}..."), bgcolor="green")
        self.page.snack_bar.open = True
        self.page.update()
        RDPAngine.executar(ip, user, senha)

if __name__ == "__main__":
    ft.run(MainApplication)