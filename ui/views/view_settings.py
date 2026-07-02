import flet as ft
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
            ft.Divider(color=ft.Colors.GREY_800),
            tabs_controller
        ], expand=True)
    
    def _criar_aba_seguranca(self):
        return ft.Container(
            content=ft.ListView([
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Comportamento de Sessão", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text("Configure como o RemoteCraft lida com suas credenciais de acesso.", size=12, color=ft.Colors.GREY_400),
                            ft.Divider(color=ft.Colors.GREY_800),
                            
                            # A feature flag que discutimos para a Senha de Sessão na RAM
                            ft.Switch(label="Ativar 'Senha de Sessão' (Manter na memória RAM até fechar o app)", value=True),
                            ft.Switch(label="Iniciar o RemoteCraft junto com a inicialização do Sistema O.S.", value=False),
                        ]), padding=15
                    ), bgcolor=ft.Colors.SURFACE
                ),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Gerador de Senhas Fortes", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text("Gere senhas robustas otimizadas para ambientes RDP, SSH e APIs.", size=12, color=ft.Colors.GREY_400),
                            ft.Divider(color=ft.Colors.GREY_800),
                            ft.Row([
                                ft.TextField(label="Senha Gerada", read_only=True, expand=True, border_color="ft.Colors.SECONDARY"),
                                ft.IconButton(ft.Icons.REFRESH, tooltip="Gerar Nova", icon_color="ft.Colors.PRIMARY"),
                                ft.IconButton(ft.Icons.COPY, tooltip="Copiar", icon_color="green"),
                            ]),
                            ft.Slider(min=8, max=32, divisions=24, label="Comprimento: {value} caracteres", value=16),
                        ]), padding=15
                    ), bgcolor=ft.Colors.SURFACE
                )
            ], spacing=15), padding=15
        )

    def _criar_aba_identidades(self):
        return ft.Container(
            content=ft.Row([
                # Sub-coluna: Cadastro Rápido de Usuários
                ft.Container(
                    content=ft.Column([
                        ft.Text("Usuários Recorrentes", size=16, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            # CORREÇÃO AQUI: mudamos size=14 para text_size=14
                            ft.TextField(label="Novo Usuário", expand=True, text_size=14),
                            ft.IconButton(ft.Icons.ADD, icon_color="green")
                        ]),
                        ft.ListView(expand=True, spacing=5) # Aqui listaremos os usuários cadastrados
                    ]), expand=1, bgcolor=ft.Colors.SURFACE, padding=15, border_radius=8
                ),
                # Sub-coluna: Cadastro Rápido de Domínios
                ft.Container(
                    content=ft.Column([
                        ft.Text("Domínios Corporativos", size=16, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            # CORREÇÃO AQUI: mudamos size=14 para text_size=14
                            ft.TextField(label="Novo Domínio (ex: empresa.local)", expand=True, text_size=14),
                            ft.IconButton(ft.Icons.ADD, icon_color="green")
                        ]),
                        ft.ListView(expand=True, spacing=5) # Aqui listaremos os domínios cadastrados
                    ]), expand=1, bgcolor=ft.Colors.SURFACE, padding=15, border_radius=8
                )
            ], spacing=15), padding=15
        )

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
                
                # Card 1: Sincronização e Cópias de Segurança
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Sincronização e Cópias de Segurança", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text("Importe, exporte ou agende rotinas para proteger seus dados locais.", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                            ft.Divider(color=ft.Colors.SECONDARY),
                            ft.Row([
                                # CORREÇÃO: Aspas de ft.Colors removidas
                                ft.ElevatedButton("Importar JSON/CSV", icon=ft.Icons.UPLOAD_FILE, bgcolor=ft.Colors.SECONDARY),
                                ft.ElevatedButton("Exportar Dados", icon=ft.Icons.DOWNLOAD, bgcolor=ft.Colors.SECONDARY_CONTAINER),
                            ], spacing=15),
                            ft.Divider(color=ft.Colors.SECONDARY),
                            ft.Switch(label="Ativar Rotina Automática de Backup Diário", value=False),
                        ]), padding=15
                    ), bgcolor=ft.Colors.SURFACE_CONTAINER
                ),
                
                # Card 2: Personalização Visual
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

    def _criar_aba_avancado(self):
        txt_api_endpoint = ft.TextField(label="Custom API Endpoint URL", border_color="ft.Colors.SECONDARY", disabled=True, value="https://api.remotecraft.internal/v1")
        
        def toggle_dev_mode(e):
            txt_api_endpoint.disabled = not e.control.value
            self.update()

        return ft.Container(
            content=ft.ListView([
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Modo Desenvolvedor", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text("Permite a manipulação avançada de requisições, testes de latência e injeção de rotas customizadas de API.", size=12, color=ft.Colors.GREY_400),
                            ft.Divider(color=ft.Colors.GREY_800),
                            ft.Switch(label="Ativar Recursos de Desenvolvedor Avançado", value=False, on_change=toggle_dev_mode),
                            ft.Divider(color=ft.Colors.GREY_800),
                            txt_api_endpoint,
                            ft.Row([
                                ft.ElevatedButton("Testar Endpoint", icon=ft.Icons.NETWORK_CHECK, bgcolor="green"),
                                ft.ElevatedButton("Resetar Padrões", icon=ft.Icons.RESTORE, bgcolor=ft.Colors.RED_400),
                            ], spacing=15)
                        ]), padding=15
                    ), bgcolor=ft.Colors.SURFACE
                )
            ], spacing=15), padding=15
        )