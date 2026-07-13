import flet as ft
import json
import urllib.request
from database.db_manager import DatabaseManager

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
            bgcolor=ft.Colors.PRIMARY,
            color=ft.Colors.ON_PRIMARY,
            on_click=self.fazer_requisicao
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
                            # Conteúdo da Aba 1
                            ft.Container(content=self.sanitized_view, padding=15),
                            # Conteúdo da Aba 2
                            ft.Container(content=ft.Column([self.raw_text], scroll=ft.ScrollMode.AUTO), padding=15),
                        ],
                    ),
                ],
            ),
        )

        self.build_ui()

    def build_ui(self):
        # Lê a URL configurada lá na aba de Configurações, ou usa uma de teste (gratuita e pública)
        endpoint_salvo = self.db.obter_configuracao("api_endpoint", "https://jsonplaceholder.typicode.com/users")
        self.txt_url.value = endpoint_salvo

        self.content = ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.ACCOUNT_TREE, color=ft.Colors.PRIMARY, size=28),
                ft.Text("Testador de API e Sanitização", size=24, weight=ft.FontWeight.BOLD)
            ]),
            ft.Divider(color=ft.Colors.SECONDARY),
            ft.Text("Faça chamadas de rede e veja o Python tratar o resultado automaticamente.", color=ft.Colors.ON_SURFACE_VARIANT),
            
            ft.Row([self.txt_url, self.btn_send]),
            
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

        # Trava o botão e avisa que está carregando
        self.btn_send.disabled = True
        self.raw_text.value = "Carregando resposta da API..."
        self.sanitized_view.controls.clear()
        self.sanitized_view.controls.append(ft.ProgressRing(color=ft.Colors.PRIMARY))
        self.update()

        try:
            # Faz a requisição GET nativa do Python
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.read().decode('utf-8')

            try:
                # Tenta converter o texto em um objeto JSON (Dicionário ou Lista)
                json_data = json.loads(data)
                
                # Preenche a aba "Bruto" formatando bonito com indentações
                self.raw_text.value = json.dumps(json_data, indent=4, ensure_ascii=False)
                
                # Envia para o motor de sanitização preencher a aba "Sanitizado"
                self.sanitizar_dados(json_data)
                
            except json.JSONDecodeError:
                self.raw_text.value = data
                self.sanitized_view.controls.clear()
                self.sanitized_view.controls.append(ft.Text("A resposta não é um JSON válido para ser sanitizado.", color=ft.Colors.ERROR))

        except Exception as ex:
            self.raw_text.value = f"Erro na requisição:\n{str(ex)}"
            self.sanitized_view.controls.clear()
            self.sanitized_view.controls.append(ft.Text(f"Falha na conexão de rede.", color=ft.Colors.ERROR))

        finally:
            self.btn_send.disabled = False
            self.update()

    def sanitizar_dados(self, json_data):
        """Mágica: Analisa o tipo de dado recebido e constrói a interface adequada"""
        self.sanitized_view.controls.clear()

        # Cenário 1: É uma lista de objetos (Ideal para criar Tabelas)
        if isinstance(json_data, list) and len(json_data) > 0 and isinstance(json_data[0], dict):
            # Pega as chaves do primeiro item para criar os cabeçalhos das colunas (limitado a 6 para caber na tela)
            chaves = list(json_data[0].keys())[:6]
            colunas = [ft.DataColumn(ft.Text(k.upper(), weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY)) for k in chaves]
            
            linhas = []
            for item in json_data:
                # Transforma cada item em uma célula, convertendo para string
                celulas = [ft.DataCell(ft.Text(str(item.get(k, "")), size=12)) for k in chaves]
                linhas.append(ft.DataRow(cells=celulas))

            tabela = ft.DataTable(columns=colunas, rows=linhas, border=ft.border.all(1, ft.Colors.SECONDARY))
            self.sanitized_view.controls.append(ft.Row([tabela], scroll=ft.ScrollMode.ALWAYS))

        # Cenário 2: É um único objeto (Ideal para criar uma lista de propriedades)
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
        
        # Cenário 3: Formato desconhecido
        else:
            self.sanitized_view.controls.append(ft.Text("Os dados foram recebidos, mas o formato é muito simples para sanitização complexa."))