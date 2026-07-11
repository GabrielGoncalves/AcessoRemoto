import os
import platform
import subprocess
import ctypes
import threading
import time
import ctypes.wintypes
from pathlib import Path

class RDPAngine:
    @staticmethod
    def obter_caminho_salvamento() -> Path:
        """Retorna a pasta de cache ideal dependendo do Sistema Operacional"""
        home = Path.home()
        if platform.system() == "Windows":
            diretorio = home / "AppData" / "Local" / "RemoteCraft"
        else:
            diretorio = home / "Library" / "Application Support" / "RemoteCraft"
            
        diretorio.mkdir(parents=True, exist_ok=True)
        return diretorio / "launcher.rdp"

    @staticmethod
    def _criptografar_senha_dpapi(senha: str) -> str:
        """Criptografa a senha nativamente usando a API DPAPI do Windows"""
        if not senha:
            return ""
        pwd_bytes = (senha + '\0').encode('utf-16le')

        class DATA_BLOB(ctypes.Structure):
            _fields_ = [("cbData", ctypes.wintypes.DWORD),
                        ("pbData", ctypes.POINTER(ctypes.c_byte))]

        data_in = DATA_BLOB(len(pwd_bytes), ctypes.cast(pwd_bytes, ctypes.POINTER(ctypes.c_byte)))
        data_out = DATA_BLOB()

        ret = ctypes.windll.crypt32.CryptProtectData(
            ctypes.byref(data_in),
            None, None, None, None, 0x01,
            ctypes.byref(data_out)
        )

        if not ret:
            return ""

        out_bytes = ctypes.string_at(data_out.pbData, data_out.cbData)
        ctypes.windll.kernel32.LocalFree(data_out.pbData)
        return out_bytes.hex().upper()

    @staticmethod
    def executar(ip, user, senha):
        sistema = platform.system()
        arquivo_rdp = RDPAngine.obter_caminho_salvamento()

        if sistema == "Windows":
            conteudo_rdp = (
                f"full address:s:{ip}\n"
                f"username:s:{user}\n"
                f"prompt for credentials:i:0\n"
                f"authentication level:i:2\n"
            )      
            if senha:
                hash_dpapi = RDPAngine._criptografar_senha_dpapi(senha)
                if hash_dpapi:
                    conteudo_rdp += f"password 51:b:{hash_dpapi}\n"

            with open(arquivo_rdp, "w", encoding="utf-8") as f:
                f.write(conteudo_rdp)
            subprocess.Popen(["mstsc", str(arquivo_rdp)])
            threading.Thread(target=RDPAngine._limpar_arquivo_temporario, args=(arquivo_rdp,), daemon=True).start()

        elif sistema == "Darwin":
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

        else: # Linux
            env_seguro = os.environ.copy()
            env_seguro["XFREERDP_PASSWORD"] = senha
            subprocess.Popen(
                ["xfreerdp", f"/v:{ip}", f"/u:{user}", "/cert:ignore", "/f"],
                env=env_seguro
            )

    @staticmethod
    def _limpar_arquivo_temporario(caminho_arquivo: Path):
        """Deleta o arquivo RDP 5 segundos após a execução para não deixar rastros"""
        time.sleep(5)
        #try:
        if caminho_arquivo.exists():
                caminho_arquivo.unlink() # Comando Pathlib para deletar arquivo
        #except Exception:
        #    pass