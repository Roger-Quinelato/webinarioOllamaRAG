"""Provider Gemini para geração e streaming do RAG."""

import os

import httpx

from generation_router import ErroProviderGeracao


MODELO_GEMINI = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


class ChaveGeminiAusente(RuntimeError):
    """A aplicação não pode consultar Gemini sem chave configurada. Herda de RuntimeError."""


def obter_chave_gemini(secrets=None, environ=None):
    """Obtém chave Gemini."""
    if secrets is None:
        try:
            import streamlit as st
            from streamlit.errors import StreamlitSecretNotFoundError

            chave = st.secrets.get("GEMINI_API_KEY")
        except (FileNotFoundError, StreamlitSecretNotFoundError):
            chave = None
    else:
        chave = secrets.get("GEMINI_API_KEY")
    environ = os.environ if environ is None else environ
    chave = chave or environ.get("GEMINI_API_KEY")
    if not chave:
        raise ChaveGeminiAusente(
            "Configure GEMINI_API_KEY em st.secrets ou como variável de ambiente antes de consultar o Gemini."
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


def _status_code(erro):
    """Auxilia status code."""
    status = getattr(erro, "status_code", None)
    if status is None:
        status = getattr(erro, "code", None)
    if status is None:
        status = getattr(getattr(erro, "response", None), "status_code", None)
    return status if isinstance(status, int) else None


def _retry_after_detalhes(erro):
    """Lê ``RetryInfo.retryDelay`` (por exemplo ``"3s"``) dos detalhes do erro do SDK."""
    detalhes = getattr(erro, "details", None)
    detalhes = detalhes.get("error", detalhes) if isinstance(detalhes, dict) else None
    for item in (detalhes or {}).get("details", []) if isinstance(detalhes, dict) else []:
        atraso = item.get("retryDelay") if isinstance(item, dict) else None
        if isinstance(atraso, str) and atraso.endswith("s"):
            try:
                return max(0.0, float(atraso[:-1]))
            except ValueError:
                return None
    return None


def _retry_after(erro):
    """Auxilia retry after, lido dos cabeçalhos e, na falta deles, dos detalhes do erro."""
    cabecalhos = getattr(erro, "headers", None)
    if cabecalhos is None:
        cabecalhos = getattr(getattr(erro, "response", None), "headers", None)
    try:
        valor = cabecalhos.get("retry-after") if cabecalhos else None
        if valor is not None:
            return max(0.0, float(valor))
    except (AttributeError, TypeError, ValueError):
        pass
    return _retry_after_detalhes(erro)


def _request_id(erro):
    """Auxilia request id."""
    request_id = getattr(erro, "request_id", None) or getattr(erro, "_request_id", None)
    if request_id:
        return request_id
    cabecalhos = getattr(erro, "headers", None)
    if cabecalhos is None:
        cabecalhos = getattr(getattr(erro, "response", None), "headers", None)
    return (cabecalhos or {}).get("x-request-id") or (cabecalhos or {}).get("request-id")


def _timeout(environ):
    """Auxilia timeout."""
    valor = environ.get("GEMINI_TIMEOUT")
    return int(float(valor) * 1000) if valor else None


def _mensagem_erro(erro):
    """Auxilia mensagem erro."""
    status = _status_code(erro)
    if status in {401, 403}:
        return "Não foi possível autenticar no Gemini. Confira GEMINI_API_KEY."
    if status == 402:
        return "O saldo do Gemini está indisponível."
    if status == 429:
        return "O Gemini atingiu o limite de requisições."
    if isinstance(erro, (ConnectionError, TimeoutError, httpx.RequestError)):
        return "Não foi possível conectar ao Gemini."
    return "O Gemini não respondeu como esperado."


def _erro_seguro(erro):
    """Auxilia erro seguro."""
    return ErroProviderGeracao(
        _mensagem_erro(erro),
        provider="Gemini",
        status_code=_status_code(erro),
        retry_after=_retry_after(erro),
        request_id=_request_id(erro),
    )


def _config_geracao(sistema):
    """Monta a config sem tools e com AFC desligado, o que evita o aviso do SDK a cada chamada."""
    config = {"automatic_function_calling": {"disable": True}}
    if sistema:
        config["system_instruction"] = sistema
    return config


def _conteudo_gemini(mensagens):
    """Auxilia conteudo gemini."""
    sistema = []
    conteudos = []
    for mensagem in mensagens:
        if mensagem["role"] == "system":
            sistema.append(mensagem["content"])
            continue
        papel = "model" if mensagem["role"] == "assistant" else "user"
        conteudos.append({"role": papel, "parts": [{"text": mensagem["content"]}]})
    return conteudos, "\n\n".join(sistema)


class ProviderGemini:
    """Contrato Gemini para geração; não fornece embeddings."""

    nome = "Gemini"

    def __init__(self, *, client=None, secrets=None, environ=None, modelo=None):
        """Inicializa instância com dependências e parâmetros."""
        self.modelo = modelo or _valor_config(
            "GEMINI_MODEL", MODELO_GEMINI, secrets=secrets, environ=environ
        )
        if client is None:
            from google import genai

            environ = os.environ if environ is None else environ
            opcoes = {"api_key": obter_chave_gemini(secrets=secrets, environ=environ)}
            timeout = _timeout(environ)
            if timeout is not None:
                opcoes["http_options"] = {"timeout": timeout}
            client = genai.Client(**opcoes)
        self._client = client

    def gerar(self, mensagens):
        """Gera valor do fluxo."""
        conteudos, sistema = _conteudo_gemini(mensagens)
        try:
            resposta = self._client.models.generate_content(
                model=self.modelo,
                contents=conteudos,
                config=_config_geracao(sistema),
            )
            if not resposta.text:
                raise RuntimeError("A resposta não foi concluída.")
        except Exception as erro:
            raise _erro_seguro(erro) from None
        return resposta.text.strip()

    def transmitir(self, mensagens):
        """Transmite valor do fluxo."""
        conteudos, sistema = _conteudo_gemini(mensagens)
        try:
            eventos = self._client.models.generate_content_stream(
                model=self.modelo,
                contents=conteudos,
                config=_config_geracao(sistema),
            )
            emitiu_texto = False
            for evento in eventos:
                texto = getattr(evento, "text", None)
                if texto:
                    emitiu_texto = True
                    yield texto
            if not emitiu_texto:
                raise RuntimeError("O streaming terminou sem texto.")
        except Exception as erro:
            raise _erro_seguro(erro) from None
