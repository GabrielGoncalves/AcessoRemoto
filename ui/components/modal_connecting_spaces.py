import flet as ft
from database.db_manager import DatabaseManager

class ModalNovaConexaoAmbiente(ft.AlertDialog):
    def __init__(self, db: DatabaseManager, on_success_callback):
        super().__init__()
        self.db = db
        self.on_success = on_success_callback
        self.ambiente_id = None
        
        self.txt_nome = ft.TextField(label="Nome de Exibição (ex: Servidor Web)", autofocus=True, border_color="#4e54c8")
        self.txt_ip = ft.TextField(label="IP / Hostname", border_color="#4e54c8")
        self.txt_user = ft.TextField(label="Usuário", border_color="#4e54c8")
        
        self.title = ft.Text("Adicionar Conexão ao Ambiente")
        self.content = ft.Column([self.txt_nome, self.txt_ip, self.txt_user], tight=True, spacing=10)
        
        self.actions = [
            ft.TextButton("Cancelar", on_click=self.fechar),
            ft.ElevatedButton("Salvar", on_click=self.salvar, bgcolor="green", color="white")
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def configurar_ambiente(self, ambiente_id):
        """Injeta o ID do ambiente ativo antes de abrir o modal"""
        self.ambiente_id = ambiente_id

    def salvar(self, e):
        if self.ambiente_id and self.txt_nome.value and self.txt_ip.value and self.txt_user.value:
            self.db.adicionar_conexao_ambiente(
                self.ambiente_id,
                self.txt_nome.value.strip(),
                self.txt_ip.value.strip(),
                self.txt_user.value.strip()
            )
            self.txt_nome.value = ""
            self.txt_ip.value = ""
            self.txt_user.value = ""
            self.page.pop_dialog()
            if self.on_success:
                self.on_success()

    def fechar(self, e):
        self.page.pop_dialog()