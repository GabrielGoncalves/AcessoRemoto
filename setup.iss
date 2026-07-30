[Setup]
; Configurações Gerais do Programa
AppName=RemoteDesk
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\RemoteDesk
DisableProgramGroupPage=yes
; Nome e local do arquivo final gerado (Ajustado)
OutputBaseFilename=Instalador_RemoteDesk
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
; Cria o atalho no Menu Iniciar (Ajustado para RemoteDesk.exe)
Name: "{autoprograms}\RemoteDesk"; Filename: "{app}\RemoteDesk.exe"
; Cria o atalho na Área de Trabalho (Ajustado para RemoteDesk.exe)
Name: "{autodesktop}\RemoteDesk"; Filename: "{app}\RemoteDesk.exe"; Tasks: desktopicon