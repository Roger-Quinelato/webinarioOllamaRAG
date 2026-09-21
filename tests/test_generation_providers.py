import unittest
from unittest.mock import patch

from generation_providers import (
    NenhumProviderGeracaoConfigurado,
    OrdemProvidersInvalida,
    criar_generation_router,
)
from nvidia_provider import ChaveNVIDIAAusente
from openai_provider import ChaveOpenAIAusente
from gemini_provider import ChaveGeminiAusente


class GenerationProvidersTest(unittest.TestCase):
    """Agrupa testes de Generation Providers Test. Herda de unittest.TestCase."""
    @patch("generation_providers.ProviderGemini", side_effect=ChaveGeminiAusente("sem Gemini"))
    @patch("generation_providers.ProviderNVIDIA")
    @patch("generation_providers.ProviderOpenAI", side_effect=ChaveOpenAIAusente("sem OpenAI"))
    def test_nvidia_configurada_permite_iniciar_sem_openai(self, _openai, nvidia, _gemini):
        """Verifica que NVIDIA configurada permite iniciar sem OpenAI."""
        nvidia.return_value.nome = "NVIDIA"

        router = criar_generation_router(secrets={"NVIDIA_API_KEY": "chave"}, environ={})

        self.assertEqual([provider.nome for provider in router._providers], ["NVIDIA"])
        nvidia.assert_called_once_with(secrets={"NVIDIA_API_KEY": "chave"}, environ={})

    @patch("generation_providers.ProviderGemini", side_effect=ChaveGeminiAusente("sem Gemini"))
    @patch("generation_providers.ProviderNVIDIA", side_effect=ChaveNVIDIAAusente("sem NVIDIA"))
    @patch("generation_providers.ProviderOpenAI", side_effect=ChaveOpenAIAusente("sem OpenAI"))
    def test_sem_credencial_expoe_configuracao_acionavel(self, _openai, _nvidia, _gemini):
        """Verifica que sem credencial expõe configuração acionavel."""
        with self.assertRaisesRegex(NenhumProviderGeracaoConfigurado, "OPENAI_API_KEY"):
            criar_generation_router(secrets={}, environ={})

    def _todos_configurados(self, openai, nvidia, gemini):
        openai.return_value.nome = "OpenAI"
        nvidia.return_value.nome = "NVIDIA"
        gemini.return_value.nome = "Gemini"

    @patch("generation_providers.ProviderGemini")
    @patch("generation_providers.ProviderNVIDIA")
    @patch("generation_providers.ProviderOpenAI")
    def test_ordem_padrao_e_gemini_nvidia_openai(self, openai, nvidia, gemini):
        """Verifica a ordem padrão Gemini, NVIDIA e OpenAI (FIN-03)."""
        self._todos_configurados(openai, nvidia, gemini)

        router = criar_generation_router(secrets={}, environ={})

        self.assertEqual([p.nome for p in router._providers], ["Gemini", "NVIDIA", "OpenAI"])

    @patch("generation_providers.ProviderGemini")
    @patch("generation_providers.ProviderNVIDIA")
    @patch("generation_providers.ProviderOpenAI")
    def test_ordem_configuravel_por_ambiente(self, openai, nvidia, gemini):
        """Verifica que GENERATION_PROVIDERS_ORDER no ambiente define a ordem."""
        self._todos_configurados(openai, nvidia, gemini)

        router = criar_generation_router(
            secrets={}, environ={"GENERATION_PROVIDERS_ORDER": " NVIDIA , gemini,openai "}
        )

        self.assertEqual([p.nome for p in router._providers], ["NVIDIA", "Gemini", "OpenAI"])

    @patch("generation_providers.ProviderGemini")
    @patch("generation_providers.ProviderNVIDIA")
    @patch("generation_providers.ProviderOpenAI")
    def test_ordem_por_secrets_e_subconjunto_desativa_ausentes(self, openai, nvidia, gemini):
        """Verifica que secrets define a ordem e que provider omitido não é instanciado."""
        self._todos_configurados(openai, nvidia, gemini)

        router = criar_generation_router(
            secrets={"GENERATION_PROVIDERS_ORDER": "nvidia,gemini"}, environ={}
        )

        self.assertEqual([p.nome for p in router._providers], ["NVIDIA", "Gemini"])
        openai.assert_not_called()

    def test_ordem_invalida_ou_repetida_e_recusada(self):
        """Verifica que nome desconhecido, repetido ou lista vazia gera erro acionável."""
        for valor in ("gemini,claude", "gemini,gemini", " , "):
            with self.subTest(valor=valor):
                with self.assertRaisesRegex(OrdemProvidersInvalida, "GENERATION_PROVIDERS_ORDER"):
                    criar_generation_router(
                        secrets={}, environ={"GENERATION_PROVIDERS_ORDER": valor}
                    )


if __name__ == "__main__":
    unittest.main()
