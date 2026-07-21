[Setup]
; Configurações Gerais do Programa
AppName=Remote Craft
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\Remote Craft
DisableProgramGroupPage=yes
; Nome e local do arquivo final gerado
OutputBaseFilename=Instalador_RemoteCraft
OutputDir=build\windows_installer
; Melhor compressão possível
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern

[Tasks]
; Cria a caixinha "Criar atalho na Área de Trabalho" já marcada por padrão
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
; Pega todos os arquivos soltos gerados pelo Flet e joga na pasta de instalação do usuário
Source: "build\windows\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Cria o atalho no Menu Iniciar
Name: "{autoprograms}\Remote Craft"; Filename: "{app}\AcessoRemoto.exe"
; Cria o atalho na Área de Trabalho (vinculado à caixinha da seção Tasks)
Name: "{autodesktop}\Remote Craft"; Filename: "{app}\AcessoRemoto.exe"; Tasks: desktopicon