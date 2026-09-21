import unittest
from types import SimpleNamespace

from generation_router import ErroProviderGeracao
from gemini_provider import ProviderGemini
from nvidia_provider import ProviderNVIDIA
from openai_provider import ProviderOpenAI


class ErroSDK(Exception):
    """Erro de SDK com status HTTP e cabeçalhos configuráveis. Herda de Exception."""

    def __init__(self, status_code=None, headers=None, **extras):
        """Inicializa instância com dependências e parâmetros."""
        super().__init__("detalhe-interno-nao-exibir")
        self.status_code = status_code
        self.headers = headers
        self.__dict__.update(extras)


def _levantar(erro):
    """Cria um método que levanta o erro informado."""

    def criar(**_kwargs):
        """Levanta o erro simulado."""
        raise erro

    return criar


def _providers(erro):
    """Constrói os três providers com um cliente que sempre falha com o erro informado."""
    return [
        ProviderOpenAI(
            client=SimpleNamespace(responses=SimpleNamespace(create=_levantar(erro)))
        ),
        ProviderNVIDIA(
            client=SimpleNamespace(
                chat=SimpleNamespace(completions=SimpleNamespace(create=_levantar(erro)))
            )
        ),
        ProviderGemini(
            client=SimpleNamespace(
                models=SimpleNamespace(
                    generate_content_stream=_levantar(erro), generate_content=_levantar(erro)
                )
            )
        ),
    ]


class ParidadeDosProvidersTest(unittest.TestCase):
    """Garante as mesmas invariantes de erro e de mensagem nos três providers."""

    def test_mensagens_descrevem_o_ocorrido_sem_prometer_fallback_ou_repeticao(self):
        """Verifica que nenhum provider promete o próximo passo, que é decisão do roteador."""
        erros = [
            ErroSDK(status_code=401),
            ErroSDK(status_code=429),
            ErroSDK(status_code=503),
            ConnectionError("rede"),
        ]
        for erro in erros:
            for provider in _providers(erro):
                with self.subTest(provider=provider.nome, erro=repr(erro)):
                    with self.assertRaises(ErroProviderGeracao) as contexto:
                        list(provider.transmitir([{"role": "user", "content": "P"}]))
                    mensagem = str(contexto.exception).lower()
                    self.assertNotIn("outro provider", mensagem)
                    self.assertNotIn("tente novamente", mensagem)
                    self.assertNotIn("detalhe-interno", mensagem)

    def test_erro_normalizado_traz_provider_status_e_retryable(self):
        """Verifica que os três providers normalizam provider, status e retry-after do mesmo modo."""
        erro = ErroSDK(status_code=429, headers={"retry-after": "1.5", "x-request-id": "req-1"})
        for provider in _providers(erro):
            with self.subTest(provider=provider.nome):
                with self.assertRaises(ErroProviderGeracao) as contexto:
                    list(provider.transmitir([]))
                normalizado = contexto.exception
                self.assertEqual(normalizado.provider, provider.nome)
                self.assertEqual(normalizado.status_code, 429)
                self.assertEqual(normalizado.retry_after, 1.5)
                self.assertEqual(normalizado.request_id, "req-1")
                self.assertTrue(normalizado.retryable)

    def test_status_vem_da_resposta_quando_o_erro_nao_o_expoe(self):
        """Verifica que o status é derivado de ``erro.response`` nos três providers."""
        erro = ErroSDK(response=SimpleNamespace(status_code=503, headers={"retry-after": "2"}))
        for provider in _providers(erro):
            with self.subTest(provider=provider.nome):
                with self.assertRaises(ErroProviderGeracao) as contexto:
                    list(provider.transmitir([]))
                self.assertEqual(contexto.exception.status_code, 503)
                self.assertEqual(contexto.exception.retry_after, 2.0)
                self.assertTrue(contexto.exception.retryable)


if __name__ == "__main__":
    unittest.main()
