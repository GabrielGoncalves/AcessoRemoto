import flet as ft
from database.db_manager import DatabaseManager
from ui.components.modal_favorites import ModalNovoFavorito

class ViewFavoritos(ft.Container):
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db
        self.expand = True
        self.padding = 20 
        
        self.lista_favoritos = ft.ListView(expand=True, spacing=10)
        
        # Instanciando o Modal isolado e passando a função de recarregar a lista como callback
        self.modal_cadastro = ModalNovoFavorito(db=self.db, on_success_callback=self.carregar_lista)
        
        self.build_ui()

    def build_ui(self):
        self.content = ft.Column([
            ft.Row([
                ft.Text("Meus Favoritos", size=24, weight=ft.FontWeight.BOLD),
                ft.ElevatedButton(
                    "Novo Favorito",
                    icon=ft.Icons.ADD,
                    on_click=self.abrir_modal_cadastro,
                    bgcolor="ft.Colors.SECONDARY"
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(color=ft.Colors.GREY_800),
            self.lista_favoritos
        ], expand=True)

    def did_mount(self):
        self.carregar_lista()

    def carregar_lista(self):
        self.lista_favoritos.controls.clear()
        dados_banco = self.db.listar_favoritos()

        if not dados_banco:
            self.lista_favoritos.controls.append(
                ft.Text("Nenhum favorito cadastrado ainda.", color=ft.Colors.GREY_500, italic=True)
            )

        for id_, nome, ip, user in dados_banco:
            linha = ft.Container(
                content=ft.ListTile(
                    leading=ft.Icon(ft.Icons.STAR, color=ft.Colors.YELLOW_700),
                    title=ft.Text(f"{nome}", weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(f"IP: {ip} | User: {user}", color=ft.Colors.GREY_400),
                    trailing=ft.IconButton(
                        ft.Icons.DELETE_OUTLINE, 
                        icon_color=ft.Colors.RED_400, 
                        tooltip="Remover Favorito",
                        on_click=lambda e, fid=id_: self.excluir_favorito(fid)
                    )
                ),
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                border_radius=8
            )
            self.lista_favoritos.controls.append(linha)
        
        self.update()

    def abrir_modal_cadastro(self, e):
        # Acopla o modal à página e abre
        self.page.show_dialog(self.modal_cadastro)
        self.modal_cadastro.open = True
        self.page.update()

    def excluir_favorito(self, fav_id):
        self.db.excluir_favorito(fav_id)
        self.carregar_lista()