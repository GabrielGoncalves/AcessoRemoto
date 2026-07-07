import flet as ft
from database.db_manager import DatabaseManager
from ui.components.modal_environments import ModalNovoAmbiente
from ui.components.modal_connecting_spaces import ModalNovaConexaoAmbiente

class ViewEnvironments(ft.Container):
    def __init__(self, db: DatabaseManager, on_connect_action, on_redirect_action=None):
        super().__init__()
        self.db = db
        self.on_connect_action = on_connect_action
        self.on_redirect_action = on_redirect_action  
        self.expand = True
        self.padding = 20
        
        self.ambiente_selecionado_id = None
        self.ambiente_selecionado_nome = ""
        
        self.txt_pesquisa_ambientes = ft.TextField(
            hint_text="Buscar ambiente...",
            prefix_icon=ft.Icons.SEARCH,
            border_color=ft.Colors.SECONDARY,
            dense=True,
            on_change=self._filtrar_ambientes
        )
        
        self.lv_ambientes = ft.ListView(expand=True, spacing=10)
        self.modal_ambiente = ModalNovoAmbiente(db=self.db, on_success_callback=self._atualizar_apos_modal_ambiente)
        
        self.col_detalhes = ft.Column(expand=True)
        self.lv_conexoes = ft.ListView(expand=True, spacing=10)
        self.modal_conexao = ModalNovaConexaoAmbiente(db=self.db, on_success_callback=self.carregar_conexoes)
        
        self.build_ui()

    def build_ui(self):
        col_master = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Ambientes", size=20, weight=ft.FontWeight.BOLD),
                    ft.IconButton(ft.Icons.ADD, icon_color=ft.Colors.PRIMARY, tooltip="Novo Ambiente", on_click=self.abrir_modal_ambiente)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                self.txt_pesquisa_ambientes,
                ft.Divider(color=ft.Colors.GREY_800),
                self.lv_ambientes
            ], expand=True),
            expand=1,
            bgcolor=ft.Colors.SURFACE,
            padding=15,
            border_radius=12
        )
        
        col_detail = ft.Container(
            content=self.col_detalhes,
            expand=2,
            bgcolor=ft.Colors.SURFACE,
            padding=15,
            border_radius=12
        )
        
        self.content = ft.Row([col_master, col_detail], spacing=15, expand=True)

    def did_mount(self):
        self.carregar_ambientes()
        self.atualizar_painel_detalhes()

    def _filtrar_ambientes(self, e):
        termo = self.txt_pesquisa_ambientes.value.strip().lower()
        self.carregar_ambientes(termo_busca=termo)

    def _atualizar_apos_modal_ambiente(self):
        termo = self.txt_pesquisa_ambientes.value.strip().lower() if self.txt_pesquisa_ambientes.value else ""
        self.carregar_ambientes(termo_busca=termo)

    def carregar_ambientes(self, termo_busca=""):
        self.lv_ambientes.controls.clear()
        todos_ambientes = self.db.listar_ambientes()
        
        if not todos_ambientes:
            self.lv_ambientes.controls.append(
                ft.Text("Nenhum ambiente criado.", color=ft.Colors.ON_SURFACE_VARIANT, italic=True, size=13)
            )
            self.update()
            return
            
        if termo_busca:
            filtrados = [a for a in todos_ambientes if termo_busca in a[1].lower()]
        else:
            filtrados = todos_ambientes

        if not filtrados:
            self.lv_ambientes.controls.append(
                ft.Text("Nenhum ambiente encontrado.", color=ft.Colors.ON_SURFACE_VARIANT, italic=True, size=13)
            )

        for id_, nome in filtrados:
            is_selected = id_ == self.ambiente_selecionado_id
            
            self.lv_ambientes.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.FOLDER, color=ft.Colors.SECONDARY if not is_selected else ft.Colors.PRIMARY),
                        ft.Text(nome, weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL, expand=True, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE, 
                            icon_color=ft.Colors.ERROR, 
                            icon_size=18,
                            tooltip="Excluir Ambiente",
                            on_click=lambda e, aid=id_: self.excluir_ambiente(aid)
                        )
                    ]),
                    bgcolor=ft.Colors.SECONDARY_CONTAINER if is_selected else "transparent",
                    padding=10,
                    border_radius=8,
                    on_click=lambda e, aid=id_, anome=nome: self.selecionar_ambiente(aid, anome)
                )
            )
        self.update()

    def selecionar_ambiente(self, ambiente_id, nome_ambiente):
        self.ambiente_selecionado_id = ambiente_id
        self.ambiente_selecionado_nome = nome_ambiente
        termo = self.txt_pesquisa_ambientes.value.strip().lower() if self.txt_pesquisa_ambientes.value else ""
        self.carregar_ambientes(termo_busca=termo) 
        self.carregar_conexoes()
        self.atualizar_painel_detalhes()

    def carregar_conexoes(self):
        self.lv_conexoes.controls.clear()
        if not self.ambiente_selecionado_id:
            return
            
        conexoes = self.db.get_conexoes_por_ambiente(self.ambiente_selecionado_id)
        
        if not conexoes:
            self.lv_conexoes.controls.append(
                ft.Text("Nenhuma conexão vinculada a este ambiente.", color=ft.Colors.ON_SURFACE_VARIANT, italic=True, size=13)
            )
        
        for id_, nome_exibicao, ip, user, seguro_fav in conexoes:
            is_fav = bool(seguro_fav)
            self.lv_conexoes.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.MONITOR, color=ft.Colors.YELLOW_700 if is_fav else ft.Colors.PRIMARY),
                        ft.Column([
                            ft.Text(nome_exibicao, weight=ft.FontWeight.BOLD),
                            ft.Text(f"IP: {ip} | User: {user if user else '[Global]'}", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
                        ], expand=True, spacing=2),
                        
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_color=ft.Colors.ERROR,
                            tooltip="Remover Acesso",
                            on_click=lambda e, cid=id_: self.remover_conexao(cid)
                        ),
                        
                        ft.IconButton(
                            icon=ft.Icons.PLAY_ARROW,
                            icon_color=ft.Colors.PRIMARY,
                            tooltip="Conectar via RDP",
                            data={"ip": ip, "user": user},
                            on_click=self._disparar_conexao_rdp
                        )
                    ]),
                    bgcolor=ft.Colors.SECONDARY_CONTAINER,
                    padding=12,
                    border_radius=8
                )
            )
        self.update()

    def atualizar_painel_detalhes(self):
        self.col_detalhes.controls.clear()
        
        if not self.ambiente_selecionado_id:
            self.col_detalhes.controls.append(
                ft.Column([
                    ft.Icon(ft.Icons.CHEVRON_LEFT, size=40, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Text("Selecione um ambiente ao lado para gerenciar os acessos", color=ft.Colors.ON_SURFACE_VARIANT, italic=True)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
            )
        else:
            self.col_detalhes.controls.append(
                ft.Row([
                    ft.Text(
                        f"Acessos: {self.ambiente_selecionado_nome}", 
                        size=20, 
                        weight=ft.FontWeight.BOLD,
                        expand=True,
                        overflow=ft.TextOverflow.ELLIPSIS
                    ),
                    ft.ElevatedButton(
                        "Vincular Acesso",
                        icon=ft.Icons.ADD,
                        bgcolor=ft.Colors.SECONDARY,
                        color=ft.Colors.ON_SECONDARY,
                        on_click=self.abrir_modal_conexao
                    )
                ])
            )
            self.col_detalhes.controls.append(ft.Divider(color=ft.Colors.GREY_800))
            self.col_detalhes.controls.append(self.lv_conexoes)
            
        self.update()

    def abrir_modal_ambiente(self, e):
        self.page.show_dialog(self.modal_ambiente)
        self.modal_ambiente.open = True
        self.page.update()

    def abrir_modal_conexao(self, e):
        if self.ambiente_selecionado_id:
            self.modal_conexao.configurar_ambiente(self.ambiente_selecionado_id)
            self.page.show_dialog(self.modal_conexao)
            self.modal_conexao.open = True
            self.page.update()

    def excluir_ambiente(self, ambiente_id):
        self.db.excluir_ambiente(ambiente_id)
        if self.ambiente_selecionado_id == ambiente_id:
            self.ambiente_selecionado_id = None
            self.ambiente_selecionado_nome = ""
        
        termo = self.txt_pesquisa_ambientes.value.strip().lower() if self.txt_pesquisa_ambientes.value else ""
        self.carregar_ambientes(termo_busca=termo)
        self.atualizar_painel_detalhes()

    def remover_conexao(self, conexao_id):
        self.db.excluir_conexao_ambiente(conexao_id)
        self.carregar_conexoes()
        
        self.page.snack_bar = ft.SnackBar(ft.Text("Acesso desvinculado!"), bgcolor=ft.Colors.ERROR)
        self.page.snack_bar.open = True
        self.page.update()

    async def _disparar_conexao_rdp(self, e):
        dados = e.control.data
        if self.on_redirect_action:
            await self.on_redirect_action(dados["ip"], dados["user"])
        else:
            self.on_connect_action(dados["ip"], dados["user"], "")