import flet as ft
from database.db_manager import DatabaseManager

class ModalNovoAmbiente(ft.AlertDialog):
    def __init__(self, db: DatabaseManager, on_success_callback):
        super().__init__()
        self.db = db
        self.on_success = on_success_callback

        self.txt_nome = ft.TextField(label="Nome do Ambiente (Ex: Cliente X)", autofocus=True, border_color=ft.Colors.SECONDARY)

        self.title = ft.Row([ft.Icon(ft.Icons.CREATE_NEW_FOLDER, color=ft.Colors.PRIMARY), ft.Text("Novo Ambiente", size=18, weight=ft.FontWeight.BOLD)])
        self.content = self.txt_nome

        self.actions = [
            ft.TextButton("Cancelar", on_click=self.fechar),
            ft.ElevatedButton("Salvar", on_click=self.salvar, bgcolor=ft.Colors.PRIMARY, color=ft.Colors.ON_PRIMARY)
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def salvar(self, e):
        nome = self.txt_nome.value.strip() if self.txt_nome.value else ""
        if nome:
            sucesso = self.db.adicionar_ambiente(nome)
            if sucesso:
                self.txt_nome.value = ""
                self.txt_nome.error_text = None
                
                # Desempilha o modal de forma nativa e segura
                self.page.pop_dialog()
                
                if self.on_success:
                    self.on_success()
            else:
                self.txt_nome.error_text = "Já existe um ambiente com este nome."
                self.txt_nome.update()

    def fechar(self, e):
        self.txt_nome.value = ""
        self.txt_nome.error_text = None
        self.page.pop_dialog()