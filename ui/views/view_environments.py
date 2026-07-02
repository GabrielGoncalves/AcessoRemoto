import flet as ft
from database.db_manager import DatabaseManager
from ui.components.modal_environments import ModalNovoAmbiente
from ui.components.modal_connecting_spaces import ModalNovaConexaoAmbiente

class ViewEnvironments(ft.Container):
    def __init__(self, db: DatabaseManager, on_connect_action, on_redirect_action=None):
        super().__init__()
        self.db = db
        self.on_connect_action = on_connect_action
        self.on_redirect_action = on_redirect_action  # Guarda a referência do redirecionador
        self.expand = True
        self.padding = 20
        
        self.ambiente_selecionado_id = None
        self.ambiente_selecionado_nome = ""
        
        self.lv_ambientes = ft.ListView(expand=True, spacing=10)
        self.modal_ambiente = ModalNovoAmbiente(db=self.db, on_success_callback=self.carregar_ambientes)
        
        self.col_detalhes = ft.Column(expand=True)
        self.lv_conexoes = ft.ListView(expand=True, spacing=10)
        self.modal_conexao = ModalNovaConexaoAmbiente(db=self.db, on_success_callback=self.carregar_conexoes)
        
        self.build_ui()

    def build_ui(self):
        # Lado Esquerdo: Lista de Ambientes (Proporção 1)
        col_master = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Ambientes", size=20, weight=ft.FontWeight.BOLD),
                    ft.IconButton(ft.Icons.ADD, icon_color="ft.Colors.PRIMARY", tooltip="Novo Ambiente", on_click=self.abrir_modal_ambiente)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(color=ft.Colors.GREY_800),
                self.lv_ambientes
            ], expand=True),
            expand=1,
            bgcolor=ft.Colors.SURFACE,
            padding=15,
            border_radius=12
        )
        
        # Lado Direito: Lista de Conexões (Proporção 2)
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

    def carregar_ambientes(self):
        self.lv_ambientes.controls.clear()
        ambientes = self.db.listar_ambientes()
        
        if not ambientes:
            self.lv_ambientes.controls.append(
                ft.Text("Nenhum ambiente criado.", color=ft.Colors.GREY_500, italic=True, size=13)
            )
        
        for id_, nome in ambientes:
            is_selected = id_ == self.ambiente_selecionado_id
            
            self.lv_ambientes.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.FOLDER, color="ft.Colors.SECONDARY" if not is_selected else "ft.Colors.PRIMARY"),
                        ft.Text(nome, weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL, expand=True),
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE, 
                            icon_color=ft.Colors.RED_400, 
                            icon_size=18,
                            tooltip="Excluir Ambiente",
                            on_click=lambda e, aid=id_: self.excluir_ambiente(aid)
                        )
                    ]),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST if is_selected else "transparent",
                    padding=10,
                    border_radius=8,
                    on_click=lambda e, aid=id_, anome=nome: self.selecionar_ambiente(aid, anome)
                )
            )
        self.update()

    def selecionar_ambiente(self, ambiente_id, nome_ambiente):
        self.ambiente_selecionado_id = ambiente_id
        self.ambiente_selecionado_nome = nome_ambiente
        self.carregar_ambientes() # Recarrega para aplicar o destaque visual de seleção
        self.carregar_conexoes()
        self.atualizar_painel_detalhes()

    def carregar_conexoes(self):
        self.lv_conexoes.controls.clear()
        if not self.ambiente_selecionado_id:
            return
            
        conexoes = self.db.get_conexoes_por_ambiente(self.ambiente_selecionado_id)
        
        if not conexoes:
            self.lv_conexoes.controls.append(
                ft.Text("Nenhuma conexão vinculada a este ambiente.", color=ft.Colors.GREY_500, italic=True, size=13)
            )
        
        for id_, nome_exibicao, ip, user, seguro_fav in conexoes:
            is_fav = bool(seguro_fav)
            self.lv_conexoes.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.MONITOR, color=ft.Colors.YELLOW_700 if is_fav else "ft.Colors.PRIMARY"),
                        ft.Column([
                            ft.Text(nome_exibicao, weight=ft.FontWeight.BOLD),
                            ft.Text(f"IP: {ip} | User: {user}", size=12, color=ft.Colors.GREY_400)
                        ], expand=True, spacing=2),
                        ft.IconButton(
                            icon=ft.Icons.PLAY_ARROW,
                            icon_color="green",
                            tooltip="Conectar via RDP",
                            data={"ip": ip, "user": user},
                            on_click=self._disparar_conexao_rdp
                        )
                    ]),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    padding=12,
                    border_radius=8
                )
            )
        self.update()

    def atualizar_painel_detalhes(self):
        self.col_detalhes.controls.clear()
        
        # Caso nenhum ambiente esteja selecionado, mostra um placeholder elegante
        if not self.ambiente_selecionado_id:
            self.col_detalhes.controls.append(
                ft.Column([
                    ft.Icon(ft.Icons.CHEVRON_LEFT, size=40, color=ft.Colors.GREY_600),
                    ft.Text("Selecione um ambiente ao lado para gerenciar os acessos", color=ft.Colors.GREY_500, italic=True)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
            )
        else:
            # Painel com as conexões do ambiente ativo
            self.col_detalhes.controls.append(
                ft.Row([
                    ft.Text(f"Acessos: {self.ambiente_selecionado_nome}", size=20, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton(
                        "Vincular Acesso",
                        icon=ft.Icons.ADD,
                        bgcolor="ft.Colors.SECONDARY",
                        on_click=self.abrir_modal_conexao
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )
            self.col_detalhes.controls.append(ft.Divider(color=ft.Colors.GREY_800))
            self.col_detalhes.controls.append(self.lv_conexoes)
            
        self.update()

    def abrir_modal_ambiente(self, e):
        self.page.show_dialog(self.modal_ambiente)

    def abrir_modal_conexao(self, e):
        if self.ambiente_selecionado_id:
            self.modal_conexao.configurar_ambiente(self.ambiente_selecionado_id)
            self.page.show_dialog(self.modal_conexao)

    def excluir_ambiente(self, ambiente_id):
        self.db.excluir_ambiente(ambiente_id)
        if self.ambiente_selecionado_id == ambiente_id:
            self.ambiente_selecionado_id = None
            self.ambiente_selecionado_nome = ""
        self.carregar_ambientes()
        self.atualizar_painel_detalhes()

    async def _disparar_conexao_rdp(self, e):
        dados = e.control.data
        if self.on_redirect_action:
            # Em vez de abrir o RDP direto sem senha, joga para o Dashboard preenchendo os dados
            await self.on_redirect_action(dados["ip"], dados["user"])
        else:
            self.on_connect_action(dados["ip"], dados["user"], "")