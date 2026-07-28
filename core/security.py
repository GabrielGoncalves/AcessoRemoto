import ctypes

class CredencialSegura:
    """Envolve a senha em um buffer mutável e a destrói fisicamente da memória após o uso."""
    def __init__(self, texto: str):
        self._buffer = bytearray(texto, 'utf-8')

    def obter_bytes(self) -> bytes:
        return bytes(self._buffer)

    def destruir(self):
        if self._buffer:
            tamanho = len(self._buffer)
            endereco = (ctypes.c_char * tamanho).from_buffer(self._buffer)
            ctypes.memset(ctypes.addressof(endereco), 0, tamanho)
            self._buffer.clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.destruir()