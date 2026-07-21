import flet as ft
import json
from database.db_manager import DatabaseManager
from services.api_service import ApiService
from ui.components.notifications import Notification

class ViewAPI(ft.Container):
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db
        self.expand = True
        self.padding = 20

        self.txt_url = ft.TextField(
            label="Endpoint URL",
            border_color=ft.Colors.SECONDARY,
            expand=True
        )
        self.btn_send = ft.ElevatedButton(
            "Enviar Requisição",
            icon=ft.Icons.SEND,
            color=ft.Colors.ON_PRIMARY,
            style=ft.ButtonStyle(
                bgcolor={
                    ft.ControlState.HOVERED: ft.Colors.PRIMARY,
                    ft.ControlState.DEFAULT: ft.Colors.SECONDARY,
                }
            ),
            on_click=self.fazer_requisicao
        )
        self.btn_clear = ft.ElevatedButton(
            "Limpar Tela",
            icon=ft.Icons.DELETE_SWEEP,
            bgcolor=ft.Colors.RED_900, 
            color=ft.Colors.WHITE,
            on_click=self.limpar_tela
        )

        # Campos de exibição dos resultados
        self.raw_text = ft.Text(selectable=True, font_family="monospace", size=13)
        self.sanitized_view = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=10)

        # Abas refatoradas para a versão 0.80+ do Flet
        self.tabs = ft.Tabs(
            length=2,
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.TabBar(
                        tabs=[
                            ft.Tab(label="Dados Sanitizados", icon=ft.Icons.TABLE_CHART),
                            ft.Tab(label="JSON Bruto", icon=ft.Icons.CODE),
                        ]
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            ft.Container(content=self.sanitized_view),
                            ft.Container(content=ft.Column([self.raw_text], scroll=ft.ScrollMode.AUTO)),
                        ],
                    ),
                ],
            ),
        )

        self.build_ui()

    def build_ui(self):
        endpoint_salvo = self.db.obter_configuracao("api_endpoint", "https://jsonplaceholder.typicode.com/todos/1")
        self.txt_url.value = endpoint_salvo

        self.content = ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.ACCOUNT_TREE, color=ft.Colors.PRIMARY, size=28),
                ft.Text("API e Sanitização", size=24, weight=ft.FontWeight.BOLD)
            ]),
            ft.Divider(color=ft.Colors.SECONDARY),
            ft.Text("Digite seu endpoint mais seus parâmetros da URL.", color=ft.Colors.ON_SURFACE_VARIANT),
            
            ft.Row([self.txt_url, self.btn_send, self.btn_clear]),
            
            ft.Container(
                content=self.tabs,
                expand=True,
                bgcolor=ft.Colors.SURFACE_CONTAINER,
                border_radius=8,
                padding=5
            )
        ])

    def fazer_requisicao(self, e):
        url = self.txt_url.value.strip()
        if not url:
            return
        
        self.db.salvar_configuracao("api_endpoint", url)
        self.btn_send.disabled = True
        self.raw_text.value = "Carregando resposta da API..."
        self.sanitized_view.controls.clear()
        self.sanitized_view.controls.append(ft.ProgressRing(color=ft.Colors.PRIMARY))
        self.update()

        # A MÁGICA DO REFACTOR AQUI: Delegamos a busca para o serviço
        sucesso, json_data, raw_data = ApiService.fetch_json(url)

        self.sanitized_view.controls.clear()

        if sucesso:
            # Se deu certo, atualizamos a tela com os dados limpos
            self.raw_text.value = json.dumps(json_data, indent=4, ensure_ascii=False)
            self.sanitizar_dados(json_data)
        else:
            # Tratamento de erro limpo
            self.raw_text.value = raw_data
            if "Erro na requisição" in raw_data:
                self.sanitized_view.controls.append(ft.Text(f"Falha na conexão de rede.", color=ft.Colors.ERROR))
            else:
                self.sanitized_view.controls.append(ft.Text("A resposta não é um JSON válido para ser sanitizado.", color=ft.Colors.ERROR))

        self.btn_send.disabled = False
        self.update()

    def limpar_tela(self, e):
        self.raw_text.value = ""
        self.sanitized_view.controls.clear()
        self.update()

    def sanitizar_dados(self, json_data):
        # Todo o seu motor visual de construção de tabelas continua intacto e isolado aqui!
        self.sanitized_view.controls.clear()

        if isinstance(json_data, list) and len(json_data) > 0 and isinstance(json_data[0], dict):
            todas_chaves = list(json_data[0].keys())
            self.colunas_visiveis = todas_chaves.copy()
            container_tabela = ft.Container()

            def atualizar_tabela():
                colunas = [ft.DataColumn(ft.Text(k.upper(), weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY)) for k in self.colunas_visiveis]
                linhas = []
                for item in json_data:
                    celulas = [ft.DataCell(ft.Text(str(item.get(k, "")), size=12)) for k in self.colunas_visiveis]
                    linhas.append(ft.DataRow(cells=celulas))
                
                tabela = ft.DataTable(columns=colunas, rows=linhas, border=ft.Border.all(1, ft.Colors.SECONDARY))
                container_tabela.content = ft.Row([tabela], scroll=ft.ScrollMode.ALWAYS)

            def on_chip_select(e):
                chave = e.control.label.value 
                is_selected = (str(e.data).lower() == "true")
                # --- LÓGICA DE BLOQUEIO (EARLY RETURN) ---
                if not is_selected and len(self.colunas_visiveis) == 1 and chave in self.colunas_visiveis:
                    e.control.selected = True
                    e.control.update()

                    Notification.show_warning(e.page, "É necessário manter pelo menos uma coluna selecionada!")
                    return
                # -----------------------------------------
                if is_selected and chave not in self.colunas_visiveis:
                    self.colunas_visiveis.append(chave)
                elif not is_selected and chave in self.colunas_visiveis:
                    self.colunas_visiveis.remove(chave)
                
                self.colunas_visiveis.sort(key=lambda x: todas_chaves.index(x))
                atualizar_tabela()
                container_tabela.update()

            chips_filtro = [
                ft.Chip(
                    label=ft.Text(chave), 
                    selected=True,
                    on_select=on_chip_select,
                    selected_color=ft.Colors.PRIMARY_CONTAINER,
                    show_checkmark=True
                ) for chave in todas_chaves
            ]
            
            atualizar_tabela()

            self.sanitized_view.controls.append(
                ft.Column([
                    ft.Row(chips_filtro, wrap=True),
                    container_tabela
                ], spacing=15, expand=True)
            )

        elif isinstance(json_data, dict):
            for chave, valor in json_data.items():
                self.sanitized_view.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(f"{chave.upper()}:", weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY, width=150),
                            ft.Text(str(valor), expand=True)
                        ]),
                        bgcolor=ft.Colors.SURFACE,
                        padding=10,
                        border_radius=5
                    )
                )
        else:
            self.sanitized_view.controls.append(ft.Text("Os dados foram recebidos, mas o formato é muito simples para sanitização complexa."))