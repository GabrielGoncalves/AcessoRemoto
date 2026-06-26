import flet as ft

class ModernTextField(ft.TextField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border = ft.InputBorder.OUTLINE
        self.bgcolor = ft.Colors.TRANSPARENT
        self.border_color = ft.Colors.SECONDARY
        self.label_style = ft.TextStyle(color=ft.Colors.ON_SURFACE_VARIANT)