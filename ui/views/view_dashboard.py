import flet as ft
from database.db_manager import DatabaseManager

class DashboardView(ft.Container):
    def __init__(self, db: DatabaseManager, on_connect_action):
        super().__init__()
        self.db = db
        self.on_connect_action = on_connect_action
        self.expand = True
        
        # Inputs focados unicamente em conexões rápidas e avulsas
        self.txt_ip = ft.TextField(label="IP / Hostname", border_color="#4e54c8")
        self.txt_user = ft.TextField(label="Usuário", border_color="#4e54c8")
        self.txt_pass = ft.TextField(label="Senha", password=True, can_reveal_password=True, border_color="#4e54c8")
        self.chk_favorito = ft.Checkbox(label="Marcar como Favorito", value=False)
        
        # Lista lateral focada no histórico global
        self.lv_historico = ft.ListView(expand=True, spacing=10)

        self.build_ui()

    def build_ui(self):
        col_form = ft.Container(
            content=ft.Column([
                ft.Row([ft.Text("Acesso Rápido", size=18, weight="bold")]),
                self.txt_ip,
                self.txt_user,
                self.txt_pass,
                self.chk_favorito,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                
                # Botão corrigido (sem o 'mouse_cursor' que causava o TypeError)
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.PLAY_ARROW),
                        ft.Text("Conectar")
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    color="black", 
                    bgcolor="#00d2ff",
                    on_click=self._btn_conectar_clicked
                )
            ], spacing=12),
            padding=20, bgcolor="#161623", border_radius=12, expand=1
        )

        col_historico = ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(ft.Icons.HISTORY, color="#00d2ff"), ft.Text("Conexões Recentes", size=18, weight="bold")]),
                self.lv_historico
            ]),
            padding=20, bgcolor="#161623", border_radius=12, expand=1
        )

        self.content = ft.Row([col_form, col_historico], spacing=15, expand=True)

    def did_mount(self):
        # Atualiza a lista lateral buscando o histórico geral do banco
        self._atualizar_lista_historico()

    def _atualizar_lista_historico(self):
        self.lv_historico.controls.clear()
        
        # Agora retorna: id, nome_exibicao, ip, user, e_favorito
        historico = self.db.listar_historico(limite=10)
        
        for id_, nome_exibicao, ip, user, e_favorito in historico:
            is_fav = bool(e_favorito) # True se a contagem for maior que 0
            
            self.lv_historico.controls.append(
                ft.Container(
                    content=ft.Row([
                        # O monitor fica amarelo se o IP estiver nos favoritos!
                        ft.Icon(ft.Icons.MONITOR, color="yellow" if is_fav else "#00d2ff"),
                        ft.Column([
                            ft.Text(f"IP: {ip}", weight="bold"),
                            ft.Text(f"User: {user}", size=12, color=ft.Colors.GREY_400)
                        ], expand=True),
                        ft.IconButton(
                            icon=ft.Icons.ARROW_FORWARD,
                            icon_color="green",
                            on_click=lambda e, cip=ip, cuser=user: self._preencher_form(cip, cuser)
                        )
                    ]),
                    bgcolor="#222235", padding=10, border_radius=8
                )
            )
        self.update()

    def _preencher_form(self, ip, user):
        self.txt_ip.value = ip
        self.txt_user.value = user
        self.txt_pass.value = ""
        self.txt_pass.focus()
        self.update()

    def _btn_conectar_clicked(self, e):
        # Validação simples de campos obrigatórios
        if not self.txt_ip.value or not self.txt_user.value:
            return
        
        ip = self.txt_ip.value.strip()
        user = self.txt_user.value.strip()
        senha = self.txt_pass.value

        # 1. Se o usuário quiser salvar como favorito permanente
        if self.chk_favorito.value:
            self.db.adicionar_favorito(ip, ip, user)
            
        # 2. Registra no histórico geral de acessos
        self.db.registrar_historico(ip, ip, user)
        
        # 3. Atualiza os cards visuais do histórico do painel direito
        self._atualizar_lista_historico()
        
        # 4. Dispara o subprocesso RDP de forma 100% autônoma
        self.on_connect_action(ip, user, senha)