"""Limite OpenAI para embeddings, geração e streaming do RAG."""

import os

import httpx


MODELO_EMBEDDING = "text-embedding-3-small"
MODELO_GERACAO = "gpt-5.6-luna"


class ChaveOpenAIAusente(RuntimeError):
    """A aplicação não pode consultar a OpenAI sem uma chave configurada."""


class ErroProviderOpenAI(RuntimeError):
    """Falha externa apresentada ao usuário sem detalhes sensíveis."""


def obter_chave_openai(secrets=None, environ=None):
    """Obtém a chave de ``st.secrets`` ou do ambiente, sem registrá-la."""
    if secrets is None:
        try:
            import streamlit as st
            from streamlit.errors import StreamlitSecretNotFoundError

            chave = st.secrets.get("OPENAI_API_KEY")
        except (FileNotFoundError, StreamlitSecretNotFoundError):
            chave = None
    else:
        chave = secrets.get("OPENAI_API_KEY")
    environ = os.environ if environ is None else environ
    chave = chave or environ.get("OPENAI_API_KEY")
    if not chave:
        raise ChaveOpenAIAusente(
            "Configure OPENAI_API_KEY em st.secrets ou como variável de ambiente antes de consultar a OpenAI."
        )
    return chave


def _mensagem_erro(erro):
    status = getattr(erro, "status_code", None)
    if status == 401:
        return "Não foi possível autenticar na OpenAI. Confira a chave OPENAI_API_KEY e tente novamente."
    if status == 429:
        return "A OpenAI atingiu o limite de requisições. Aguarde um momento e tente novamente."
    if isinstance(erro, (ConnectionError, TimeoutError, httpx.RequestError)) or type(erro).__name__ in {
        "APIConnectionError",
        "APITimeoutError",
    }:
        return "Não foi possível conectar à OpenAI. Confira a conexão e tente novamente."
    return "A OpenAI não respondeu como esperado. Tente novamente em instantes."


class ProviderOpenAI:
    """Contrato direto do SDK OpenAI, isolado do restante do pipeline RAG."""

    def __init__(self, *, client=None, secrets=None, environ=None):
        if client is None:
            chave = obter_chave_openai(secrets=secrets, environ=environ)
            from openai import OpenAI

            client = OpenAI(api_key=chave, max_retries=0)
        self._client = client

    def gerar_embeddings(self, textos):
        try:
            resposta = self._client.embeddings.create(model=MODELO_EMBEDDING, input=textos)
        except Exception as erro:
            raise ErroProviderOpenAI(_mensagem_erro(erro)) from None
        return [item.embedding for item in resposta.data]

    def gerar(self, mensagens):
        try:
            resposta = self._client.responses.create(model=MODELO_GERACAO, input=mensagens)
            if resposta.status != "completed":
                raise RuntimeError("A resposta não foi concluída.")
        except Exception as erro:
            raise ErroProviderOpenAI(_mensagem_erro(erro)) from None
        return resposta.output_text.strip()

    def transmitir(self, mensagens):
        try:
            eventos = self._client.responses.create(model=MODELO_GERACAO, input=mensagens, stream=True)
            concluida = False
            for evento in eventos:
                if evento.type == "response.output_text.delta":
                    yield evento.delta
                elif evento.type == "response.completed":
                    concluida = True
                elif evento.type in {"error", "response.failed", "response.incomplete"}:
                    raise RuntimeError("A resposta em streaming falhou.")
            if not concluida:
                raise RuntimeError("O streaming terminou sem conclusão.")
        except Exception as erro:
            raise ErroProviderOpenAI(_mensagem_erro(erro)) from None
