import flet as ft

class PrimaryButton(ft.ElevatedButton):
    def __init__(self, text: str, icon_name: str = None, **kwargs):
        super().__init__(**kwargs)
        self.bgcolor = ft.Colors.PRIMARY
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=20),
            padding=15
        )
        
        conteudo = []
        if icon_name:
            conteudo.append(ft.Icon(icon_name, color=ft.Colors.ON_PRIMARY))
        
        conteudo.append(ft.Text(text, color=ft.Colors.ON_PRIMARY, weight=ft.FontWeight.BOLD))
        
        self.content = ft.Row(controls=conteudo, alignment=ft.MainAxisAlignment.CENTER)