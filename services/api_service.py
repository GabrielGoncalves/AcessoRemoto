import json
import urllib.request
from typing import Tuple, Any

class ApiService:
    @staticmethod
    def fetch_json(url: str, timeout: int = 10) -> Tuple[bool, Any, str]:
        """
        Realiza a requisição HTTP e tenta converter a resposta para JSON.
        Retorna uma tupla: (Sucesso_booleano, Dados_JSON_ou_None, Texto_Bruto_ou_Erro)
        """
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                data = response.read().decode('utf-8')

            try:
                # Tenta converter para JSON
                json_data = json.loads(data)
                return True, json_data, data
            except json.JSONDecodeError:
                # É uma string válida, mas não é um JSON
                return False, None, data

        except Exception as ex:
            # Falha de rede, timeout, ou erro 404/500
            return False, None, f"Erro na requisição:\n{str(ex)}"