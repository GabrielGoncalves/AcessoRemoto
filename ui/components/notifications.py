import flet as ft

class Notification:
    @staticmethod
    def _show_snackbar(page: ft.Page, message: str, bgcolor: str, icon_name: str):
        """Método base privado que monta o SnackBar padronizado"""
        snack = ft.SnackBar(
            content=ft.Row(
                controls=[
                    ft.Icon(icon_name, color=ft.Colors.WHITE, size=20),
                    ft.Text(message, color=ft.Colors.WHITE, size=14, weight=ft.FontWeight.W_500)
                ],
                alignment=ft.MainAxisAlignment.CENTER # Centraliza o ícone e o texto
            ),
            bgcolor=bgcolor,
            margin=50,                             # Afasta das bordas da tela
            duration=3000                          # Some automaticamente após 3 segundos
        )
        page.show_dialog(snack)

    @staticmethod
    def show_success(page: ft.Page, message: str):
        Notification._show_snackbar(page, message, bgcolor=ft.Colors.GREEN_700, icon_name=ft.Icons.CHECK_CIRCLE)

    @staticmethod
    def show_error(page: ft.Page, message: str):
        Notification._show_snackbar(page, message, bgcolor=ft.Colors.RED_700, icon_name=ft.Icons.ERROR)

    @staticmethod
    def show_info(page: ft.Page, message: str):
        Notification._show_snackbar(page, message, bgcolor=ft.Colors.BLUE_700, icon_name=ft.Icons.INFO)

    @staticmethod
    def show_warning(page: ft.Page, message: str):
        Notification._show_snackbar(page, message, bgcolor=ft.Colors.ORANGE_700, icon_name=ft.Icons.WARNING_AMBER)