import unittest
from types import SimpleNamespace
from unittest.mock import patch

from generation_router import ErroProviderGeracao
from nvidia_provider import ProviderNVIDIA


class ProviderNVIDIATest(unittest.TestCase):
    def test_streaming_converte_chat_completions_em_deltas(self):
        def criar(**kwargs):
            self.assertEqual(kwargs["model"], "modelo-nvidia")
            self.assertTrue(kwargs["stream"])
            return iter(
                [
                    SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="Resposta"), finish_reason=None)]),
                    SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=None), finish_reason="stop")]),
                ]
            )

        client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=criar)))
        provider = ProviderNVIDIA(client=client, modelo="modelo-nvidia")

        self.assertEqual("".join(provider.transmitir([{"role": "user", "content": "Pergunta"}])), "Resposta")
        self.assertFalse(hasattr(provider, "gerar_embeddings"))

    def test_erro_http_e_normalizado_sem_expor_mensagem_bruta(self):
        class ErroHTTP(Exception):
            status_code = 429
            headers = {"retry-after": "3", "x-request-id": "nvidia-123"}

        client = SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **_kwargs: (_ for _ in ()).throw(ErroHTTP())))
        )
        provider = ProviderNVIDIA(client=client)

        with self.assertRaises(ErroProviderGeracao) as contexto:
            list(provider.transmitir([]))

        self.assertEqual(contexto.exception.provider, "NVIDIA")
        self.assertEqual(contexto.exception.status_code, 429)
        self.assertEqual(contexto.exception.retry_after, 3.0)
        self.assertEqual(contexto.exception.request_id, "nvidia-123")
        self.assertNotIn("ErroHTTP", str(contexto.exception))

    def test_timeout_opcional_e_repassado_ao_sdk(self):
        cliente = object()
        with patch("openai.OpenAI", return_value=cliente) as criar_cliente:
            provider = ProviderNVIDIA(
                secrets={},
                environ={"NVIDIA_API_KEY": "chave", "NVIDIA_TIMEOUT": "4.5"},
            )

        self.assertIs(provider._client, cliente)
        criar_cliente.assert_called_once_with(
            api_key="chave",
            base_url="https://integrate.api.nvidia.com/v1",
            max_retries=0,
            timeout=4.5,
        )

    def test_modelo_e_base_url_podem_vir_de_secrets(self):
        cliente = object()
        with patch("openai.OpenAI", return_value=cliente) as criar_cliente:
            provider = ProviderNVIDIA(
                secrets={
                    "NVIDIA_API_KEY": "chave",
                    "NVIDIA_MODEL": "modelo-secrets",
                    "NVIDIA_BASE_URL": "https://nvidia.example/v1",
                },
                environ={},
            )

        self.assertEqual(provider.modelo, "modelo-secrets")
        criar_cliente.assert_called_once_with(
            api_key="chave",
            base_url="https://nvidia.example/v1",
            max_retries=0,
        )


if __name__ == "__main__":
    unittest.main()
