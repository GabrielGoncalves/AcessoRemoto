import flet as ft
import ssl

from database.db_manager import DatabaseManager
from core.rdp_engine import RDPAngine
from ui.views.view_dashboard import DashboardView
from ui.views.view_favorites import ViewFavoritos
from ui.views.view_environments import ViewEnvironments
from ui.views.view_settings import ViewSettings

ssl._create_default_https_context = ssl._create_unverified_context

class MainApplication:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Remote Craft"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = "#1a1a2e"
        self.page.window.width = 900
        self.page.window.height = 650

        self.db = DatabaseManager()

        # MELHORIA: Instanciamos as Views uma única vez no construtor para manter o estado dos campos fixos
        self.view_dashboard = DashboardView(self.db, on_connect_action=self.disparar_rdp)
        self.view_favorites = ViewFavoritos(self.db)
        self.view_environments = ViewEnvironments(
            db=self.db, 
            on_connect_action=self.disparar_rdp,
            on_redirect_action=self.redirecionar_para_dashboard  # Injeta a função de redirecionar
        )
        self.view_settings = ViewSettings(self.db)
        self.view_container = ft.Container(expand=True)
        
        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            bgcolor="#161623",
            destinations=[
                ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD_OUTLINED, selected_icon=ft.Icons.DASHBOARD, label="Dashboard"),
                ft.NavigationRailDestination(icon=ft.Icons.STAR_BORDER, selected_icon=ft.Icons.STAR, label="Favoritos"),
                ft.NavigationRailDestination(icon=ft.Icons.FOLDER_OUTLINED, selected_icon=ft.Icons.FOLDER, label="Ambientes"),
                ft.NavigationRailDestination(icon=ft.Icons.ACCOUNT_TREE_OUTLINED, selected_icon=ft.Icons.ACCOUNT_TREE, label="API"),
                ft.NavigationRailDestination(icon=ft.CupertinoIcons.GEAR, selected_icon=ft.CupertinoIcons.GEAR_SOLID, label="Configurações"),
                ft.NavigationRailDestination(icon=ft.Icons.INFO_OUTLINE, selected_icon=ft.Icons.INFO, label="Informações")
            ]
        )
        self.nav_rail.on_change = self._nav_changed

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

    def _nav_changed(self, e):
        self._carregar_view(int(e.data))

    def _carregar_view(self, index):
        # Apenas alteramos o ponteiro do container para a instância existente (preserva dados digitados)
        if index == 0:
            self.view_container.content = self.view_dashboard
        elif index == 1:
            self.view_container.content = self.view_favorites
        elif index == 2:
            self.view_container.content = self.view_environments
        elif index == 4:
            self.view_container.content = self.view_settings
        self.page.update()

    def redirecionar_para_dashboard(self, ip, user):
        """Muda visualmente para a aba Dashboard e injeta os dados do servidor selecionado de forma assíncrona"""
        self.nav_rail.selected_index = 0
        self.view_container.content = self.view_dashboard
        
        # Executa de forma segura a tarefa assíncrona de preenchimento e foco na senha do Dashboard
        self.page.run_task(self.view_dashboard.preencher_form_externo, ip, user)
        self.page.update()

    def disparar_rdp(self, ip, user, senha):
        self.page.snack_bar = ft.SnackBar(ft.Text(f"Abrindo RDP para {ip}..."), bgcolor="green")
        self.page.snack_bar.open = True
        self.page.update()
        RDPAngine.executar(ip, user, senha)

if __name__ == "__main__":
    ft.run(MainApplication)