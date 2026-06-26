import flet as ft
from database.db_manager import DatabaseManager

class DashboardView(ft.Container):
    def __init__(self, db: DatabaseManager, on_connect_action):
        super().__init__()
        self.db = db
        self.on_connect_action = on_connect_action
        self.expand = True
        
        # O campo de IP agora faz o papel de Busca (on_change) e Transição (on_submit)
        self.txt_ip = ft.TextField(
            label="IP, Hostname ou Favorito", 
            border_color="#4e54c8", 
            autofocus=True, 
            prefix_icon=ft.Icons.SEARCH,
            on_change=self._pesquisar_favorito_inline,
            on_submit=self._focar_user
        )
        
        # Container de sugestões com altura limitada que começa invisível
        self.lv_sugestoes_fav = ft.ListView(height=120, spacing=5, visible=False)
        
        self.txt_user = ft.TextField(label="Usuário", border_color="#4e54c8", on_submit=self._focar_senha)
        self.txt_pass = ft.TextField(label="Senha", password=True, can_reveal_password=True, border_color="#4e54c8", on_submit=self._btn_conectar_clicked)
        
        self.chk_favorito = ft.Checkbox(label="Marcar como Favorito", value=False)
        self.lv_historico = ft.ListView(expand=True, spacing=10)

        self.build_ui()

    def build_ui(self):
        col_form = ft.Container(
            content=ft.Column([
                ft.Row([ft.Text("Acesso Rápido", size=18, weight=ft.FontWeight.BOLD)]),
                
                self.txt_ip,
                self.lv_sugestoes_fav, # Fica logo abaixo do IP
                self.txt_user,
                self.txt_pass,
                self.chk_favorito,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.PLAY_ARROW),
                        ft.Text("Conectar")
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    color="white", 
                    bgcolor="#00d2ff",
                    on_click=self._btn_conectar_clicked
                )
            ], spacing=12),
            padding=20, bgcolor="#161623", border_radius=12, expand=1
        )

        col_historico = ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(ft.Icons.HISTORY, color="#00d2ff"), ft.Text("Conexões Recentes", size=18, weight=ft.FontWeight.BOLD)]),
                self.lv_historico
            ]),
            padding=20, bgcolor="#161623", border_radius=12, expand=1
        )

        self.content = ft.Row([col_form, col_historico], spacing=15, expand=True)

    def did_mount(self):
        self._atualizar_lista_historico()

    # --- Lógica Unificada: Busca no próprio campo de IP ---
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
                        bgcolor="#222235",
                        padding=8,
                        border_radius=6,
                        data={"ip": ip, "user": user},
                        on_click=self._carregar_favorito_selecionado
                    )
                )
        else:
            # Se não achou favorito, esconde a lista (usuário está digitando um IP novo)
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

    # --- Funções de transição de foco ---
    async def _focar_user(self, e):
        # Esconde a lista caso o usuário dê enter no meio de uma busca
        self.lv_sugestoes_fav.visible = False 
        self.update()
        await self.txt_user.focus()

    async def _focar_senha(self, e):
        await self.txt_pass.focus()

    # --- Lógica do histórico ---
    def _atualizar_lista_historico(self):
        self.lv_historico.controls.clear()
        historico = self.db.listar_historico(limite=10)
        
        for id_, nome_exibicao, ip, user, e_favorito in historico:
            is_fav = bool(e_favorito)
            
            self.lv_historico.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.MONITOR, color=ft.Colors.YELLOW_700 if is_fav else "#00d2ff"),
                        ft.Column([
                            ft.Text(f"IP: {ip}", weight=ft.FontWeight.BOLD),
                            ft.Text(f"User: {user}", size=12, color=ft.Colors.GREY_400)
                        ], expand=True),
                        ft.IconButton(
                            icon=ft.Icons.ARROW_FORWARD,
                            icon_color="green",
                            tooltip="Preencher dados",
                            data={"ip": ip, "user": user}, 
                            on_click=self._preencher_form
                        )
                    ]),
                    bgcolor="#222235", padding=10, border_radius=8
                )
            )
        self.update()

    async def _preencher_form(self, e):
        dados = e.control.data
        self.txt_ip.value = dados["ip"]
        self.txt_user.value = dados["user"]
        self.txt_pass.value = ""
        self.lv_sugestoes_fav.visible = False # Garante que a lista feche
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