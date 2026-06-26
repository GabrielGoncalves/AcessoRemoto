import flet as ft
from database.db_manager import DatabaseManager

class ModalNovoFavorito(ft.AlertDialog):
    def __init__(self, db: DatabaseManager, on_success_callback):
        super().__init__()
        self.db = db
        self.on_success = on_success_callback
        
        self.txt_nome = ft.TextField(label="Nome de Exibição", autofocus=True, border_color="#4e54c8")
        self.txt_ip = ft.TextField(label="IP / Hostname", border_color="#4e54c8")
        self.txt_user = ft.TextField(label="Usuário", border_color="#4e54c8")
        
        self.title = ft.Text("Cadastrar Favorito")
        self.content = ft.Column([self.txt_nome, self.txt_ip, self.txt_user], tight=True, spacing=10)
        
        self.actions = [
            ft.TextButton("Cancelar", on_click=self.fechar),
            ft.ElevatedButton("Salvar", on_click=self.salvar, bgcolor="green", color="white")
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def salvar(self, e):
        if self.txt_nome.value and self.txt_ip.value and self.txt_user.value:
            self.db.adicionar_favorito(
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