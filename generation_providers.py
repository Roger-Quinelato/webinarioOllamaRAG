"""Fábrica dos providers remotos de geração configurados."""

import logging
import os

from gemini_provider import ChaveGeminiAusente, ProviderGemini
from generation_router import GenerationRouter
from nvidia_provider import ChaveNVIDIAAusente, ProviderNVIDIA
from openai_provider import ChaveOpenAIAusente, ProviderOpenAI


def _habilitar_registro():
    """Envia o log ``rag.geracao`` ao stderr em INFO, sem alterar o logging raiz nem duplicar handlers."""
    logger = logging.getLogger("rag.geracao")
    if not logger.handlers:
        manipulador = logging.StreamHandler()
        manipulador.setFormatter(logging.Formatter("%(asctime)s %(name)s %(message)s"))
        logger.addHandler(manipulador)
        logger.setLevel(logging.INFO)
        logger.propagate = False


class NenhumProviderGeracaoConfigurado(RuntimeError):
    """Nenhuma credencial de geração foi configurada. Herda de RuntimeError."""


class OrdemProvidersInvalida(ValueError):
    """``GENERATION_PROVIDERS_ORDER`` tem nome desconhecido, repetido ou vazio. Herda de ValueError."""


PROVIDERS_GERACAO = {
    "gemini": ("ProviderGemini", ChaveGeminiAusente, "GEMINI_API_KEY"),
    "nvidia": ("ProviderNVIDIA", ChaveNVIDIAAusente, "NVIDIA_API_KEY"),
    "openai": ("ProviderOpenAI", ChaveOpenAIAusente, "OPENAI_API_KEY"),
}
ORDEM_PADRAO = "nvidia,gemini,openai"


def ordem_providers(*, secrets, environ):
    """Lê ``GENERATION_PROVIDERS_ORDER`` do ambiente ou de secrets; provider omitido fica desativado."""
    environ = os.environ if environ is None else environ
    valor = environ.get("GENERATION_PROVIDERS_ORDER") or (
        secrets.get("GENERATION_PROVIDERS_ORDER") if secrets is not None else None
    ) or ORDEM_PADRAO
    nomes = [nome.strip().lower() for nome in str(valor).split(",") if nome.strip()]
    desconhecidos = [nome for nome in nomes if nome not in PROVIDERS_GERACAO]
    if not nomes or desconhecidos or len(set(nomes)) != len(nomes):
        raise OrdemProvidersInvalida(
            "GENERATION_PROVIDERS_ORDER inválida: use nomes únicos entre "
            f"{', '.join(PROVIDERS_GERACAO)}, separados por vírgula (padrão: {ORDEM_PADRAO})."
        )
    return nomes


def criar_generation_router(*, secrets, environ):
    """Cria o roteador com os providers configurados, na ordem de ``GENERATION_PROVIDERS_ORDER``."""
    _habilitar_registro()
    ordem = ordem_providers(secrets=secrets, environ=environ)
    providers = []
    for nome in ordem:
        nome_classe, erro_chave, _ = PROVIDERS_GERACAO[nome]
        try:
            providers.append(globals()[nome_classe](secrets=secrets, environ=environ))
        except erro_chave:
            continue
    if not providers:
        chaves = " ou ".join(PROVIDERS_GERACAO[nome][2] for nome in ordem)
        raise NenhumProviderGeracaoConfigurado(f"Configure {chaves} antes de consultar.")
    return GenerationRouter(providers)
