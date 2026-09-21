"""Limite OpenAI para geração e streaming do RAG."""

import os

import httpx

from generation_router import ErroProviderGeracao

MODELO_GERACAO = os.getenv("OPENAI_GENERATION_MODEL", "gpt-5.6-luna")


class ChaveOpenAIAusente(RuntimeError):
    """A aplicação não pode consultar a OpenAI sem uma chave configurada. Herda de RuntimeError."""


class ErroProviderOpenAI(ErroProviderGeracao):
    """Falha externa apresentada ao usuário sem detalhes sensíveis. Herda de ErroProviderGeracao."""

    def __init__(self, mensagem, *, status_code=None, retry_after=None, request_id=None):
        """Inicializa instância com dependências e parâmetros."""
        super().__init__(
            mensagem,
            provider="OpenAI",
            status_code=status_code,
            retry_after=retry_after,
            request_id=request_id,
        )


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


def _valor_config(nome, padrao, *, secrets=None, environ=None):
    """Auxilia valor de configuração, lendo primeiro do ambiente e depois de secrets."""
    environ = os.environ if environ is None else environ
    valor = environ.get(nome)
    if valor:
        return valor
    if secrets is not None:
        return secrets.get(nome, padrao)
    return padrao


def _timeout(*, secrets=None, environ=None):
    """Lê ``OPENAI_TIMEOUT`` em segundos, do ambiente ou de secrets; ausente mantém o padrão do SDK."""
    valor = _valor_config("OPENAI_TIMEOUT", None, secrets=secrets, environ=environ)
    return float(valor) if valor else None


_CODIGOS_STATUS = {
    "credit_balance_exhausted": 429,
    "insufficient_quota": 429,
    "rate_limit_exceeded": 429,
    "invalid_api_key": 401,
}
_CODIGOS_SEM_SALDO = {"credit_balance_exhausted", "insufficient_quota"}


class _ErroEventoStream(Exception):
    """Evento de erro do stream, reduzido a código e status; nunca guarda mensagem ou corpo."""

    def __init__(self, codigo=None, status_code=None):
        """Inicializa instância com dependências e parâmetros."""
        super().__init__("evento de erro no streaming")
        self.code = codigo
        self.status_code = status_code


def _codigo_erro(erro):
    """Auxilia código do erro, lido do atributo ou do corpo estruturado."""
    codigo = getattr(erro, "code", None)
    if not isinstance(codigo, str):
        corpo = getattr(erro, "body", None)
        corpo = corpo.get("error", corpo) if isinstance(corpo, dict) else None
        codigo = corpo.get("code") if isinstance(corpo, dict) else None
    return codigo if isinstance(codigo, str) else None


def _status_code(erro):
    """Deriva o status HTTP do erro, da resposta ou do código do erro, nessa ordem."""
    status = getattr(erro, "status_code", None)
    if status is None:
        status = getattr(getattr(erro, "response", None), "status_code", None)
    if status is None:
        status = _CODIGOS_STATUS.get(_codigo_erro(erro))
    return status if isinstance(status, int) else None


def _mensagem_erro(erro):
    """Auxilia mensagem erro."""
    status = _status_code(erro)
    if status == 401:
        return "Não foi possível autenticar na OpenAI. Confira a chave OPENAI_API_KEY."
    if status == 429 and _codigo_erro(erro) in _CODIGOS_SEM_SALDO:
        return "A conta OpenAI está sem saldo ou cota. Verifique o faturamento."
    if status == 429:
        return "A OpenAI atingiu o limite de requisições."
    if isinstance(erro, (ConnectionError, TimeoutError, httpx.RequestError)) or type(erro).__name__ in {
        "APIConnectionError",
        "APITimeoutError",
    }:
        return "Não foi possível conectar à OpenAI. Confira a conexão."
    return "A OpenAI não respondeu como esperado."


def _retry_after(erro):
    """Auxilia retry after."""
    cabecalhos = getattr(erro, "headers", None)
    if cabecalhos is None:
        cabecalhos = getattr(getattr(erro, "response", None), "headers", None)
    if not cabecalhos:
        return None
    try:
        valor = cabecalhos.get("retry-after")
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


def _erro_do_evento(evento):
    """Reduz um evento de erro do stream ao código e ao status, sem carregar a mensagem."""
    origem = getattr(getattr(evento, "response", None), "error", None) or evento
    codigo = getattr(origem, "code", None)
    return _ErroEventoStream(
        codigo if isinstance(codigo, str) else None,
        getattr(evento, "status_code", None),
    )


def _erro_seguro(erro):
    """Auxilia erro seguro."""
    return ErroProviderOpenAI(
        _mensagem_erro(erro),
        status_code=_status_code(erro),
        retry_after=_retry_after(erro),
        request_id=_request_id(erro),
    )


class ProviderOpenAI:
    """Contrato de geração do SDK OpenAI, isolado do restante do pipeline RAG."""

    nome = "OpenAI"

    def __init__(self, *, client=None, secrets=None, environ=None):
        """Inicializa instância com dependências e parâmetros."""
        self.modelo = _valor_config(
            "OPENAI_GENERATION_MODEL", MODELO_GERACAO, secrets=secrets, environ=environ
        )
        if client is None:
            chave = obter_chave_openai(secrets=secrets, environ=environ)
            from openai import OpenAI

            opcoes = {"api_key": chave, "max_retries": 0}
            timeout = _timeout(secrets=secrets, environ=environ)
            if timeout is not None:
                opcoes["timeout"] = timeout
            client = OpenAI(**opcoes)
        self._client = client

    def gerar(self, mensagens):
        """Gera valor do fluxo."""
        try:
            resposta = self._client.responses.create(model=self.modelo, input=mensagens)
            if resposta.status != "completed":
                raise RuntimeError("A resposta não foi concluída.")
        except Exception as erro:
            raise _erro_seguro(erro) from None
        return resposta.output_text.strip()

    def transmitir(self, mensagens):
        """Transmite valor do fluxo."""
        try:
            eventos = self._client.responses.create(model=self.modelo, input=mensagens, stream=True)
            concluida = False
            for evento in eventos:
                if evento.type == "response.output_text.delta":
                    yield evento.delta
                elif evento.type == "response.completed":
                    concluida = True
                elif evento.type in {"error", "response.failed", "response.incomplete"}:
                    raise _erro_do_evento(evento)
            if not concluida:
                raise RuntimeError("O streaming terminou sem conclusão.")
        except Exception as erro:
            raise _erro_seguro(erro) from None
