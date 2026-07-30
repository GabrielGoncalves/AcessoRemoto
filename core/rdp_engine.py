import os
import platform
import subprocess
import threading
import time
import sys
from pathlib import Path
from core.security import CredencialSegura

class RDPAngine:
    @staticmethod
    def _obter_caminho_wfreerdp() -> str:
        """Resolve o caminho absoluto do sdl-freerdp.exe, seja rodando local ou compilado"""
        if getattr(sys, 'frozen', False):
            base_path = Path(sys._MEIPASS)
        else:
            base_path = Path(__file__).parent.parent
        return str(base_path / "assets" / "sdl-freerdp.exe")

    @staticmethod
    def obter_caminho_salvamento() -> Path:
        """Retorna a pasta de cache ideal dependendo do Sistema Operacional (usado por Mac)"""
        home = Path.home()
        if platform.system() == "Windows":
            diretorio = home / "AppData" / "Local" / "RemoteDesk"
        else:
            diretorio = home / "Library" / "Application Support" / "RemoteDesk"
            
        diretorio.mkdir(parents=True, exist_ok=True)
        return diretorio / "launcher.rdp"

    @staticmethod
    def executar(ip, user, senha):
        sistema = platform.system()
        
        # ==========================================
        # ENGINE WINDOWS COM FREE RDP
        # ==========================================
        if sistema == "Windows":
            caminho_binario = RDPAngine._obter_caminho_wfreerdp()
            
            comando = [
                caminho_binario,
                f"/v:{ip}",
                f"/u:{user}",
                f'{ip}',
                "/size:85%",           
                "/from-stdin",         
                "/dynamic-resolution", 
                "/cert:ignore",        
                "+clipboard"           
            ]

            CREATE_NO_WINDOW = 0x08000000
            
            processo = subprocess.Popen(
                comando,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=CREATE_NO_WINDOW
            )
            if senha:
                with CredencialSegura(senha) as cred:
                    processo.stdin.write(cred.obter_bytes() + b"\n")
                    processo.stdin.flush()      
            if processo.stdin:
                processo.stdin.close()

        # ==========================================
        # ENGINE MACOS
        # ==========================================
        elif sistema == "Darwin":
            arquivo_rdp = RDPAngine.obter_caminho_salvamento()
            conteudo_rdp = (
                f"full address:s:{ip}\n"
                f"username:s:{user}\n"
                f"screen mode id:i:2\n"        
                f"prompt for credentials:i:1\n"
            )

            with open(arquivo_rdp, "w", encoding="utf-8") as f:
                f.write(conteudo_rdp)

            if senha:
                subprocess.run(["pbcopy"], text=True, input=senha)
            subprocess.Popen(["open", str(arquivo_rdp)])
            threading.Thread(target=RDPAngine._limpar_arquivo_temporario, args=(arquivo_rdp,), daemon=True).start()

        # ==========================================
        # ENGINE LINUX
        # ==========================================
        else: 
            comando = [
                "xfreerdp",
                f"/v:{ip}",
                f"/u:{user}",
                f"/t:Remote Craft - Conectado em {ip}",
                "/size:1280x720",
                "/from-stdin",
                "/dynamic-resolution",
                "/cert:ignore",
                "+clipboard"
            ]
            processo = subprocess.Popen(
                comando,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            if senha:
                with CredencialSegura(senha) as cred:
                    processo.stdin.write(cred.obter_bytes() + b"\n")
                    processo.stdin.flush()
            
            if processo.stdin:
                processo.stdin.close()

    @staticmethod
    def _limpar_arquivo_temporario(caminho_arquivo: Path):
        """Deleta o arquivo RDP 5 segundos após a execução para não deixar rastros no Mac/Linux"""
        time.sleep(5)
        if caminho_arquivo.exists():
            caminho_arquivo.unlink()