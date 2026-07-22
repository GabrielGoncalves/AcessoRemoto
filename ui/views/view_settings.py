import flet as ft
import json
import os
import shutil
from database.db_manager import DatabaseManager
from services.password_service import PasswordService
from services.window_service import WindowService
from ui.components.notifications import Notification

class ViewSettings(ft.Container):
    def __init__(self, db: DatabaseManager, window_service: WindowService, on_dev_mode_change=None):
        super().__init__()
        self.db = db
        self.on_dev_mode_change = on_dev_mode_change
        self.expand = True
        self.padding = 20
        self.window_service = window_service
        self.build_ui()

    def build_ui(self):
        tabs_controller = ft.Tabs(
            length=5,
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.TabBar(
                        scrollable=True,                    
                        tab_alignment=ft.TabAlignment.START,
                        tabs=[
                            ft.Tab(label="Sessão & Segurança", icon=ft.Icons.SECURITY),
                            ft.Tab(label="Identidades", icon=ft.Icons.PEOPLE_ALT),
                            ft.Tab(label="Dados & Backup", icon=ft.Icons.DATA_USAGE),
                            ft.Tab(label="Personalização", icon=ft.Icons.PALETTE),
                            ft.Tab(label="Avançado", icon=ft.Icons.CODE),
                        ]
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            self._criar_aba_seguranca(),
                            self._criar_aba_identidades(),
                            self._criar_aba_dados(),
                            self._criar_aba_personalizacao(),
                            self._criar_aba_avancado(),
                        ],
                    ),
                ],
            ),
        )
        
        self.content = ft.Column([
            ft.Text("Configurações do Sistema", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(color=ft.Colors.SECONDARY),
            tabs_controller
        ], expand=True)
    
    # ==========================================
    # ABA 1: SESSÃO & SEGURANÇA
    # ==========================================
    def _criar_aba_seguranca(self):
        def alternar_flag_seguranca(e):
            valor_salvar = "1" if e.control.value else "0"
            self.db.salvar_configuracao("exigir_senha_sessao", valor_salvar)
            
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Configuração de segurança atualizada!"),
                bgcolor=ft.Colors.SECONDARY
            )
            self.page.snack_bar.open = True
            self.page.update()

        flag_atual = self.db.obter_configuracao("exigir_senha_sessao", "0")
        estado_switch = True if flag_atual == "1" else False

        txt_senha_gerada = ft.TextField(
            hint_text="Gerador de Senha",
            hint_style=ft.TextStyle(color=ft.Colors.GREY),
            read_only=True,
            border_color=ft.Colors.SECONDARY,
            expand=True
        )
        
        slider_comprimento = ft.Slider(
            min=8, max=32, divisions=24,
            label="{value} caracteres", value=16
        )

        def gerar_senha_aleatoria(e):
            comprimento = int(slider_comprimento.value)
            senha_final = PasswordService.generate_safe_password(length=comprimento)
            txt_senha_gerada.value = senha_final
            txt_senha_gerada.update()

        async def copiar_senha_clipboard(e):
            if txt_senha_gerada.value:
                await ft.Clipboard().set(txt_senha_gerada.value)                    
                txt_senha_gerada.value = ""
                self.page.update()

        return ft.Container(
            content=ft.ListView([
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.LOCK, color=ft.Colors.PRIMARY),
                                ft.Text("Segurança de Credenciais", size=16, weight=ft.FontWeight.BOLD)
                            ]),
                            ft.Divider(color=ft.Colors.SECONDARY),
                            ft.Text(
                                "Determine como a interface do aplicativo gerencia dados sensíveis após disparar conexões.",
                                size=12, color=ft.Colors.ON_SURFACE_VARIANT
                            ),
                            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                            ft.Switch(
                                label="Lembrar senha da sessão após conectar (Desative para limpar o campo por segurança)",
                                value=estado_switch,
                                on_change=alternar_flag_seguranca,
                                active_color=ft.Colors.PRIMARY
                            ),
                        ]), padding=15
                    ), bgcolor=ft.Colors.SURFACE_CONTAINER
                ),

                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.PASSWORD, color=ft.Colors.PRIMARY),
                                ft.Text("Gerador de Senhas Avançado", size=16, weight=ft.FontWeight.BOLD)
                            ]),
                            ft.Divider(color=ft.Colors.SECONDARY),
                            ft.Text("Gere senhas randômicas de alta complexidade para usar nos seus servidores remotos.", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                            ft.Text("Comprimento da Senha:", size=13, weight=ft.FontWeight.W_500),
                            slider_comprimento,
                            ft.Row([
                                txt_senha_gerada,
                                ft.IconButton(
                                    icon=ft.Icons.COPY,
                                    icon_color=ft.Colors.PRIMARY,
                                    tooltip="Copiar Senha",
                                    on_click=copiar_senha_clipboard
                                )
                            ], spacing=10),
                            ft.ElevatedButton(
                                "Gerar Nova Senha",
                                icon=ft.Icons.REFRESH,
                                bgcolor=ft.Colors.PRIMARY,
                                color=ft.Colors.ON_PRIMARY,
                                on_click=gerar_senha_aleatoria
                            )
                        ]), padding=15
                    ), bgcolor=ft.Colors.SURFACE_CONTAINER
                )
            ], spacing=15), padding=15
        )

    # ==========================================
    # ABA 2: IDENTIDADES
    # ==========================================
    def _criar_aba_identidades(self):
        txt_novo_user = ft.TextField(label="Novo Usuário", expand=True, border_color=ft.Colors.SECONDARY)
        txt_novo_dom = ft.TextField(label="Novo Domínio (ex: empresa.local)", expand=True, border_color=ft.Colors.SECONDARY)
        lv_users = ft.ListView(expand=True, spacing=5)
        lv_dominios = ft.ListView(expand=True, spacing=5)

        def atualizar_lista_usuarios():
            lv_users.controls.clear()
            for id_, nome in self.db.listar_usuarios():
                lv_users.controls.append(
                    ft.Row([
                        ft.Icon(ft.Icons.PERSON_OUTLINE, size=18, color=ft.Colors.ON_SURFACE_VARIANT),
                        ft.Text(nome, expand=True, size=13),
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.ERROR, icon_size=16,
                            on_click=lambda e, uid=id_: remover_usuario(uid)
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )
            try:
                lv_users.update()
            except Exception:
                pass

        def atualizar_lista_dominios():
            lv_dominios.controls.clear()
            for id_, dom in self.db.listar_dominios():
                lv_dominios.controls.append(
                    ft.Row([
                        ft.Icon(ft.Icons.DOMAIN_OUTLINED, size=18, color=ft.Colors.ON_SURFACE_VARIANT),
                        ft.Text(dom, expand=True, size=13),
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.ERROR, icon_size=16,
                            on_click=lambda e, did=id_: remover_dominio(did)
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )
            try:
                lv_dominios.update()
            except Exception:
                pass
        
        self.atualizar_lista_usuarios = atualizar_lista_usuarios
        self.atualizar_lista_dominios = atualizar_lista_dominios

        def salvar_usuario(e):
            nome = txt_novo_user.value.strip()
            if nome and self.db.adicionar_usuario(nome):
                txt_novo_user.value = ""
                txt_novo_user.update()
                atualizar_lista_usuarios()

        def remover_usuario(uid):
            self.db.excluir_usuario(uid)
            atualizar_lista_usuarios()

        def salvar_dominio(e):
            dominio = txt_novo_dom.value.strip()
            if dominio and self.db.adicionar_dominio(dominio):
                txt_novo_dom.value = ""
                txt_novo_dom.update()
                atualizar_lista_dominios()

        def remover_dominio(did):
            self.db.excluir_dominio(did)
            atualizar_lista_dominios()

        def alternar_flag_user_padrao(e):
            self.db.salvar_configuracao("usar_usuario_padrao", "1" if e.control.value else "0")

        def alternar_flag_dominio_padrao(e):
            self.db.salvar_configuracao("usar_dominio_padrao", "1" if e.control.value else "0")
            
        def atualizar_texto_user_padrao(e):
            self.db.salvar_configuracao("usuario_padrao_texto", e.control.value.strip())

        def atualizar_texto_dominio_padrao(e):
            self.db.salvar_configuracao("dominio_padrao_texto", e.control.value.strip())

        flag_user = self.db.obter_configuracao("usar_usuario_padrao", "0") == "1"
        flag_dom = self.db.obter_configuracao("usar_dominio_padrao", "0") == "1"
        val_user_padrao = self.db.obter_configuracao("usuario_padrao_texto", "")
        val_dom_padrao = self.db.obter_configuracao("dominio_padrao_texto", "")

        atualizar_lista_usuarios()
        atualizar_lista_dominios()

        return ft.Container(
            content=ft.Column([
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Configurações de Identidade Inicial (Boot)", size=14, weight=ft.FontWeight.BOLD),
                            ft.Divider(color=ft.Colors.SECONDARY, height=5),
                            ft.Row([
                                ft.Column([
                                    ft.Switch(label="Iniciar com Usuário Padrão", value=flag_user, on_change=alternar_flag_user_padrao, active_color=ft.Colors.PRIMARY),
                                    ft.TextField(label="Definir Usuário Padrão", value=val_user_padrao, on_change=atualizar_texto_user_padrao, width=250, border_color=ft.Colors.SECONDARY)
                                ], spacing=5),
                                ft.VerticalDivider(width=20),
                                ft.Column([
                                    ft.Switch(label="Iniciar com Domínio Padrão", value=flag_dom, on_change=alternar_flag_dominio_padrao, active_color=ft.Colors.PRIMARY),
                                    ft.TextField(label="Definir Domínio Padrão", value=val_dom_padrao, on_change=atualizar_texto_dominio_padrao, width=250, border_color=ft.Colors.SECONDARY)
                                ], spacing=5),
                            ], alignment=ft.MainAxisAlignment.START, spacing=30)
                        ]), padding=12
                    ), bgcolor=ft.Colors.SURFACE_CONTAINER
                ),
                
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Usuários Recorrentes", size=15, weight=ft.FontWeight.BOLD),
                            ft.Row([txt_novo_user, ft.IconButton(ft.Icons.ADD, icon_color=ft.Colors.PRIMARY, on_click=salvar_usuario)]),
                            ft.Divider(color=ft.Colors.SECONDARY, height=5),
                            lv_users 
                        ]), expand=1, bgcolor=ft.Colors.SURFACE_CONTAINER, padding=12, border_radius=8
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Domínios Corporativos", size=15, weight=ft.FontWeight.BOLD),
                            ft.Row([txt_novo_dom, ft.IconButton(ft.Icons.ADD, icon_color=ft.Colors.PRIMARY, on_click=salvar_dominio)]),
                            ft.Divider(color=ft.Colors.SECONDARY, height=5),
                            lv_dominios 
                        ]), expand=1, bgcolor=ft.Colors.SURFACE_CONTAINER, padding=12, border_radius=8
                    )
                ], spacing=15, expand=True)
            ], spacing=15), padding=15
        )

    # ==========================================
    # ABA 3: DADOS & BACKUP
    # ==========================================
    def _criar_aba_dados(self):
        # ------------------------------------------
        # LÓGICA 1: RETENÇÃO DE HISTÓRICO
        # ------------------------------------------
        retencao_atual = str(self.db.obter_configuracao("retencao_historico_dias", "0"))
        
        def alterar_retencao(e):
            valor_escolhido = str(e.control.value)
            self.db.salvar_configuracao("retencao_historico_dias", valor_escolhido)
            Notification.show_success(self.page, f"Retenção automática salva para {valor_escolhido} dias!")
            
        dropdown_retencao = ft.Dropdown(
            label="Período de Retenção",
            value=retencao_atual,
            on_select=alterar_retencao,
            border_color=ft.Colors.SECONDARY,
            width=350,
            options=[
                ft.dropdown.Option("0", "0 Dias (Limpar histórico ao iniciar)"),
                ft.dropdown.Option("1", "Manter por 1 dia"),
                ft.dropdown.Option("3", "Manter por 3 dias"),
                ft.dropdown.Option("7", "Manter por 7 dias"),
                ft.dropdown.Option("15", "Manter por 15 dias"),
                ft.dropdown.Option("30", "Manter por 30 dias"),
                ft.dropdown.Option("-1", "Manter para sempre (Nunca apagar)"),
            ]
        )

        # ------------------------------------------
        # LÓGICA 2: IMPORTAÇÃO E MODELOS
        # ------------------------------------------
        async def abrir_janela_arquivos(e):
            files = await ft.FilePicker().pick_files(allow_multiple=True, allowed_extensions=["json"])
            if not files: return
                
            arquivos_processados = 0
            arquivos_com_erro = []
            
            for f in files:
                try:
                    with open(f.path, 'r', encoding='utf-8') as file:
                        dados = json.load(file)
                        
                    nome_min = f.name.lower()
                    
                    if nome_min == "config.json":
                        perfil = dados.get("perfil", "")
                        if "@" in perfil:
                            usuario, dominio = perfil.split("@", 1)
                            if usuario: self.db.adicionar_usuario(usuario)
                            if dominio: self.db.adicionar_dominio(dominio)
                        elif perfil:
                            self.db.adicionar_usuario(perfil)
                        arquivos_processados += 1
                        
                    elif nome_min == "favoritos.json":
                        for i in range(1, 100):
                            if f"fav{i}" in dados and f"button_fav{i}" in dados:
                                ip, nome = dados[f"fav{i}"].strip(), dados[f"button_fav{i}"].strip()
                                if nome and ip: self.db.adicionar_favorito(nome, ip, "")
                        arquivos_processados += 1
                        
                    else:
                        nome_ambiente = os.path.splitext(f.name)[0]
                        self.db.adicionar_ambiente(nome_ambiente)
                        ambientes = self.db.listar_ambientes()
                        ambiente_id = next((a[0] for a in ambientes if a[1] == nome_ambiente), None)
                        
                        if ambiente_id:
                            for chave, valor in dados.items():
                                if chave.strip() and str(valor).strip():
                                    self.db.adicionar_conexao_ambiente(ambiente_id, chave.strip(), str(valor).strip(), "")
                            arquivos_processados += 1
                except:
                    arquivos_com_erro.append(f.name)
                    continue 

            if hasattr(self, 'atualizar_lista_usuarios'): self.atualizar_lista_usuarios()
            if hasattr(self, 'atualizar_lista_dominios'): self.atualizar_lista_dominios()

            if arquivos_processados > 0:
                msg = f"Importação concluída! {arquivos_processados} migrado(s)."
                if arquivos_com_erro: msg += f" Erro em: {', '.join(arquivos_com_erro)}"
                Notification.show_success(e.page, msg)
            elif arquivos_com_erro:
                Notification.show_error(e.page, f"Falha ao importar: {', '.join(arquivos_com_erro)}")

        async def gerar_modelos(e):
            dir_path = await ft.FilePicker().get_directory_path(dialog_title="Selecione a pasta para salvar os modelos")
            if not dir_path: return

            modelo_config = {"perfil": "usuario@dominio.com.br"}
            modelo_fav = {"fav1": "192.168.0.100", "button_fav1": "Nome de Exibição 01"}
            modelo_amb = {"SRV-APP-01": "10.0.0.50", "SRV-BD-01": "10.0.0.51"}

            try:
                with open(os.path.join(dir_path, "config.json"), "w") as f: json.dump(modelo_config, f, indent=4)
                with open(os.path.join(dir_path, "favoritos.json"), "w") as f: json.dump(modelo_fav, f, indent=4)
                with open(os.path.join(dir_path, "Modelo_Fazenda.json"), "w") as f: json.dump(modelo_amb, f, indent=4)
                Notification.show_success(e.page, "Modelos gerados com sucesso na pasta selecionada!")
            except Exception as ex:
                Notification.show_error(e.page, "Erro ao gerar os modelos de importação.")

        # ------------------------------------------
        # LÓGICA 3: BACKUP MANUAL
        # ------------------------------------------
        async def realizar_backup_manual(e):
            save_path = await ft.FilePicker().save_file(
                dialog_title="Salvar Backup do Banco de Dados",
                file_name="autordp_backup.db",
                allowed_extensions=["db"]
            )
            if not save_path: return

            try:
                shutil.copy2("autordp.db", save_path)
                Notification.show_success(e.page, "Cópia de segurança criada com sucesso!")
            except Exception as ex:
                Notification.show_error(e.page, "Não foi possível criar o backup.")

        # ------------------------------------------
        # LÓGICA DE RESTAURAÇÃO (SEGURA)
        # ------------------------------------------
        async def restaurar_backup(e):
            files = await ft.FilePicker().pick_files(
                dialog_title="Selecione o arquivo de Backup para Restaurar",
                allowed_extensions=["db"]
            )
            if not files: return
            
            backup_path = files[0].path
            
            try:
                shutil.copy2(backup_path, "autordp.db")
                
                async def fechar_aplicativo(event):
                    await event.page.window.destroy()

                dialogo_restart = ft.AlertDialog(
                    modal=True,
                    title=ft.Row([ft.Icon(ft.Icons.WARNING_AMBER, color=ft.Colors.AMBER), ft.Text("Restauração Concluída")]),
                    content=ft.Text("O banco de dados foi substituído com sucesso.\n\nPara evitar conflitos de memória e carregar os novos dados, o Remote Craft precisa ser reiniciado."),
                    actions=[
                        ft.ElevatedButton("Fechar Aplicativo Agora", on_click=fechar_aplicativo, bgcolor=ft.Colors.ERROR_CONTAINER, color=ft.Colors.ON_ERROR_CONTAINER)
                    ],
                    actions_alignment=ft.MainAxisAlignment.END
                )
                
                e.page.overlay.append(dialogo_restart)
                dialogo_restart.open = True
                e.page.update()
                
            except Exception as ex:
                print(f"Erro ao restaurar: {ex}")
                Notification.show_error(e.page, "Erro ao restaurar o banco de dados. O arquivo pode estar corrompido.")

        # ------------------------------------------
        # INTERFACE VISUAL (DIVIDIDA EM 3 CARDS)
        # ------------------------------------------
        return ft.Container(
            content=ft.ListView([
                
                # Card 1: Limpeza do histórico
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([ft.Icon(ft.Icons.CLEANING_SERVICES, color=ft.Colors.PRIMARY), ft.Text("Manutenção de Dados", size=16, weight=ft.FontWeight.BOLD)]),
                            ft.Divider(color=ft.Colors.SECONDARY),
                            ft.Text("Defina a política de limpeza automática do histórico de conexões.", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                            dropdown_retencao,
                        ]), padding=15
                    ), bgcolor=ft.Colors.SURFACE_CONTAINER
                ),

                # Card 2: Importação
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([ft.Icon(ft.Icons.DRIVE_FOLDER_UPLOAD, color=ft.Colors.PRIMARY), ft.Text("Carga de Dados e Legado", size=16, weight=ft.FontWeight.BOLD)]),
                            ft.Divider(color=ft.Colors.SECONDARY),
                            ft.Text("Importe usuários, favoritos ou cargas completas de ambientes de versões anteriores em formato JSON.", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                            ft.Row([
                                ft.ElevatedButton("Importar Arquivos", icon=ft.Icons.UPLOAD_FILE, bgcolor=ft.Colors.SECONDARY, on_click=abrir_janela_arquivos),
                                ft.ElevatedButton("Gerar Modelos", icon=ft.Icons.FILE_DOWNLOAD_OUTLINED, bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST, on_click=gerar_modelos),
                            ], spacing=15),
                        ]), padding=15
                    ), bgcolor=ft.Colors.SURFACE_CONTAINER
                ),

                # Card 3: Backup
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([ft.Icon(ft.Icons.SAVE_ALT, color=ft.Colors.PRIMARY), ft.Text("Backup do Sistema", size=16, weight=ft.FontWeight.BOLD)]),
                            ft.Divider(color=ft.Colors.SECONDARY),
                            ft.Text("Exporte uma cópia completa do seu banco de dados atual ou restaure um backup existente. A restauração reiniciará o aplicativo.", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                            
                            ft.Row([
                                ft.ElevatedButton(
                                    "Fazer Backup", 
                                    icon=ft.Icons.BACKUP, 
                                    bgcolor=ft.Colors.PRIMARY, 
                                    color=ft.Colors.ON_PRIMARY, 
                                    on_click=realizar_backup_manual
                                ),
                                ft.ElevatedButton(
                                    "Restaurar Backup", 
                                    icon=ft.Icons.RESTORE, 
                                    bgcolor=ft.Colors.ERROR_CONTAINER, 
                                    color=ft.Colors.ON_ERROR_CONTAINER, 
                                    on_click=restaurar_backup
                                ),
                            ], spacing=15),   
                        ]), padding=15
                    ), bgcolor=ft.Colors.SURFACE_CONTAINER
                )  
            ], spacing=15), padding=15
        )

    # ==========================================
    # ABA 4: PERSONALIZAÇÃO
    # ==========================================
    def _criar_aba_personalizacao(self):
        from ui.layout import AppTheme
        tema_atual = self.db.obter_tema()
        nav_recolhido_ativo = self.db.obter_configuracao("nav_rail_iniciar_recolhido", "0") == "1"
        hist_recolhido_ativo = self.db.obter_configuracao("historico_iniciar_recolhido", "0") == "1"
        
        def alterar_tema(e):
            novo_tema = e.control.value
            tema_obj, tema_modo = AppTheme.get_theme(novo_tema)
            
            self.page.theme = tema_obj
            self.page.theme_mode = tema_modo
            self.page.bgcolor = self.page.theme.color_scheme.surface_container
            self.page.update()
            self.db.salvar_tema(novo_tema)

        def salvar_tamanho(e):
            self.window_service.salvar_tamanho_atual()
            Notification.show_info(e.page, "Tamanho atual e estado da janela foram salvos com sucesso!")

        def restaurar_tamanho(e):
            self.window_service.restaurar_padrao()
            Notification.show_success(e.page, "Janela restaurada para o tamanho padrão.")

        def toggle_nav_recolhido(e):
            self.db.salvar_configuracao("nav_rail_iniciar_recolhido", "1" if e.control.value else "0")
            Notification.show_info(e.page, "Configuração do Menu Lateral salva para a próxima inicialização")

        def toggle_hist_recolhido(e):
            self.db.salvar_configuracao("historico_iniciar_recolhido", "1" if e.control.value else "0")
            Notification.show_info(e.page, "Configuração do Histórico salva para a próxima inicialização")

        switch_nav_recolhido = ft.Switch(
            label="Iniciar Menu Lateral recolhido",
            value=nav_recolhido_ativo,
            on_change=toggle_nav_recolhido,
            active_color=ft.Colors.PRIMARY
        )
        
        switch_hist_recolhido = ft.Switch(
            label="Iniciar Histórico de Conexões recolhido",
            value=hist_recolhido_ativo,
            on_change=toggle_hist_recolhido,
            active_color=ft.Colors.PRIMARY
        )

        return ft.Container(
            content=ft.ListView([
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.PALETTE, color=ft.Colors.PRIMARY),
                                ft.Text("Aparência e Estilo", size=16, weight=ft.FontWeight.BOLD)
                            ]),
                            ft.Divider(color=ft.Colors.SECONDARY),
                            ft.Text("Selecione o tema para o seu aplicativo.", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                            ft.Dropdown(
                                label="Tema do Aplicativo", 
                                value=tema_atual, 
                                on_select=alterar_tema, 
                                options=[
                                    ft.dropdown.Option("cyberpunk", "Cyberpunk"),
                                    ft.dropdown.Option("neon_tokyo", "Neon Tokyo"),
                                    ft.dropdown.Option("floresta_boreal", "Floresta Boreal"),
                                    ft.dropdown.Option("cafe_expresso", "Café Expresso"),
                                    ft.dropdown.Option("dracula_dev", "Dracula Dev"),
                                    ft.dropdown.Option("gelo_claro", "Gelo Claro"),
                                    ft.dropdown.Option("creme_de_baunilha", "Creme de Baunilha"),
                                    ft.dropdown.Option("cereja_doce", "Cereja Doce"),
                                    ft.dropdown.Option("outono_fazenda", "Outono de Fazenda"),
                                ],
                                bgcolor=ft.Colors.SURFACE,
                                border_color=ft.Colors.SECONDARY,
                                width=350,
                                menu_height=200
                            )
                        ]), padding=15
                    ), bgcolor=ft.Colors.SURFACE_CONTAINER
                ),
                
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.ASPECT_RATIO, color=ft.Colors.PRIMARY),
                                ft.Text("Dimensionamento da Janela", size=16, weight=ft.FontWeight.BOLD)
                            ]),
                            ft.Divider(color=ft.Colors.SECONDARY),
                            ft.Text("Ajuste a janela para o tamanho desejado e clique em salvar para que sempre abra nesta resolução.", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                            ft.Row([
                                ft.ElevatedButton(
                                    "Salvar Tamanho Atual",
                                    icon=ft.Icons.SAVE,
                                    bgcolor=ft.Colors.PRIMARY,
                                    color=ft.Colors.ON_SECONDARY,
                                    on_click=salvar_tamanho
                                ),
                                ft.ElevatedButton(
                                    "Restaurar Padrão",
                                    icon=ft.Icons.RESTORE,
                                    bgcolor=ft.Colors.SECONDARY,
                                    color=ft.Colors.ON_SECONDARY,
                                    on_click=restaurar_tamanho
                                )
                            ], spacing=15)
                        ]), padding=15
                    ), bgcolor=ft.Colors.SURFACE_CONTAINER
                ),

                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.VIEW_COMPACT, color=ft.Colors.PRIMARY),
                                ft.Text("Comportamento de Interface na Inicialização", size=16, weight=ft.FontWeight.BOLD)
                            ]),
                            ft.Text("Defina o estado inicial dos painéis retráteis da aplicação.", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                            ft.Divider(color=ft.Colors.SECONDARY),
                            switch_nav_recolhido,
                            switch_hist_recolhido,
                        ]), padding=15
                    ), bgcolor=ft.Colors.SURFACE_CONTAINER
                )
            ], spacing=15), padding=15
        )

    # ==========================================
    # ABA 5: AVANÇADO
    # ==========================================
    def _criar_aba_avancado(self):
        dev_mode_ativo = self.db.obter_configuracao("modo_desenvolvedor", "0") == "1"
        api_module_ativo = self.db.obter_configuracao("modulo_api_ativo", "0") == "1"

        def toggle_dev_mode(e):
            is_active = e.control.value
            self.db.salvar_configuracao("modo_desenvolvedor", "1" if is_active else "0")
            
            switch_modulo_api.disabled = not is_active
            if not is_active:
                switch_modulo_api.value = False
                self.db.salvar_configuracao("modulo_api_ativo", "0")
                
            self.update()
            if self.on_dev_mode_change:
                self.on_dev_mode_change()

        def toggle_api_module(e):
            is_active = e.control.value
            self.db.salvar_configuracao("modulo_api_ativo", "1" if is_active else "0")
            if self.on_dev_mode_change:
                self.on_dev_mode_change()

        switch_dev_mode = ft.Switch(
            label="Ativar Recursos Avançados", 
            value=dev_mode_ativo, 
            on_change=toggle_dev_mode, 
            active_color=ft.Colors.PRIMARY
        )
        
        switch_modulo_api = ft.Switch(
            label="Habilitar Módulo de API", 
            value=api_module_ativo and dev_mode_ativo, 
            disabled=not dev_mode_ativo, 
            on_change=toggle_api_module, 
            active_color=ft.Colors.SECONDARY
        )

        return ft.Container(
            content=ft.ListView([
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.WARNING, color=ft.Colors.ERROR), 
                                ft.Text("Módulos Avançados", size=16, weight=ft.FontWeight.BOLD)
                            ]),
                            ft.Text("Permite a manipulação avançada e ativação de módulos extras.", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                            ft.Divider(color=ft.Colors.SECONDARY),
                            
                            switch_dev_mode,
                            
                            ft.Container(
                                content=ft.Column([switch_modulo_api]),
                                padding=ft.Padding.only(left=20)
                            )
                        ]), padding=15
                    ), bgcolor=ft.Colors.SURFACE_CONTAINER
                )
            ], spacing=15), padding=15
        )