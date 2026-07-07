import flet as ft
from database.db_manager import DatabaseManager

class ModalNovaConexaoAmbiente(ft.AlertDialog):
    def __init__(self, db: DatabaseManager, on_success_callback):
        super().__init__()
        self.db = db
        self.on_success = on_success_callback
        self.ambiente_id = None

        self.txt_nome = ft.TextField(label="Nome de Exibição", autofocus=True, border_color=ft.Colors.SECONDARY)
        self.txt_ip = ft.TextField(label="IP / Hostname", border_color=ft.Colors.SECONDARY)
        self.txt_user = ft.TextField(label="Usuário (Opcional)", hint_text="Deixe vazio para usar o Global", border_color=ft.Colors.SECONDARY)

        self.title = ft.Row([ft.Icon(ft.Icons.ADD_LINK, color=ft.Colors.PRIMARY), ft.Text("Vincular Acesso", size=18, weight=ft.FontWeight.BOLD)])
        self.content = ft.Column([self.txt_nome, self.txt_ip, self.txt_user], tight=True, spacing=10)

        self.actions = [
            ft.TextButton("Cancelar", on_click=self.fechar),
            ft.ElevatedButton("Salvar", on_click=self.salvar, bgcolor=ft.Colors.PRIMARY, color=ft.Colors.ON_PRIMARY)
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def configurar_ambiente(self, ambiente_id):
        self.ambiente_id = ambiente_id

    def salvar(self, e):
        nome = self.txt_nome.value.strip() if self.txt_nome.value else ""
        ip = self.txt_ip.value.strip() if self.txt_ip.value else ""
        user = self.txt_user.value.strip() if self.txt_user.value else ""
        
        if nome and ip and self.ambiente_id:
            self.db.adicionar_conexao_ambiente(self.ambiente_id, nome, ip, user)
            
            self.txt_nome.value = ""
            self.txt_ip.value = ""
            self.txt_user.value = ""
            
            self.page.pop_dialog()
            if self.on_success:
                self.on_success()

    def fechar(self, e):
        self.txt_nome.value = ""
        self.txt_ip.value = ""
        self.txt_user.value = ""
        self.page.pop_dialog()