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
                "surface_container": "#242438",           
                "secondary_container": "#222235",  
                "primary": "#00d2ff",              
                "on_primary": ft.Colors.BLACK,     
                "secondary": "#4e54c8",            
                "on_surface": ft.Colors.WHITE,     
                "on_surface_variant": "#e2e8f0"    
            },
            "neon_tokyo": {  # Vibe Synthwave, com roxo profundo e rosa choque
                "surface": "#0f0f1b",
                "surface_container": "#252540",
                "surface_variant": "#1a1a2e",
                "secondary_container": "#252540",
                "primary": "#ff2a6d",              # Rosa Neon
                "on_primary": ft.Colors.WHITE,
                "secondary": "#05d9e8",            # Ciano
                "on_surface": ft.Colors.WHITE,
                "on_surface_variant": "#d1d1e0"
            },
            "floresta_boreal": {  # Tons de verde escuro e esmeralda, muito relaxante
                "surface": "#0d1a15",
                "surface_container": "#1f3b2f",
                "surface_variant": "#162a22",
                "secondary_container": "#1f3b2f",
                "primary": "#2ecc71",              # Verde Esmeralda
                "on_primary": ft.Colors.BLACK,
                "secondary": "#f1c40f",            # Amarelo Sol
                "on_surface": ft.Colors.WHITE,
                "on_surface_variant": "#b3d4c6"
            },
            "cafe_expresso": {  # Tons amadeirados e quentes (sépia escuro)
                "surface": "#1c1714",
                "surface_container": "#3e322c",
                "surface_variant": "#2b231f",
                "secondary_container": "#3e322c",
                "primary": "#d4a373",              # Cor de Latte/Caramelo
                "on_primary": ft.Colors.BLACK,
                "secondary": "#e9edc9",
                "on_surface": ft.Colors.WHITE,
                "on_surface_variant": "#d1c7c3"
            },
            "dracula_dev": {  # Baseado no famoso tema Drácula de editores de código
                "surface": "#282a36",
                "surface_container": "#44475a",
                "surface_variant": "#343746",
                "secondary_container": "#44475a",
                "primary": "#bd93f9",              # Roxo suave
                "on_primary": ft.Colors.BLACK,
                "secondary": "#ff79c6",            # Rosa pastel
                "on_surface": "#f8f8f2",
                "on_surface_variant": "#6272a4"
            },
            
            # ==========================================
            # TEMAS CLAROS (LIGHT MODE)
            # ==========================================
            "gelo_claro": {  # O claro tradicional, muito profissional
                "surface": "#f4f5f7",
                "surface_container": "#e2e8f0",
                "surface_variant": "#ffffff",
                "secondary_container": "#e2e8f0",
                "primary": "#0077b6",              # Azul corporativo
                "on_primary": ft.Colors.WHITE,
                "secondary": "#bdbdbd",
                "on_surface": ft.Colors.BLACK,
                "on_surface_variant": "#555555"
            },
            "creme_de_baunilha": {  # Um tema claro aquecido, estilo páginas de livro antigo
                "surface": "#fdf6e3",              # Bege clarinho
                "surface_container": "#e1dabb",
                "surface_variant": "#eee8d5",
                "secondary_container": "#e1dabb",
                "primary": "#b58900",              # Mostarda
                "on_primary": ft.Colors.WHITE,
                "secondary": "#cb4b16",            # Laranja queimado
                "on_surface": "#073642",
                "on_surface_variant": "#586e75"
            },
            
            # ==========================================
            # TEMAS VIBRANTES
            # ==========================================
            "cereja_doce": {  # Tons de vinho e vermelho
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
            "outono_fazenda": {  # Tons de laranja e terra
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
        
        # Fallback de segurança: se o tema não existir, carrega o cyberpunk original
        c = paletas.get(nome_tema.lower().strip(), paletas["cyberpunk"])
        
        return ft.Theme(
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