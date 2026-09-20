"""Provider de embeddings locais ``bge-m3`` via Ollama."""

import config
import httpx


MODELO_EMBEDDING = "bge-m3"


class ErroProviderEmbeddingsOllama(RuntimeError):
    """Falha externa de embeddings apresentada sem detalhes internos."""


class ProviderEmbeddingsOllama:
    """Adapter mínimo entre o RAG e a fronteira externa do Ollama."""

    def __init__(self, *, client=None):
        if client is None:
            from ollama import Client

            client = Client(host=config.OLLAMA_HOST)
        self._client = client

    def gerar_embeddings(self, textos):
        try:
            resposta = self._client.embed(model=MODELO_EMBEDDING, input=textos)
        except Exception as erro:
            if getattr(erro, "status_code", None) == 404:
                mensagem = (
                    "O modelo bge-m3 não está instalado. "
                    "Execute `ollama pull bge-m3` e tente novamente."
                )
            elif isinstance(erro, (ConnectionError, TimeoutError, httpx.RequestError)):
                mensagem = "Não foi possível conectar ao Ollama. Inicie o Ollama e tente novamente."
            else:
                mensagem = "O Ollama não gerou os embeddings. Confira o serviço e tente novamente."
            raise ErroProviderEmbeddingsOllama(mensagem) from None
        return resposta.embeddings
