import os
import sys
import platform
import subprocess
from pathlib import Path

class RDPAngine:
    @staticmethod
    def obter_caminho_salvamento() -> Path:
        """Retorna a pasta de cache ideal para o arquivo temporário do Mac"""
        home = Path.home()
        diretorio = home / "Library" / "Application Support" / "RemoteCraft"
        diretorio.mkdir(parents=True, exist_ok=True)
        return diretorio / "launcher.rdp"

    @staticmethod
    def obter_binario_windows() -> Path:
        """Localiza o FreeRDP portátil embutido na pasta do projeto no Windows"""
        if getattr(sys, 'frozen', False):
            base_path = Path(sys._MEIPASS)
        else:
            base_path = Path(__file__).resolve().parent.parent
        return base_path / "bin" / "windows" / "wfreerdp.exe"

    @staticmethod
    def executar(ip, user, senha):
        sistema = platform.system()

        if sistema == "Windows":
            binario_win = RDPAngine.obter_binario_windows()
            
            env_seguro = os.environ.copy()
            env_seguro["XFREERDP_PASSWORD"] = senha
            subprocess.Popen(
                [str(binario_win), f"/v:{ip}", f"/u:{user}", "/cert:ignore", "+clipboard", "/f"],
                env=env_seguro
            )

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
                subprocess.run("pbcopy", text=True, input=senha)

            subprocess.Popen(["open", str(arquivo_rdp)])

        else:
            env_seguro = os.environ.copy()
            env_seguro["XFREERDP_PASSWORD"] = senha
            subprocess.Popen(
                ["xfreerdp", f"/v:{ip}", f"/u:{user}", "/cert:ignore", "/f"],
                env=env_seguro
            )