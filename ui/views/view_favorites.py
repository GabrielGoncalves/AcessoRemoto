import flet as ft
from database.db_manager import DatabaseManager
from ui.components.modal_favorites import ModalNovoFavorito

class ViewFavoritos(ft.Container):
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db
        self.expand = True
        self.padding = 20 
        
        # Campo de pesquisa em tempo real
        self.txt_pesquisa = ft.TextField(
            hint_text="Buscar por nome, IP ou usuário...",
            prefix_icon=ft.Icons.SEARCH,
            border_color=ft.Colors.SECONDARY,
            dense=True,
            on_change=self._filtrar_lista
        )
        
        self.lista_favoritos = ft.ListView(expand=True, spacing=10)
        
        self.modal_cadastro = ModalNovoFavorito(
            db=self.db, 
            on_success_callback=self._atualizar_apos_modal
        )
        
        self.build_ui()

    def build_ui(self):
        cabecalho = ft.Row([
            ft.Text("Meus Favoritos", size=24, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton(
                "Novo Favorito",
                icon=ft.Icons.ADD,
                on_click=self.abrir_modal_cadastro,
                bgcolor=ft.Colors.SECONDARY, 
                color=ft.Colors.ON_SECONDARY
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        self.content = ft.Container(
            content=ft.Column([
                cabecalho,
                self.txt_pesquisa,
                ft.Divider(color=ft.Colors.GREY_800),
                self.lista_favoritos
            ], expand=True),
            bgcolor=ft.Colors.SURFACE,
            padding=20,
            border_radius=12,
            expand=True
        )

    def did_mount(self):
        self.carregar_lista()

    def _filtrar_lista(self, e):
        """Disparado a cada letra digitada para filtrar a lista instantaneamente"""
        termo = self.txt_pesquisa.value.strip().lower()
        self.carregar_lista(termo_busca=termo)

    def _atualizar_apos_modal(self):
        """Garante que ao adicionar um favorito, o filtro de texto não se perca"""
        termo = self.txt_pesquisa.value.strip().lower() if self.txt_pesquisa.value else ""
        self.carregar_lista(termo_busca=termo)

    def carregar_lista(self, termo_busca=""):
        self.lista_favoritos.controls.clear()
        dados_banco = self.db.listar_favoritos()

        if not dados_banco:
            self.lista_favoritos.controls.append(
                ft.Text("Nenhum favorito cadastrado ainda.", color=ft.Colors.ON_SURFACE_VARIANT, italic=True)
            )
            self.update()
            return

        if termo_busca:
            filtrados = [
                f for f in dados_banco 
                if termo_busca in f[1].lower() or termo_busca in f[2].lower() or termo_busca in f[3].lower()
            ]
        else:
            filtrados = dados_banco

        if not filtrados:
            self.lista_favoritos.controls.append(
                ft.Text("Nenhum favorito encontrado com esse termo.", color=ft.Colors.ON_SURFACE_VARIANT, italic=True)
            )

        for id_, nome, ip, user in filtrados:
            linha = ft.Container(
                content=ft.ListTile(
                    leading=ft.Icon(ft.Icons.STAR, color=ft.Colors.YELLOW_700),
                    title=ft.Text(f"{nome}", weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(f"IP: {ip} | User: {user}", color=ft.Colors.ON_SURFACE_VARIANT),
                    trailing=ft.IconButton(
                        ft.Icons.DELETE_OUTLINE, 
                        icon_color=ft.Colors.ERROR, 
                        tooltip="Remover Favorito",
                        on_click=lambda e, fid=id_: self.excluir_favorito(fid)
                    )
                ),
                bgcolor=ft.Colors.SECONDARY_CONTAINER, 
                border_radius=8
            )
            self.lista_favoritos.controls.append(linha)
        
        self.update()

    def abrir_modal_cadastro(self, e):
        self.page.show_dialog(self.modal_cadastro)
        self.modal_cadastro.open = True
        self.page.update()

    def excluir_favorito(self, fav_id):
        self.db.excluir_favorito(fav_id)
        termo_atual = self.txt_pesquisa.value.strip().lower() if self.txt_pesquisa.value else ""
        self.carregar_lista(termo_busca=termo_atual)
        
        if self.page:
            self.page.snack_bar = ft.SnackBar(ft.Text("Favorito removido com sucesso!"), bgcolor=ft.Colors.ERROR)
            self.page.snack_bar.open = True
            self.page.update()