import flet as ft
import ssl

from database.db_manager import DatabaseManager
from core.rdp_engine import RDPAngine
from ui.views.view_dashboard import DashboardView

ssl._create_default_https_context = ssl._create_unverified_context

db = DatabaseManager()
dashboard = DashboardView(db=db, on_connect_action=RDPAngine.executar)

class MainApplication:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Remote Craft"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = "#1a1a2e"
        self.page.window.width = 900
        self.page.window.height = 650

        self.db = DatabaseManager()

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
                ft.NavigationRailDestination(icon=ft.Icons.INFO_OUTLINE, selected_icon=ft.Icons.INFO, label="API")
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
        if index == 0:
            self.view_container.content = DashboardView(self.db, on_connect_action=self.disparar_rdp)
        elif index == 1:
            self.view_container.content = self._criar_view_favoritos()
        self.page.update()

    def _criar_view_favoritos(self):
        lv_favs = ft.ListView(expand=True, spacing=10)
        favs = self.db.listar_ambientes()
        
        for id_, ip, user, data_favoritado in favs:
            lv_favs.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.STAR, color="yellow"),
                        ft.Column([
                            ft.Text(f"IP: {ip}", weight="bold"),
                            ft.Text(f"Usuário: {user}", size=12, color=ft.Colors.GREY_400),
                            ft.Text(f"Data de criação: {data_favoritado}")
                        ])
                    ]),
                    bgcolor="#161623", padding=15, border_radius=10
                )
            )
            
        if not favs:
            lv_favs.controls.append(ft.Text("Nenhuma conexão favoritada ainda.", color=ft.Colors.GREY_500, italic=True))

        return ft.Container(
            content=ft.Column([
                ft.Text("Suas Conexões Favoritas", size=22, weight="bold"),
                ft.Divider(color=ft.Colors.GREY_800),
                lv_favs
            ]), padding=20, expand=True
        )

    def disparar_rdp(self, ip, user, senha):
        self.page.snack_bar = ft.SnackBar(ft.Text(f"Abrindo RDP para {ip}..."), bgcolor="green")
        self.page.snack_bar.open = True
        self.page.update()
        RDPAngine.executar(ip, user, senha)

if __name__ == "__main__":
    ft.run(MainApplication)