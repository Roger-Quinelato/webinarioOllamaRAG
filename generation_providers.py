"""Fábrica dos providers remotos de geração configurados."""

import logging

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


def criar_generation_router(*, secrets, environ):
    """Cria generation router."""
    _habilitar_registro()
    providers = []
    for classe, erro_chave in (
        (ProviderOpenAI, ChaveOpenAIAusente),
        (ProviderNVIDIA, ChaveNVIDIAAusente),
        (ProviderGemini, ChaveGeminiAusente),
    ):
        try:
            providers.append(classe(secrets=secrets, environ=environ))
        except erro_chave:
            continue
    if not providers:
        raise NenhumProviderGeracaoConfigurado(
            "Configure OPENAI_API_KEY, NVIDIA_API_KEY ou GEMINI_API_KEY antes de consultar."
        )
    return GenerationRouter(providers)
