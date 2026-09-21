"""Provider NVIDIA API Catalog para geração e streaming do RAG."""

import os

import httpx

from generation_router import ErroProviderGeracao


MODELO_NVIDIA = os.getenv("NVIDIA_MODEL", "meta/llama-3.1-8b-instruct")
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")


class ChaveNVIDIAAusente(RuntimeError):
    """A aplicação não pode consultar NVIDIA sem chave configurada."""


def obter_chave_nvidia(secrets=None, environ=None):
    if secrets is None:
        try:
            import streamlit as st
            from streamlit.errors import StreamlitSecretNotFoundError

            chave = st.secrets.get("NVIDIA_API_KEY")
        except (FileNotFoundError, StreamlitSecretNotFoundError):
            chave = None
    else:
        chave = secrets.get("NVIDIA_API_KEY")
    environ = os.environ if environ is None else environ
    chave = chave or environ.get("NVIDIA_API_KEY")
    if not chave:
        raise ChaveNVIDIAAusente(
            "Configure NVIDIA_API_KEY em st.secrets ou como variável de ambiente antes de consultar a NVIDIA."
        )
    return chave


def _valor_config(nome, padrao, *, secrets=None, environ=None):
    environ = os.environ if environ is None else environ
    valor = environ.get(nome)
    if valor:
        return valor
    if secrets is not None:
        return secrets.get(nome, padrao)
    return padrao


def _retry_after(erro):
    cabecalhos = getattr(erro, "headers", None)
    if cabecalhos is None:
        cabecalhos = getattr(getattr(erro, "response", None), "headers", None)
    try:
        valor = cabecalhos.get("retry-after") if cabecalhos else None
        return max(0.0, float(valor)) if valor is not None else None
    except (AttributeError, TypeError, ValueError):
        return None


def _request_id(erro):
    request_id = getattr(erro, "request_id", None) or getattr(erro, "_request_id", None)
    if request_id:
        return request_id
    cabecalhos = getattr(erro, "headers", None)
    if cabecalhos is None:
        cabecalhos = getattr(getattr(erro, "response", None), "headers", None)
    return (cabecalhos or {}).get("x-request-id") or (cabecalhos or {}).get("request-id")


def _timeout(environ):
    valor = environ.get("NVIDIA_TIMEOUT")
    return float(valor) if valor else None


def _mensagem_erro(erro):
    status = getattr(erro, "status_code", None)
    if status in {401, 403}:
        return "Não foi possível autenticar na NVIDIA. Confira NVIDIA_API_KEY e tente novamente."
    if status == 429:
        return "A NVIDIA atingiu o limite de requisições. Tentando outro provider de geração."
    if isinstance(erro, (ConnectionError, TimeoutError, httpx.RequestError)):
        return "Não foi possível conectar à NVIDIA. Tentando outro provider de geração."
    return "A NVIDIA não respondeu como esperado. Tentando outro provider de geração."


def _erro_seguro(erro):
    return ErroProviderGeracao(
        _mensagem_erro(erro),
        provider="NVIDIA",
        status_code=getattr(erro, "status_code", None),
        retry_after=_retry_after(erro),
        request_id=_request_id(erro),
    )


class ProviderNVIDIA:
    """Contrato NVIDIA para geração; não fornece embeddings."""

    nome = "NVIDIA"

    def __init__(self, *, client=None, secrets=None, environ=None, modelo=None, base_url=None):
        self.modelo = modelo or _valor_config(
            "NVIDIA_MODEL", MODELO_NVIDIA, secrets=secrets, environ=environ
        )
        if client is None:
            from openai import OpenAI

            environ = os.environ if environ is None else environ
            opcoes = {
                "api_key": obter_chave_nvidia(secrets=secrets, environ=environ),
                "base_url": base_url
                or _valor_config(
                    "NVIDIA_BASE_URL", NVIDIA_BASE_URL, secrets=secrets, environ=environ
                ),
                "max_retries": 0,
            }
            timeout = _timeout(environ)
            if timeout is not None:
                opcoes["timeout"] = timeout
            client = OpenAI(**opcoes)
        self._client = client

    def gerar(self, mensagens):
        try:
            resposta = self._client.chat.completions.create(model=self.modelo, messages=mensagens)
            texto = resposta.choices[0].message.content
            if not texto:
                raise RuntimeError("A resposta não foi concluída.")
        except Exception as erro:
            raise _erro_seguro(erro) from None
        return texto.strip()

    def transmitir(self, mensagens):
        try:
            eventos = self._client.chat.completions.create(
                model=self.modelo, messages=mensagens, stream=True
            )
            concluida = False
            for evento in eventos:
                escolha = evento.choices[0]
                texto = getattr(escolha.delta, "content", None)
                if texto:
                    yield texto
                if escolha.finish_reason:
                    concluida = True
            if not concluida:
                raise RuntimeError("O streaming terminou sem conclusão.")
        except Exception as erro:
            raise _erro_seguro(erro) from None
