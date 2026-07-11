import flet as ft
import ssl

from database.db_manager import DatabaseManager
from core.rdp_engine import RDPAngine
from ui.views.view_dashboard import DashboardView
from ui.views.view_favorites import ViewFavoritos
from ui.views.view_environments import ViewEnvironments
from ui.views.view_settings import ViewSettings
from ui.layout import AppTheme

ssl._create_default_https_context = ssl._create_unverified_context

class MainApplication:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Remote Craft"
        self.page.window.width = 900
        self.page.window.height = 700
        self.db = DatabaseManager()

        tema_salvo = self.db.obter_tema()
        self.page.theme = AppTheme.get_theme(tema_salvo)
        self.page.bgcolor = self.page.theme.color_scheme.surface_container
        self.page.update()

        self.view_dashboard = DashboardView(self.db, on_connect_action=self.disparar_rdp)
        self.view_favorites = ViewFavoritos(self.db)
        self.view_environments = ViewEnvironments(
            db=self.db, 
            on_connect_action=self.disparar_rdp,
            on_redirect_action=self.redirecionar_para_dashboard
        )
        # 1. Instanciando com o self da nova função abaixo
        self.view_settings = ViewSettings(self.db, on_dev_mode_change=self.atualizar_menu_lateral)
        self.view_container = ft.Container(expand=True)
        
        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            on_change=self._nav_changed
        )
        
        # 2. Constrói o menu dinâmico na primeira vez que o app abre
        dev_mode_ativo = self.db.obter_configuracao("modo_desenvolvedor", "0") == "1"
        self.atualizar_menu_lateral(dev_mode_ativo)

        self.build_structure()
        self._carregar_view(0)

    def build_structure(self):
        self.page.add(
            ft.Row([
                self.nav_rail,
                ft.VerticalDivider(width=1, color=ft.Colors.GREY_800),
                self.view_container
            ], expand=True)
        )

    # 3. Nova função que constrói as opções do menu com ou sem a API
    def atualizar_menu_lateral(self, dev_mode_ativo):
        destinations = [
            ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD_OUTLINED, selected_icon=ft.Icons.DASHBOARD, label="Dashboard"),
            ft.NavigationRailDestination(icon=ft.Icons.STAR_BORDER, selected_icon=ft.Icons.STAR, label="Favoritos"),
            ft.NavigationRailDestination(icon=ft.Icons.FOLDER_OUTLINED, selected_icon=ft.Icons.FOLDER, label="Ambientes"),
        ]
        
        if dev_mode_ativo:
            destinations.append(ft.NavigationRailDestination(icon=ft.Icons.ACCOUNT_TREE_OUTLINED, selected_icon=ft.Icons.ACCOUNT_TREE, label="API"))
            
        destinations.extend([
            ft.NavigationRailDestination(icon=ft.CupertinoIcons.GEAR, selected_icon=ft.CupertinoIcons.GEAR_SOLID, label="Configurações"),
            ft.NavigationRailDestination(icon=ft.Icons.INFO_OUTLINE, selected_icon=ft.Icons.INFO, label="Informações")
        ])
        
        self.nav_rail.destinations = destinations
        
        # Só dá update na página se os componentes já estiverem carregados na tela
        if self.page.controls:
            self.page.update()

    def _nav_changed(self, e):
        self._carregar_view(int(e.data))

    def _carregar_view(self, index):
        # 4. Roteamento inteligente independente do número da aba!
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
            pass # Substituiremos por: self.view_container.content = self.view_api
        elif selected_label == "Configurações":
            self.view_container.content = self.view_settings
        elif selected_label == "Informações":
            pass # Substituiremos por: self.view_container.content = self.view_info
            
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