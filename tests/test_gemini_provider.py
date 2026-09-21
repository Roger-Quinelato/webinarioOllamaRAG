import unittest
from types import SimpleNamespace
from unittest.mock import patch

from gemini_provider import ProviderGemini
from generation_router import ErroProviderGeracao


class ProviderGeminiTest(unittest.TestCase):
    """Agrupa testes de Provider Gemini Test. Herda de unittest.TestCase."""
    def test_streaming_mapeia_system_historico_e_deltas(self):
        """Verifica que streaming mapeia system historico e deltas."""
        chamadas = []

        def gerar_stream(**kwargs):
            """Gera stream."""
            chamadas.append(kwargs)
            return iter([SimpleNamespace(text="Resposta"), SimpleNamespace(text=None)])

        client = SimpleNamespace(models=SimpleNamespace(generate_content_stream=gerar_stream))
        provider = ProviderGemini(client=client, modelo="modelo-gemini")
        mensagens = [
            {"role": "system", "content": "Use somente os trechos."},
            {"role": "assistant", "content": "Resposta anterior"},
            {"role": "user", "content": "Pergunta"},
        ]

        self.assertEqual("".join(provider.transmitir(mensagens)), "Resposta")
        self.assertEqual(chamadas[0]["model"], "modelo-gemini")
        self.assertEqual(chamadas[0]["config"], {"system_instruction": "Use somente os trechos."})
        self.assertEqual(
            chamadas[0]["contents"],
            [
                {"role": "model", "parts": [{"text": "Resposta anterior"}]},
                {"role": "user", "parts": [{"text": "Pergunta"}]},
            ],
        )
        self.assertFalse(hasattr(provider, "gerar_embeddings"))

    def test_saldo_esgotado_nao_e_retentavel(self):
        """Verifica que saldo esgotado não e retentavel."""
        class ErroHTTP(Exception):
            """Representa erro Erro HTTP. Herda de Exception."""
            status_code = 402

        client = SimpleNamespace(
            models=SimpleNamespace(
                generate_content_stream=lambda **_kwargs: (_ for _ in ()).throw(ErroHTTP())
            )
        )
        provider = ProviderGemini(client=client)

        with self.assertRaises(ErroProviderGeracao) as contexto:
            list(provider.transmitir([]))

        self.assertEqual(contexto.exception.provider, "Gemini")
        self.assertFalse(contexto.exception.retryable)

    def test_erro_do_sdk_usa_code_http_para_roteamento(self):
        """Verifica que erro do sdk usa code http para roteamento."""
        class ErroSDK(Exception):
            """Representa erro Erro SDK. Herda de Exception."""
            code = 429

        client = SimpleNamespace(
            models=SimpleNamespace(
                generate_content_stream=lambda **_kwargs: (_ for _ in ()).throw(ErroSDK())
            )
        )
        provider = ProviderGemini(client=client)

        with self.assertRaises(ErroProviderGeracao) as contexto:
            list(provider.transmitir([]))

        self.assertEqual(contexto.exception.status_code, 429)
        self.assertTrue(contexto.exception.retryable)

    def test_timeout_opcional_e_repassado_ao_sdk_em_milisegundos(self):
        """Verifica que timeout opcional e repassado ao sdk em milisegundos."""
        cliente = object()
        with patch("google.genai.Client", return_value=cliente) as criar_cliente:
            provider = ProviderGemini(
                secrets={},
                environ={"GEMINI_API_KEY": "chave", "GEMINI_TIMEOUT": "4.5"},
            )

        self.assertIs(provider._client, cliente)
        criar_cliente.assert_called_once_with(api_key="chave", http_options={"timeout": 4500})

    def test_modelo_pode_vir_de_secrets(self):
        cliente = object()
        with patch("google.genai.Client", return_value=cliente):
            provider = ProviderGemini(
                secrets={"GEMINI_API_KEY": "chave", "GEMINI_MODEL": "modelo-secrets"},
                environ={},
            )

        self.assertEqual(provider.modelo, "modelo-secrets")


if __name__ == "__main__":
    unittest.main()
