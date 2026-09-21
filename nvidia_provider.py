"""Provider NVIDIA API Catalog para geração e streaming do RAG."""

import logging
import os

import httpx

from generation_router import ErroProviderGeracao


LOGGER = logging.getLogger("rag.geracao")
TIMEOUT_PADRAO = 30.0
MODELO_NVIDIA = os.getenv("NVIDIA_MODEL", "meta/llama-3.2-11b-vision-instruct")
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")


class ChaveNVIDIAAusente(RuntimeError):
    """A aplicação não pode consultar NVIDIA sem chave configurada. Herda de RuntimeError."""


def obter_chave_nvidia(secrets=None, environ=None):
    """Obtém chave NVIDIA."""
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
    """Auxilia valor de configuração, lendo primeiro do ambiente e depois de secrets."""
    environ = os.environ if environ is None else environ
    valor = environ.get(nome)
    if valor:
        return valor
    if secrets is not None:
        return secrets.get(nome, padrao)
    return padrao


def _retry_after(erro):
    """Auxilia retry after."""
    cabecalhos = getattr(erro, "headers", None)
    if cabecalhos is None:
        cabecalhos = getattr(getattr(erro, "response", None), "headers", None)
    try:
        valor = cabecalhos.get("retry-after") if cabecalhos else None
        return max(0.0, float(valor)) if valor is not None else None
    except (AttributeError, TypeError, ValueError):
        return None


def _request_id(erro):
    """Auxilia request id."""
    request_id = getattr(erro, "request_id", None) or getattr(erro, "_request_id", None)
    if request_id:
        return request_id
    cabecalhos = getattr(erro, "headers", None)
    if cabecalhos is None:
        cabecalhos = getattr(getattr(erro, "response", None), "headers", None)
    return (cabecalhos or {}).get("x-request-id") or (cabecalhos or {}).get("request-id")


def _timeout(*, secrets=None, environ=None):
    """Lê ``NVIDIA_TIMEOUT`` em segundos; sem valor, usa ``TIMEOUT_PADRAO`` para não esperar 90 s."""
    valor = _valor_config("NVIDIA_TIMEOUT", None, secrets=secrets, environ=environ)
    return float(valor) if valor else TIMEOUT_PADRAO


def _status_code(erro):
    """Deriva o status HTTP do erro ou da resposta associada."""
    status = getattr(erro, "status_code", None)
    if status is None:
        status = getattr(getattr(erro, "response", None), "status_code", None)
    return status if isinstance(status, int) else None


def _mensagem_erro(erro):
    """Auxilia mensagem erro."""
    status = _status_code(erro)
    if status in {401, 403}:
        return "Não foi possível autenticar na NVIDIA. Confira NVIDIA_API_KEY."
    if status == 429:
        return "A NVIDIA atingiu o limite de requisições."
    if isinstance(erro, (ConnectionError, TimeoutError, httpx.RequestError)) or type(erro).__name__ in {
        "APIConnectionError",
        "APITimeoutError",
    }:
        return "Não foi possível conectar à NVIDIA."
    return "A NVIDIA não respondeu como esperado."


def _erro_seguro(erro):
    """Auxilia erro seguro."""
    return ErroProviderGeracao(
        _mensagem_erro(erro),
        provider="NVIDIA",
        status_code=_status_code(erro),
        retry_after=_retry_after(erro),
        request_id=_request_id(erro),
    )


class ProviderNVIDIA:
    """Contrato NVIDIA para geração; não fornece embeddings."""

    nome = "NVIDIA"

    def __init__(self, *, client=None, secrets=None, environ=None, modelo=None, base_url=None):
        """Inicializa instância com dependências e parâmetros."""
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
            opcoes["timeout"] = _timeout(secrets=secrets, environ=environ)
            client = OpenAI(**opcoes)
        self._client = client

    def gerar(self, mensagens):
        """Gera valor do fluxo."""
        try:
            resposta = self._client.chat.completions.create(model=self.modelo, messages=mensagens)
            texto = resposta.choices[0].message.content
            if not texto:
                raise RuntimeError("A resposta não foi concluída.")
        except Exception as erro:
            raise _erro_seguro(erro) from None
        return texto.strip()

    def transmitir(self, mensagens):
        """Transmite valor do fluxo."""
        try:
            eventos = self._client.chat.completions.create(
                model=self.modelo, messages=mensagens, stream=True
            )
            concluida = False
            eventos_recebidos = 0
            try:
                for evento in eventos:
                    eventos_recebidos += 1
                    if not evento.choices:
                        continue
                    escolha = evento.choices[0]
                    texto = getattr(escolha.delta, "content", None)
                    if texto:
                        yield texto
                    if escolha.finish_reason:
                        concluida = True
            finally:
                LOGGER.info(
                    "nvidia_stream modelo=%s eventos=%s finish_reason=%s",
                    self.modelo, eventos_recebidos, concluida,
                )
            if not concluida:
                raise RuntimeError("O streaming terminou sem conclusão.")
        except Exception as erro:
            raise _erro_seguro(erro) from None
