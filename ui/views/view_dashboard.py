import flet as ft
from database.db_manager import DatabaseManager
from ui.components.inputs import ModernTextField
from ui.components.custom_buttons import PrimaryButton

class DashboardView(ft.Container):
    def __init__(self, db: DatabaseManager, on_connect_action):
        super().__init__()
        self.db = db
        self.on_connect_action = on_connect_action
        self.expand = True
        
        self.txt_ip = ft.TextField(
            label="IP / Hostname", 
            autofocus=True, 
            prefix_icon=ft.Icons.SEARCH,
            on_change=self._pesquisar_favorito_inline,
            on_submit=self._focar_user
        )
        
        self.txt_user = ft.TextField(
            label="Usuário", 
            on_submit=self._focar_senha)
        
        self.txt_pass = ft.TextField(
            label="Senha", 
            password=True, 
            can_reveal_password=True, 
            on_submit=self._btn_conectar_clicked)
        
        self.lv_sugestoes_fav = ft.ListView(height=80, spacing=5, visible=False)
        self.chk_favorito = ft.Checkbox(label="Marcar como Favorito", value=False)
        self.lv_historico = ft.ListView(expand=True, spacing=10)
        self.build_ui()

    def build_ui(self):
        col_form = ft.Container(
            content=ft.Column([
                ft.Row([ft.Text("Acesso Rápido", size=18, weight=ft.FontWeight.BOLD)]),
                
                self.txt_ip,
                self.lv_sugestoes_fav,
                self.txt_user,
                self.txt_pass,
                self.chk_favorito,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                
                PrimaryButton(
                    text="Conectar",
                    icon_name=ft.Icons.PLAY_ARROW,
                    on_click=self._btn_conectar_clicked
                )
                
            ], spacing=12),
            padding=20, bgcolor=ft.Colors.SURFACE, border_radius=12, expand=1
        )

        col_historico = ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(ft.Icons.HISTORY, color=ft.Colors.PRIMARY), ft.Text("Conexões Recentes", size=18, weight=ft.FontWeight.BOLD)]),
                self.lv_historico
            ]),
            padding=20, bgcolor=ft.Colors.SURFACE, border_radius=12, expand=1
        )

        self.content = ft.Row([col_form, col_historico], spacing=15, expand=True)

    def did_mount(self):
        self._atualizar_lista_historico()

    def _pesquisar_favorito_inline(self, e):
        texto = e.data.strip().lower()
        
        if not texto:
            self.lv_sugestoes_fav.visible = False
            self.update()
            return
        
        todos_favoritos = self.db.listar_favoritos()
        filtrados = [
            f for f in todos_favoritos 
            if texto in f[1].lower() or texto in f[2].lower()
        ]
        
        self.lv_sugestoes_fav.controls.clear()
        
        if filtrados:
            self.lv_sugestoes_fav.visible = True
            for id_, nome, ip, user in filtrados:
                self.lv_sugestoes_fav.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.STAR, color=ft.Colors.YELLOW_700, size=16),
                            ft.Column([
                                ft.Text(nome, size=13, weight=ft.FontWeight.BOLD),
                                ft.Text(f"{ip} | {user}", size=11, color=ft.Colors.GREY_400)
                            ], spacing=2, expand=True)
                        ]),
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                        padding=8,
                        border_radius=6,
                        data={"ip": ip, "user": user},
                        on_click=self._carregar_favorito_selecionado
                    )
                )
        else:
            self.lv_sugestoes_fav.visible = False
            
        self.update()

    async def _carregar_favorito_selecionado(self, e):
        dados = e.control.data
        self.txt_ip.value = dados["ip"]
        self.txt_user.value = dados["user"]
        self.txt_pass.value = "" 
        
        self.lv_sugestoes_fav.visible = False
        self.lv_sugestoes_fav.controls.clear()
        
        await self.txt_pass.focus()
        self.update()

    async def _focar_user(self, e):
        self.lv_sugestoes_fav.visible = False 
        self.update()
        await self.txt_user.focus()

    async def _focar_senha(self, e):
        await self.txt_pass.focus()

    def _atualizar_lista_historico(self):
        self.lv_historico.controls.clear()
        historico = self.db.listar_historico(limite=10)
        
        for id_, nome_exibicao, ip, user, e_favorito in historico:
            is_fav = bool(e_favorito)
            
            self.lv_historico.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.MONITOR, color=ft.Colors.YELLOW_700 if is_fav else ft.Colors.PRIMARY),
                        ft.Column([
                            ft.Text(f"IP: {ip}", weight=ft.FontWeight.BOLD),
                            ft.Text(f"User: {user}", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
                        ], expand=True),
                        ft.IconButton(
                            icon=ft.Icons.ARROW_FORWARD,
                            icon_color="green",
                            tooltip="Preencher dados",
                            data={"ip": ip, "user": user}, 
                            on_click=self._preencher_form
                        )
                    ]),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    padding=10, border_radius=8
                )
            )
        self.update()

    async def _preencher_form(self, e):
        dados = e.control.data
        self.txt_ip.value = dados["ip"]
        self.txt_user.value = dados["user"]
        self.txt_pass.value = ""
        self.lv_sugestoes_fav.visible = False
        await self.txt_pass.focus()
        self.update()

    # --- Ação principal ---
    async def _btn_conectar_clicked(self, e):
        if not self.txt_ip.value:
            await self.txt_ip.focus()
            return
        if not self.txt_user.value:
            await self.txt_user.focus()
            return
        
        ip = self.txt_ip.value.strip()
        user = self.txt_user.value.strip()
        senha = self.txt_pass.value

        if self.chk_favorito.value:
            self.db.adicionar_favorito(ip, ip, user)
            
        self.db.registrar_historico(ip, ip, user)
        self._atualizar_lista_historico()
        
        self.lv_sugestoes_fav.visible = False
        self.update()
        
        self.on_connect_action(ip, user, senha)

    async def preencher_form_externo(self, ip, user):
        """Método público chamado ao redirecionar acessos de outras telas"""
        self.txt_ip.value = ip
        self.txt_user.value = user
        self.txt_pass.value = "" 
        self.lv_sugestoes_fav.visible = False
        
        await self.txt_pass.focus()
        self.update()