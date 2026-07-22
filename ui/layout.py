import flet as ft

class AppTheme:
    """
    Centralizador da engine de temas.
    Para adicionar um novo tema, basta registrar sua paleta de cores no catálogo e criar o dropdown no view_settings.
    """
    
    @staticmethod
    def get_theme(nome_tema: str):
        paletas = {
            "cyberpunk": {  
                "mode": ft.ThemeMode.DARK,
                "surface": "#1a1a2e",   
                "surface_container": "#242438",           
                "secondary_container": "#222235",  
                "primary": "#00d2ff",              
                "on_primary": ft.Colors.BLACK,     
                "secondary": "#4e54c8",            
                "on_surface": ft.Colors.WHITE,     
                "on_surface_variant": "#e2e8f0"    
            },
            "neon_tokyo": {  
                "mode": ft.ThemeMode.DARK,
                "surface": "#0f0f1b",
                "surface_container": "#252540",
                "surface_variant": "#1a1a2e",
                "secondary_container": "#252540",
                "primary": "#ff2a6d",
                "on_primary": ft.Colors.WHITE,
                "secondary": "#05d9e8",
                "on_surface": ft.Colors.WHITE,
                "on_surface_variant": "#d1d1e0"
            },
            "floresta_boreal": {  
                "mode": ft.ThemeMode.DARK,
                "surface": "#0d1a15",
                "surface_container": "#1f3b2f",
                "surface_variant": "#162a22",
                "secondary_container": "#1f3b2f",
                "primary": "#2ecc71",
                "on_primary": ft.Colors.BLACK,
                "secondary": "#f1c40f",
                "on_surface": ft.Colors.WHITE,
                "on_surface_variant": "#b3d4c6"
            },
            "cafe_expresso": {  
                "mode": ft.ThemeMode.DARK,
                "surface": "#1c1714",
                "surface_container": "#3e322c",
                "surface_variant": "#2b231f",
                "secondary_container": "#3e322c",
                "primary": "#d4a373",
                "on_primary": ft.Colors.BLACK,
                "secondary": "#e9edc9",
                "on_surface": ft.Colors.WHITE,
                "on_surface_variant": "#d1c7c3"
            },
            "dracula_dev": {  
                "mode": ft.ThemeMode.DARK,
                "surface": "#282a36",
                "surface_container": "#44475a",
                "surface_variant": "#343746",
                "secondary_container": "#44475a",
                "primary": "#bd93f9",
                "on_primary": ft.Colors.BLACK,
                "secondary": "#ff79c6",        
                "on_surface": "#f8f8f2",
                "on_surface_variant": "#6272a4"
            },
            
            # ==========================================
            # TEMAS CLAROS (LIGHT MODE)
            # ==========================================
            "gelo_claro": {  
                "mode": ft.ThemeMode.LIGHT,
                "surface": "#f4f5f7",
                "surface_container": "#e2e8f0",
                "surface_variant": "#ffffff",
                "secondary_container": "#e2e8f0",
                "primary": "#0077b6",
                "on_primary": ft.Colors.WHITE,
                "secondary": "#bdbdbd",
                "on_surface": ft.Colors.BLACK,
                "on_surface_variant": "#555555"
            },
            "creme_de_baunilha": {  
                "mode": ft.ThemeMode.LIGHT,
                "surface": "#fdf6e3",
                "surface_container": "#e1dabb",
                "surface_variant": "#eee8d5",
                "secondary_container": "#e1dabb",
                "primary": "#b58900",          
                "on_primary": ft.Colors.WHITE,
                "secondary": "#cb4b16", 
                "on_surface": "#073642",
                "on_surface_variant": "#586e75"
            },
            
            # ==========================================
            # TEMAS VIBRANTES
            # ==========================================
            "cereja_doce": {  
                "mode": ft.ThemeMode.DARK,
                "surface": "#2b1219",
                "surface_container": "#532537",
                "surface_variant": "#3d1c28",
                "secondary_container": "#532537",
                "primary": "#ff4d6d",
                "on_primary": ft.Colors.WHITE,
                "secondary": "#c9184a",
                "on_surface": ft.Colors.WHITE,
                "on_surface_variant": "#ffb5a7"
            },
            "outono_fazenda": {  
                "mode": ft.ThemeMode.DARK,
                "surface": "#2e1c10",
                "surface_container": "#5c3921",
                "surface_variant": "#422918",
                "secondary_container": "#5c3921",
                "primary": "#f77f00",
                "on_primary": ft.Colors.BLACK,
                "secondary": "#d62828",
                "on_surface": ft.Colors.WHITE,
                "on_surface_variant": "#fae0c4"
            }
        }
        
        # Fallback de segurança: se o tema não existir, carrega o cyberpunk
        c = paletas.get(nome_tema.lower().strip(), paletas["cyberpunk"])
        
        tema_obj = ft.Theme(
            color_scheme=ft.ColorScheme(
                surface=c["surface"],
                surface_container=c["surface_container"],
                secondary_container=c["secondary_container"],
                primary=c["primary"],
                on_primary=c["on_primary"],
                secondary=c["secondary"],
                on_surface=c["on_surface"],
                on_surface_variant=c["on_surface_variant"]
            )
        )
        
        return tema_obj, c["mode"]