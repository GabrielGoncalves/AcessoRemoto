import flet as ft
from database.db_manager import DatabaseManager

class ViewFavoritos(ft.Container): # Alterado para ft.Container para consistência com o Dashboard
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db
        self.expand = True
        
        self.lista_favoritos = ft.ListView(expand=True, spacing=10)
        self.build_ui()

    def build_ui(self):
        self.content = ft.Column([
            ft.Row([
                ft.Text("Meus Favoritos", size=24, weight=ft.FontWeight.BOLD),
                ft.ElevatedButton(
                    "Novo Favorito",
                    icon=ft.icons.ADD,
                    on_click=self.abrir_modal_cadastro
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            self.lista_favoritos
        ], expand=True, padding=20)

    def did_mount(self):
        # Chama a lista dinamicamente sempre que a aba é aberta
        self.carregar_lista()

    def carregar_lista(self):
        self.lista_favoritos.controls.clear()
        
        # Puxa os dados reais inseridos no banco pelo Acesso Rápido
        dados_banco = self.db.listar_favoritos()

        for id_, nome, ip, user in dados_banco:
            linha = ft.ListTile(
                leading=ft.Icon(ft.icons.STAR, color=ft.colors.YELLOW_700),
                title=ft.Text(f"{nome}"),
                subtitle=ft.Text(f"IP: {ip} | User: {user}"),
                trailing=ft.Row([
                    ft.IconButton(ft.icons.DELETE, icon_color=ft.colors.RED, on_click=lambda e, fid=id_: self.excluir_favorito(fid))
                ], tight=True)
            )
            self.lista_favoritos.controls.append(linha)
        
        self.update()

    def abrir_modal_cadastro(self, e):
        print("Abrir modal de novo cadastro")

    def excluir_favorito(self, fav_id):
        self.db.excluir_favorito(fav_id)
        self.carregar_lista()