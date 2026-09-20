"""Fábrica dos providers remotos de geração configurados."""

from gemini_provider import ChaveGeminiAusente, ProviderGemini
from generation_router import GenerationRouter
from nvidia_provider import ChaveNVIDIAAusente, ProviderNVIDIA
from openai_provider import ChaveOpenAIAusente, ProviderOpenAI


class NenhumProviderGeracaoConfigurado(RuntimeError):
    """Nenhuma credencial de geração foi configurada."""


def criar_generation_router(*, secrets, environ):
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
