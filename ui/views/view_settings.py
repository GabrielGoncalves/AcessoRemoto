import flet as ft
import random
import string
from database.db_manager import DatabaseManager

class ViewSettings(ft.Container):
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db
        self.expand = True
        self.padding = 20
        
        self.build_ui()

    def build_ui(self):
        # Implementação moderna utilizando TabBar e TabBarView separados
        tabs_controller = ft.Tabs(
            length=4,
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.TabBar(
                        tabs=[
                            ft.Tab(label="Sessão & Segurança", icon=ft.Icons.SECURITY),
                            ft.Tab(label="Identidades", icon=ft.Icons.PEOPLE_ALT),
                            ft.Tab(label="Dados & Backup", icon=ft.Icons.DATA_USAGE),
                            ft.Tab(label="Avançado", icon=ft.Icons.CODE),
                        ]
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            self._criar_aba_seguranca(),
                            self._criar_aba_identidades(),
                            self._criar_aba_dados(),
                            self._criar_aba_avancado(),
                        ],
                    ),
                ],
            ),
        )
        
        self.content = ft.Column([
            ft.Text("Configurações do Sistema", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(color=ft.Colors.SECONDARY),
            tabs_controller
        ], expand=True)
    
    # ==========================================
    # ABA 1: SESSÃO & SEGURANÇA
    # ==========================================
    def _criar_aba_seguranca(self):
        
        # --- Lógica da Flag de Segurança ---
        def alternar_flag_seguranca(e):
            valor_salvar = "1" if e.control.value else "0"
            self.db.salvar_configuracao("exigir_senha_sessao", valor_salvar)
            
            # Padrão tradicional (Compatível com sua versão)
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Configuração de segurança updated!"),
                bgcolor=ft.Colors.SECONDARY
            )
            self.page.snack_bar.open = True
            self.page.update()

        flag_atual = self.db.obter_configuracao("exigir_senha_sessao", "0")
        estado_switch = True if flag_atual == "1" else False

        # --- Lógica do Gerador de Senhas RDP ---
        txt_senha_gerada = ft.TextField(
            label="Senha Forte Gerada",
            read_only=True,
            border_color=ft.Colors.SECONDARY,
            expand=True
        )
        
        slider_comprimento = ft.Slider(
            min=8, max=32, divisions=24,
            label="{value} caracteres", value=16
        )

        def gerar_senha_aleatoria(e):
            comprimento = int(slider_comprimento.value)
            caracteres = string.ascii_letters + string.digits + "!@#$%&*"
            senha_final = "".join(random.choice(caracteres) for _ in range(comprimento))
            txt_senha_gerada.value = senha_final
            txt_senha_gerada.update()

        def copiar_senha_clipboard(e):
            if txt_senha_gerada.value:
                self.page.set_clipboard(txt_senha_gerada.value)
                
                # Padrão tradicional (Compatível com sua versão)
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Senha copiada para a área de transferência!"),
                    bgcolor=ft.Colors.GREEN_700
                )
                self.page.snack_bar.open = True
                self.page.update()

        return ft.Container(
            content=ft.ListView([
                # Card 1: Controle de Sessão
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.LOCK, color=ft.Colors.PRIMARY),
                                ft.Text("Segurança de Credenciais", size=16, weight=ft.FontWeight.BOLD)
                            ]),
                            ft.Divider(color=ft.Colors.SECONDARY),
                            ft.Text(
                                "Determine como a interface do aplicativo gerencia dados sensíveis após disparar conexões.",
                                size=12, color=ft.Colors.ON_SURFACE_VARIANT
                            ),
                            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                            
                            ft.Switch(
                                label="Lembrar senha da sessão após conectar (Desative para limpar o campo por segurança)",
                                value=estado_switch,
                                on_change=alternar_flag_seguranca,
                                active_color=ft.Colors.PRIMARY
                            ),
                        ]), padding=15
                    ), bgcolor=ft.Colors.SURFACE_CONTAINER
                ),

                # Card 2: Gerador de Senhas Fortes
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.PASSWORD, color=ft.Colors.PRIMARY),
                                ft.Text("Gerador de Senhas Avançado", size=16, weight=ft.FontWeight.BOLD)
                            ]),
                            ft.Divider(color=ft.Colors.SECONDARY),
                            ft.Text("Gere senhas randômicas de alta complexidade para usar nos seus servidores remotos.", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                            
                            ft.Text("Comprimento da Senha:", size=13, weight=ft.FontWeight.W_500),
                            slider_comprimento,
                            
                            ft.Row([
                                txt_senha_gerada,
                                ft.IconButton(
                                    icon=ft.Icons.COPY,
                                    icon_color=ft.Colors.PRIMARY,
                                    tooltip="Copiar Senha",
                                    on_click=copiar_senha_clipboard # <-- CORRIGIDO AQUI
                                )
                            ], spacing=10),
                            
                            ft.ElevatedButton(
                                "Gerar Nova Senha",
                                icon=ft.Icons.REFRESH,
                                bgcolor=ft.Colors.PRIMARY,
                                color=ft.Colors.ON_PRIMARY,
                                on_click=gerar_senha_aleatoria
                            )
                        ]), padding=15
                    ), bgcolor=ft.Colors.SURFACE_CONTAINER
                )
            ], spacing=15), padding=15
        )

    # ==========================================
    # ABA 2: IDENTIDADES (UI BASE)
    # ==========================================
    def _criar_aba_identidades(self):
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Text("Usuários Recorrentes", size=16, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.TextField(label="Novo Usuário", expand=True, text_size=14, border_color=ft.Colors.SECONDARY),
                            ft.IconButton(ft.Icons.ADD, icon_color=ft.Colors.PRIMARY)
                        ]),
                        ft.ListView(expand=True, spacing=5) 
                    ]), expand=1, bgcolor=ft.Colors.SURFACE_CONTAINER, padding=15, border_radius=8
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Domínios Corporativos", size=16, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.TextField(label="Novo Domínio (ex: empresa.local)", expand=True, text_size=14, border_color=ft.Colors.SECONDARY),
                            ft.IconButton(ft.Icons.ADD, icon_color=ft.Colors.PRIMARY)
                        ]),
                        ft.ListView(expand=True, spacing=5) 
                    ]), expand=1, bgcolor=ft.Colors.SURFACE_CONTAINER, padding=15, border_radius=8
                )
            ], spacing=15), padding=15
        )

    # ==========================================
    # ABA 3: DADOS & BACKUP
    # ==========================================
    def _criar_aba_dados(self):
        from ui.layout import AppTheme
        tema_atual = self.db.obter_tema()
        
        def alterar_tema(e):
            novo_tema = e.control.value
            self.page.theme = AppTheme.get_theme(novo_tema)
            self.page.bgcolor = self.page.theme.color_scheme.surface_container
            self.page.update()
            self.db.salvar_tema(novo_tema)

        return ft.Container(
            content=ft.ListView([
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Sincronização e Cópias de Segurança", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text("Importe, exporte ou agende rotinas para proteger seus dados locais.", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                            ft.Divider(color=ft.Colors.SECONDARY),
                            ft.Row([
                                ft.ElevatedButton("Importar JSON/CSV", icon=ft.Icons.UPLOAD_FILE, bgcolor=ft.Colors.SECONDARY),
                                ft.ElevatedButton("Exportar Dados", icon=ft.Icons.DOWNLOAD, bgcolor=ft.Colors.SECONDARY_CONTAINER),
                            ], spacing=15),
                            ft.Divider(color=ft.Colors.SECONDARY),
                            ft.Switch(label="Ativar Rotina Automática de Backup Diário", value=False, active_color=ft.Colors.PRIMARY),
                        ]), padding=15
                    ), bgcolor=ft.Colors.SURFACE_CONTAINER
                ),
                
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Personalização Visual", size=16, weight=ft.FontWeight.BOLD),
                            ft.Divider(color=ft.Colors.SECONDARY),
                            ft.Dropdown(
                                label="Tema do Aplicativo",
                                value=tema_atual,       
                                on_select=alterar_tema, 
                                options=[
                                    ft.dropdown.Option("cyberpunk", "Cyberpunk"),
                                    ft.dropdown.Option("neon_tokyo", "Neon Tokyo"),
                                    ft.dropdown.Option("floresta_boreal", "Floresta Boreal"),
                                    ft.dropdown.Option("cafe_expresso", "Café Expresso"),
                                    ft.dropdown.Option("dracula_dev", "Dracula Dev"),
                                    ft.dropdown.Option("gelo_claro", "Gelo Claro"),
                                    ft.dropdown.Option("creme_de_baunilha", "Creme de Baunilha"),
                                    ft.dropdown.Option("cereja_doce", "Cereja Doce"),
                                    ft.dropdown.Option("outono_fazenda", "Outono de Fazenda"),
                                ],
                                border_color=ft.Colors.SECONDARY
                            )
                        ]), padding=15
                    ), bgcolor=ft.Colors.SURFACE_CONTAINER
                )
            ], spacing=15), padding=15
        )

    # ==========================================
    # ABA 4: AVANÇADO
    # ==========================================
    def _criar_aba_avancado(self):
        txt_api_endpoint = ft.TextField(
            label="Custom API Endpoint URL", 
            border_color=ft.Colors.SECONDARY, 
            disabled=True, 
            value="https://api.remotecraft.internal/v1"
        )
        
        def toggle_dev_mode(e):
            txt_api_endpoint.disabled = not e.control.value
            self.update()

        return ft.Container(
            content=ft.ListView([
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.WARNING, color=ft.Colors.ERROR),
                                ft.Text("Modo Desenvolvedor", size=16, weight=ft.FontWeight.BOLD)
                            ]),
                            ft.Text("Permite a manipulação avançada de requisições, testes de latência e injeção de rotas customizadas de API.", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                            ft.Divider(color=ft.Colors.SECONDARY),
                            
                            ft.Switch(label="Ativar Recursos de Desenvolvedor Avançado", value=False, on_change=toggle_dev_mode, active_color=ft.Colors.PRIMARY),
                            ft.Divider(color=ft.Colors.SECONDARY),
                            txt_api_endpoint,
                            
                            ft.Row([
                                ft.ElevatedButton("Testar Endpoint", icon=ft.Icons.NETWORK_CHECK, bgcolor=ft.Colors.PRIMARY, color=ft.Colors.ON_PRIMARY),
                                ft.ElevatedButton("Resetar Padrões", icon=ft.Icons.RESTORE, bgcolor=ft.Colors.ERROR, color=ft.Colors.ON_PRIMARY),
                            ], spacing=15)
                        ]), padding=15
                    ), bgcolor=ft.Colors.SURFACE_CONTAINER
                )
            ], spacing=15), padding=15
        )