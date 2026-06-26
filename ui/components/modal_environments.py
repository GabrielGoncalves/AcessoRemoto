import flet as ft
from database.db_manager import DatabaseManager

class ModalNovoAmbiente(ft.AlertDialog):
    def __init__(self, db: DatabaseManager, on_success_callback):
        super().__init__()
        self.db = db
        self.on_success = on_success_callback
        
        self.txt_nome = ft.TextField(label="Nome do Ambiente (ex: Produção)", autofocus=True, border_color="#4e54c8")
        
        self.title = ft.Text("Cadastrar Novo Ambiente")
        self.content = ft.Column([self.txt_nome], tight=True)
        
        self.actions = [
            ft.TextButton("Cancelar", on_click=self.fechar),
            ft.ElevatedButton("Salvar", on_click=self.salvar, bgcolor="green", color="white")
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def salvar(self, e):
        if self.txt_nome.value:
            self.db.adicionar_ambiente(self.txt_nome.value.strip())
            self.txt_nome.value = ""
            self.page.pop_dialog()
            if self.on_success:
                self.on_success()

    def fechar(self, e):
        self.page.pop_dialog()