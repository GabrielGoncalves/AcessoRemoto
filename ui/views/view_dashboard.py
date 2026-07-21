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
        
        self.menu_identidades = ft.PopupMenuButton(
            icon=ft.Icons.BADGE,
            tooltip="Identidades Rápidas",
            items=[]
        )
        
        self.txt_ip = ft.TextField(
            label="IP / Hostname", 
            autofocus=True, 
            prefix_icon=ft.Icons.SEARCH,
            on_change=self._pesquisar_favorito_inline,
            on_submit=self._focar_user
        )
        
        self.txt_user = ft.TextField(
            label="Usuário", 
            suffix_icon=self.menu_identidades, 
            on_submit=self._focar_senha
        )
        
        self.txt_pass = ft.TextField(
            label="Senha", 
            password=True, 
            can_reveal_password=True, 
            on_submit=self._btn_conectar_clicked
        )
        
        self.lv_sugestoes_fav = ft.ListView(spacing=5)
        self.container_sugestoes = ft.Container(
            content=self.lv_sugestoes_fav,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
            border_radius=8,
            padding=5,
            height=120,
            visible=False
        )
        
        self.chk_favorito = ft.Checkbox(label="Marcar como Favorito", value=False)
        self.lv_historico = ft.ListView(expand=True, spacing=10)
        
        self.build_ui()

    def build_ui(self):
        self.historico_minimizado = False

        # --- 1. GRUPO DE PESQUISA COM ALINHAMENTO DE ESTICAMENTO (STRETCH) ---
        grupo_pesquisa_colada = ft.Column(
            controls=[
                self.txt_ip,
                self.container_sugestoes
            ],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH # Estica o campo de IP e sugestões
        )

        # --- 2. COLUNA DO FORMULÁRIO COM STRETCH ---
        col_form = ft.Container(
            content=ft.Column([
                ft.Row([ft.Text("Acesso Rápido", size=18, weight=ft.FontWeight.BOLD)]),
                
                grupo_pesquisa_colada,
                
                self.txt_user,
                self.txt_pass,
                self.chk_favorito,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                
                PrimaryButton(
                    text="Conectar",
                    icon_name=ft.Icons.PLAY_ARROW,
                    on_click=self._btn_conectar_clicked
                )
                
            ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.STRETCH), # Estica todos os inputs
            padding=20, 
            bgcolor=ft.Colors.SURFACE, 
            border_radius=12,
            expand=True # Permite que o card do formulário ocupe o espaço livre
        )

        # 3. LAYOUT DO HISTÓRICO COMPLETO (EXPANDIDO)
        self.col_conteudo_historico = ft.Column(
            controls=[
                ft.Row([
                    ft.Row([
                        ft.Icon(ft.Icons.HISTORY, color=ft.Colors.PRIMARY), 
                        ft.Text("Conexões Recentes", size=18, weight=ft.FontWeight.BOLD)
                    ]),
                    ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.DELETE_SWEEP, 
                            icon_color=ft.Colors.ON_SURFACE_VARIANT, 
                            tooltip="Limpar Histórico", 
                            on_click=self.limpar_historico_ui
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CHEVRON_RIGHT, 
                            icon_color=ft.Colors.PRIMARY, 
                            tooltip="Minimizar Histórico", 
                            on_click=self.toggle_historico_lateral
                        )
                    ], spacing=0)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self.lv_historico
            ],
            spacing=10,
            expand=True,
            visible=True
        )

        # 4. LAYOUT DO HISTÓRICO MINIMIZADO (BARRA COMPACTA)
        self.col_minimizado_historico = ft.Column(
            controls=[
                ft.Icon(ft.Icons.HISTORY, color=ft.Colors.PRIMARY, size=24),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.IconButton(
                    icon=ft.Icons.CHEVRON_LEFT, 
                    icon_color=ft.Colors.PRIMARY, 
                    tooltip="Expandir Histórico", 
                    on_click=self.toggle_historico_lateral
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
            visible=False
        )

        # 5. CONTAINER DO HISTÓRICO COM TRANSIÇÃO
        self.col_historico = ft.Container(
            content=ft.Stack([
                self.col_conteudo_historico,
                self.col_minimizado_historico
            ]),
            padding=15, 
            bgcolor=ft.Colors.SURFACE, 
            border_radius=12,
            width=350,
            animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
            animate_opacity=200
        )

        self.content = ft.Row([col_form, self.col_historico], spacing=15, expand=True)

    # --- FUNÇÃO DE ALTERNÂNCIA COM ANIMAÇÃO ---
    def toggle_historico_lateral(self, e):
        self.historico_minimizado = not self.historico_minimizado
        
        if self.historico_minimizado:
            # Encolhe a barra e alterna a visibilidade dos elementos internos
            self.col_historico.width = 70
            self.col_conteudo_historico.visible = False
            self.col_minimizado_historico.visible = True
        else:
            # Expande a barra e exibe o conteúdo completo novamente
            self.col_historico.width = 350
            self.col_conteudo_historico.visible = True
            self.col_minimizado_historico.visible = False
            
        self.update()

    def limpar_historico_ui(self, e):
        self.db.limpar_historico_completo()
        
        self.lv_historico.controls.clear()
        self.lv_historico.controls.append(ft.Text("Histórico vazio.", color=ft.Colors.ON_SURFACE_VARIANT, italic=True))
        self.update()

    def did_mount(self):
        self._atualizar_lista_historico()
        self.atualizar_menu_identidades_rapido()

        usar_user_padrao = self.db.obter_configuracao("usar_usuario_padrao", "0") == "1"
        usar_dom_padrao = self.db.obter_configuracao("usar_dominio_padrao", "0") == "1" 
        
        user_padrao = self.db.obter_configuracao("usuario_padrao_texto", "")
        dom_padrao = self.db.obter_configuracao("dominio_padrao_texto", "")

        if usar_user_padrao and usar_dom_padrao and user_padrao and dom_padrao:
            self.txt_user.value = f"{dom_padrao}\\{user_padrao}"
        elif usar_user_padrao and user_padrao:
            self.txt_user.value = user_padrao
        elif usar_dom_padrao and dom_padrao:
            self.txt_user.value = f"{dom_padrao}\\"
            
        self.update()

    def atualizar_menu_identidades_rapido(self):
        self.menu_identidades.items.clear()
        usuarios = self.db.listar_usuarios()
        dominios = self.db.listar_dominios()
        
        if usuarios:
            self.menu_identidades.items.append(
                ft.PopupMenuItem(
                    content=ft.Text("--- USUÁRIOS ---", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE_VARIANT), 
                    disabled=True
                )
            )
            for _, nome in usuarios:
                self.menu_identidades.items.append(
                    ft.PopupMenuItem(
                        content=ft.Row([ft.Icon(ft.Icons.PERSON, size=20), ft.Text(nome)]),
                        on_click=lambda e, u=nome: self._aplicar_identidade_rapida(user=u)
                    )
                )
                
        if dominios:
            self.menu_identidades.items.append(
                ft.PopupMenuItem(
                    content=ft.Text("--- DOMÍNIOS ---", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE_VARIANT), 
                    disabled=True
                )
            )
            for _, dom in dominios:
                self.menu_identidades.items.append(
                    ft.PopupMenuItem(
                        content=ft.Row([ft.Icon(ft.Icons.DOMAIN, size=20), ft.Text(dom)]),
                        on_click=lambda e, d=dom: self._aplicar_identidade_rapida(dominio=d)
                    )
                )
        self.menu_identidades.update()

    def _aplicar_identidade_rapida(self, user=None, dominio=None):
        valor_atual = self.txt_user.value.strip() if self.txt_user.value else ""
        partes = valor_atual.split("\\") if "\\" in valor_atual else ["", valor_atual]
        dom_atual = partes[0]
        user_atual = partes[1] if len(partes) > 1 else partes[0]

        if user:
            user_atual = user
        if dominio:
            dom_atual = dominio

        if dom_atual:
            self.txt_user.value = f"{dom_atual}\\{user_atual}"
        else:
            self.txt_user.value = user_atual
            
        self.txt_user.update()

    def _pesquisar_favorito_inline(self, e):
        texto = e.data.strip().lower()
        if not texto:
            self.container_sugestoes.visible = False
            self.update()
            return
        
        todos_favoritos = self.db.listar_favoritos()
        filtrados = [f for f in todos_favoritos if texto in f[1].lower() or texto in f[2].lower()]
        self.lv_sugestoes_fav.controls.clear()
        
        if filtrados:
            self.container_sugestoes.visible = True
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
                        bgcolor=ft.Colors.SURFACE,
                        padding=8, border_radius=6,
                        data={"ip": ip, "user": user},
                        on_click=self._carregar_favorito_selecionado
                    )
                )
        else:
            self.container_sugestoes.visible = False
            
        self.update()

    async def _carregar_favorito_selecionado(self, e):
        dados = e.control.data
        self.txt_ip.value = dados["ip"]
        if dados["user"]: 
            self.txt_user.value = dados["user"]
            
        self.txt_pass.value = "" 
        self.container_sugestoes.visible = False
        self.lv_sugestoes_fav.controls.clear()
        
        await self.txt_pass.focus()
        self.update()

    async def _focar_user(self, e):
        self.container_sugestoes.visible = False 
        self.update()
        await self.txt_user.focus()

    async def _focar_senha(self, e):
         await self.txt_pass.focus()

    def _atualizar_lista_historico(self):
        self.lv_historico.controls.clear()
        historico = self.db.listar_historico(limite=10)
        
        for item in historico:
            ip = item[2]
            user = item[3]
            is_fav = bool(item[4])
            data_hora = item[5]
            
            self.lv_historico.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.MONITOR, color=ft.Colors.YELLOW_700 if is_fav else ft.Colors.PRIMARY),
                        ft.Column([
                            ft.Text(f"{ip}", weight=ft.FontWeight.BOLD),
                            ft.Text(f"{user}", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                            ft.Text(f"Conectado em: {data_hora}", size=11, color=ft.Colors.PRIMARY, italic=True)
                        ], expand=True, spacing=1),
                        
                        ft.IconButton(
                            icon=ft.Icons.ARROW_FORWARD,
                            icon_color=ft.Colors.PRIMARY,
                            tooltip="Preencher dados",
                            data={"ip": ip, "user": user}, 
                            on_click=self._preencher_form
                        )
                    ]),
                    bgcolor=ft.Colors.SECONDARY_CONTAINER,
                    padding=10, 
                    border_radius=8
                )
            )
        self.update()

    async def _preencher_form(self, e):
        dados = e.control.data
        self.txt_ip.value = dados["ip"]
        
        if dados["user"]:
            self.txt_user.value = dados["user"]
            
        self.txt_pass.value = ""
        self.container_sugestoes.visible = False
        
        await self.txt_pass.focus()
        self.update()

    async def preencher_form_externo(self, ip, user):
        lembra_senha = self.db.obter_configuracao("exigir_senha_sessao", "0")
        self.txt_ip.value = ip
        
        if user:
            self.txt_user.value = user
            
        if lembra_senha == "1" and self.txt_pass.value: 
            self.container_sugestoes.visible = False
            self.update()
            self._disparar_conexao_rdp(self.txt_ip.value, self.txt_user.value, self.txt_pass.value)
            return True
        else: 
            self.txt_pass.value = "" 
            self.container_sugestoes.visible = False
            self.update()
            return False

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
        self._disparar_conexao_rdp(ip, user, senha)

    def _disparar_conexao_rdp(self, ip, user, senha):
        if self.chk_favorito.value:
            self.db.adicionar_favorito(ip, ip, user)
            
        self.db.registrar_historico(ip, ip, user)
        self._atualizar_lista_historico()
        self.container_sugestoes.visible = False
        
        lembrar_senha = self.db.obter_configuracao("exigir_senha_sessao", "0")
        if lembrar_senha == "0":
            self.txt_pass.value = ""
            
        self.update()
        self.on_connect_action(ip, user, senha)
