import unittest
from unittest.mock import patch

from generation_providers import NenhumProviderGeracaoConfigurado, criar_generation_router
from nvidia_provider import ChaveNVIDIAAusente
from openai_provider import ChaveOpenAIAusente
from gemini_provider import ChaveGeminiAusente


class GenerationProvidersTest(unittest.TestCase):
    @patch("generation_providers.ProviderGemini", side_effect=ChaveGeminiAusente("sem Gemini"))
    @patch("generation_providers.ProviderNVIDIA")
    @patch("generation_providers.ProviderOpenAI", side_effect=ChaveOpenAIAusente("sem OpenAI"))
    def test_nvidia_configurada_permite_iniciar_sem_openai(self, _openai, nvidia, _gemini):
        nvidia.return_value.nome = "NVIDIA"

        router = criar_generation_router(secrets={"NVIDIA_API_KEY": "chave"}, environ={})

        self.assertEqual([provider.nome for provider in router._providers], ["NVIDIA"])
        nvidia.assert_called_once_with(secrets={"NVIDIA_API_KEY": "chave"}, environ={})

    @patch("generation_providers.ProviderGemini", side_effect=ChaveGeminiAusente("sem Gemini"))
    @patch("generation_providers.ProviderNVIDIA", side_effect=ChaveNVIDIAAusente("sem NVIDIA"))
    @patch("generation_providers.ProviderOpenAI", side_effect=ChaveOpenAIAusente("sem OpenAI"))
    def test_sem_credencial_expoe_configuracao_acionavel(self, _openai, _nvidia, _gemini):
        with self.assertRaisesRegex(NenhumProviderGeracaoConfigurado, "OPENAI_API_KEY"):
            criar_generation_router(secrets={}, environ={})


if __name__ == "__main__":
    unittest.main()
