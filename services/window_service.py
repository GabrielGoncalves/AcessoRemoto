import flet as ft
from database.db_manager import DatabaseManager

class WindowService:
    DEFAULT_WIDTH = 900
    DEFAULT_HEIGHT = 700
    MIN_WIDTH = 700
    MIN_HEIGHT = 500

    def __init__(self, page: ft.Page, db: DatabaseManager):
        self.page = page
        self.db = db

    def inicializar_janela(self):
        """Aplica limites e carrega o último tamanho/estado salvo (se a flag estiver ativa)"""
        self.page.window.min_width = self.MIN_WIDTH
        self.page.window.min_height = self.MIN_HEIGHT

        lembrar = self.db.obter_configuracao("lembrar_tamanho_janela", "0") == "1"

        if lembrar:
            maximizado = self.db.obter_configuracao("window_maximized", "0") == "1"
            largura = float(self.db.obter_configuracao("window_width", str(self.DEFAULT_WIDTH)))
            altura = float(self.db.obter_configuracao("window_height", str(self.DEFAULT_HEIGHT)))

            self.page.window.width = largura
            self.page.window.height = altura
            self.page.window.maximized = maximizado
        else:
            self.page.window.maximized = False
            self.page.window.width = self.DEFAULT_WIDTH
            self.page.window.height = self.DEFAULT_HEIGHT
            
        self.page.update()

    def salvar_tamanho_atual(self):
        """Salva a dimensão exata e o estado da janela no momento do clique"""
        # Ativa a flag de lembrar automaticamente
        self.db.salvar_configuracao("lembrar_tamanho_janela", "1")
        
        is_maximized = self.page.window.maximized
        self.db.salvar_configuracao("window_maximized", "1" if is_maximized else "0")
        
        # Só salva a resolução numérica se não estiver em tela cheia
        if not is_maximized and self.page.window.width and self.page.window.height:
            self.db.salvar_configuracao("window_width", str(int(self.page.window.width)))
            self.db.salvar_configuracao("window_height", str(int(self.page.window.height)))

    def restaurar_padrao(self):
        """Restaura as dimensões, desativa o salvamento automático e atualiza o banco"""
        # Desativa a flag para voltar a abrir no padrão
        self.db.salvar_configuracao("lembrar_tamanho_janela", "0")
        
        self.page.window.maximized = False
        self.page.window.width = self.DEFAULT_WIDTH
        self.page.window.height = self.DEFAULT_HEIGHT
        
        self.db.salvar_configuracao("window_maximized", "0")
        self.db.salvar_configuracao("window_width", str(self.DEFAULT_WIDTH))
        self.db.salvar_configuracao("window_height", str(self.DEFAULT_HEIGHT))
        self.page.update()