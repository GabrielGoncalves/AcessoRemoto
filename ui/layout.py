import flet as ft

class AppTheme:
    """
    Centraliza a engine de temas do RemoteCraft.
    Para adicionar um novo tema, basta registrar sua paleta de cores no catálogo.
    """
    
    @staticmethod
    def get_theme(nome_tema: str) -> ft.Theme:
        # Catálogo centralizado de temas criativos do sistema
        paletas = {
            "cyberpunk": {
                "surface": "#1a1a2e",              
                "secondary_container": "#222235",  
                "primary": "#00d2ff",              
                "on_primary": ft.Colors.BLACK,     
                "secondary": "#4e54c8",            
                "on_surface": ft.Colors.WHITE,     
                "on_surface_variant": "#e2e8f0"    
            },
            "cereja_doce": {
                "surface": "#2b1219",
                "secondary_container": "#532537",
                "primary": "#ff4d6d",
                "on_primary": ft.Colors.WHITE,
                "secondary": "#c9184a",
                "on_surface": ft.Colors.WHITE,
                "on_surface_variant": "#ffb5a7"
            },
            "outono_fazenda": {
                "surface": "#2e1c10",
                "secondary_container": "#5c3921",
                "primary": "#f77f00",
                "on_primary": ft.Colors.BLACK,
                "secondary": "#d62828",
                "on_surface": ft.Colors.WHITE,
                "on_surface_variant": "#fae0c4"
            },
            "gelo_claro": {
                "surface": "#f4f5f7",
                "secondary_container": "#e2e8f0",
                "primary": "#0077b6",
                "on_primary": ft.Colors.WHITE,
                "secondary": "#bdbdbd",
                "on_surface": ft.Colors.BLACK,
                "on_surface_variant": "#555555"
            }
        }
        
        # Fallback de segurança: se o tema não existir, carrega o cyberpunk original
        c = paletas.get(nome_tema.lower().strip(), paletas["cyberpunk"])
        
        return ft.Theme(
            color_scheme=ft.ColorScheme(
                surface=c["surface"],
                secondary_container=c["secondary_container"],
                primary=c["primary"],
                on_primary=c["on_primary"],
                secondary=c["secondary"],
                on_surface=c["on_surface"],
                on_surface_variant=c["on_surface_variant"]
            )
        )