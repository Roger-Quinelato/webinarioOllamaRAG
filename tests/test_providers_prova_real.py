import logging
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from gemini_provider import ProviderGemini
from generation_router import ErroProviderGeracao, ExecucaoGeracao
from nvidia_provider import ProviderNVIDIA
from openai_provider import ProviderOpenAI


class APIErrorSemStatus(Exception):
    """Imita ``openai.APIError`` de streaming: sem ``status_code``, com código e corpo."""

    def __init__(self, code=None, body=None):
        """Inicializa instância com dependências e parâmetros."""
        super().__init__("You have no credits remaining")
        self.code, self.body = code, body


def _openai(criar):
    """Cria ProviderOpenAI com a função ``create`` informada."""
    return ProviderOpenAI(client=SimpleNamespace(responses=SimpleNamespace(create=criar)))


def _nvidia(criar):
    """Cria ProviderNVIDIA com a função ``create`` informada."""
    return ProviderNVIDIA(
        client=SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=criar)))
    )


def _levantar(erro):
    """Cria uma função que levanta o erro informado."""

    def criar(**_kwargs):
        """Levanta o erro simulado."""
        raise erro

    return criar


class OpenAIStreamingSemStatusTest(unittest.TestCase):
    """FIN-04: erro de streaming da OpenAI sem ``status_code`` continua específico."""

    def test_sem_saldo_vira_429_com_mensagem_acionavel(self):
        """Verifica que ``credit_balance_exhausted`` sem status vira 429 e mensagem de saldo."""
        provider = _openai(_levantar(APIErrorSemStatus(code="credit_balance_exhausted")))

        with self.assertRaises(ErroProviderGeracao) as contexto:
            list(provider.transmitir([]))

        self.assertEqual(contexto.exception.status_code, 429)
        self.assertTrue(contexto.exception.retryable)
        self.assertIn("sem saldo", str(contexto.exception))

    def test_codigo_lido_do_corpo_estruturado(self):
        """Verifica que o código também é lido de ``body["error"]["code"]``."""
        erro = APIErrorSemStatus(body={"error": {"code": "invalid_api_key"}})
        provider = _openai(_levantar(erro))

        with self.assertRaises(ErroProviderGeracao) as contexto:
            list(provider.transmitir([]))

        self.assertEqual(contexto.exception.status_code, 401)
        self.assertIn("OPENAI_API_KEY", str(contexto.exception))

    def test_evento_de_erro_do_stream_preserva_o_codigo(self):
        """Verifica que evento ``response.failed`` com código de saldo não vira mensagem genérica."""
        evento = SimpleNamespace(
            type="response.failed",
            response=SimpleNamespace(error=SimpleNamespace(code="insufficient_quota", message="x")),
        )
        provider = _openai(lambda **_kwargs: iter([evento]))

        with self.assertRaises(ErroProviderGeracao) as contexto:
            list(provider.transmitir([]))

        self.assertEqual(contexto.exception.status_code, 429)
        self.assertIn("sem saldo", str(contexto.exception))

    def test_evento_de_erro_nao_expoe_a_mensagem_externa(self):
        """Verifica que a mensagem do evento nunca chega ao usuário."""
        evento = SimpleNamespace(type="error", code=None, message="segredo-do-provedor")
        provider = _openai(lambda **_kwargs: iter([evento]))

        with self.assertRaises(ErroProviderGeracao) as contexto:
            list(provider.transmitir([]))

        self.assertNotIn("segredo-do-provedor", str(contexto.exception))


class TimeoutOpenAITest(unittest.TestCase):
    """FIN-27: ``OPENAI_TIMEOUT`` configurável, como nos outros providers."""

    def test_timeout_vem_do_ambiente(self):
        """Verifica que o timeout do ambiente chega ao cliente."""
        with patch("openai.OpenAI") as criar_cliente:
            ProviderOpenAI(secrets={"OPENAI_API_KEY": "k"}, environ={"OPENAI_TIMEOUT": "12.5"})
        criar_cliente.assert_called_once_with(api_key="k", max_retries=0, timeout=12.5)

    def test_timeout_vem_de_secrets(self):
        """Verifica que o timeout também pode vir de secrets."""
        with patch("openai.OpenAI") as criar_cliente:
            ProviderOpenAI(secrets={"OPENAI_API_KEY": "k", "OPENAI_TIMEOUT": "7"}, environ={})
        criar_cliente.assert_called_once_with(api_key="k", max_retries=0, timeout=7.0)

    def test_sem_configuracao_mantem_o_padrao_do_sdk(self):
        """Verifica que, sem valor, nenhum timeout é passado ao cliente."""
        with patch("openai.OpenAI") as criar_cliente:
            ProviderOpenAI(secrets={"OPENAI_API_KEY": "k"}, environ={})
        criar_cliente.assert_called_once_with(api_key="k", max_retries=0)


class NVIDIAEstabilidadeTest(unittest.TestCase):
    """FIN-05: timeout definido, status preservado e diagnóstico do encerramento do stream."""

    def test_timeout_padrao_e_configuravel(self):
        """Verifica o timeout padrão de 30 s e a substituição por secrets ou ambiente."""
        with patch("openai.OpenAI") as criar_cliente:
            ProviderNVIDIA(secrets={"NVIDIA_API_KEY": "k"}, environ={})
            self.assertEqual(criar_cliente.call_args.kwargs["timeout"], 30.0)
            ProviderNVIDIA(secrets={"NVIDIA_API_KEY": "k", "NVIDIA_TIMEOUT": "8"}, environ={})
            self.assertEqual(criar_cliente.call_args.kwargs["timeout"], 8.0)
            ProviderNVIDIA(secrets={"NVIDIA_API_KEY": "k"}, environ={"NVIDIA_TIMEOUT": "5"})
            self.assertEqual(criar_cliente.call_args.kwargs["timeout"], 5.0)

    def test_status_da_resposta_e_preservado_no_stream(self):
        """Verifica que o status derivado de ``erro.response`` sobrevive ao streaming."""
        erro = APIErrorSemStatus()
        erro.response = SimpleNamespace(status_code=429, headers={"retry-after": "1"})
        provider = _nvidia(_levantar(erro))

        with self.assertRaises(ErroProviderGeracao) as contexto:
            list(provider.transmitir([]))

        self.assertEqual(contexto.exception.status_code, 429)
        self.assertEqual(contexto.exception.retry_after, 1.0)

    def test_evento_sem_choices_e_ignorado(self):
        """Verifica que evento sem ``choices`` (uso/keep-alive) não derruba o stream."""
        eventos = [
            SimpleNamespace(choices=[]),
            SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="Oi"), finish_reason=None)]),
            SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=None), finish_reason="stop")]),
        ]
        provider = _nvidia(lambda **_kwargs: iter(eventos))

        self.assertEqual("".join(provider.transmitir([])), "Oi")

    def test_registra_eventos_e_finish_reason_sem_conteudo(self):
        """Verifica o diagnóstico NV-11: quantos eventos chegaram e se houve ``finish_reason``."""
        eventos = [
            SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="texto-secreto"), finish_reason=None)]),
        ]
        provider = _nvidia(lambda **_kwargs: iter(eventos))

        with self.assertLogs("rag.geracao", level=logging.INFO) as registro:
            with self.assertRaises(ErroProviderGeracao):
                list(provider.transmitir([]))

        saida = " | ".join(registro.output)
        self.assertIn("eventos=1", saida)
        self.assertIn("finish_reason=False", saida)
        self.assertNotIn("texto-secreto", saida)


class GeminiFalhaRealTest(unittest.TestCase):
    """FIN-04 (H-2) e FIN-31: retry-after de mais de uma fonte e AFC desligado."""

    def test_retry_after_lido_dos_detalhes_do_erro(self):
        """Verifica que ``RetryInfo.retryDelay`` vira ``retry_after`` quando não há cabeçalho."""
        erro = SimpleNamespace(
            code=503,
            details={"error": {"code": 503, "details": [{"@type": "x.RetryInfo", "retryDelay": "2s"}]}},
        )
        provider = ProviderGemini(
            client=SimpleNamespace(models=SimpleNamespace(generate_content_stream=_levantar(_ExcecaoComAtributos(erro))))
        )

        with self.assertRaises(ErroProviderGeracao) as contexto:
            list(provider.transmitir([{"role": "user", "content": "P"}]))

        self.assertEqual(contexto.exception.status_code, 503)
        self.assertEqual(contexto.exception.retry_after, 2.0)

    def test_status_nao_inteiro_e_descartado(self):
        """Verifica que um ``code`` textual não vira status HTTP."""
        erro = _ExcecaoComAtributos(SimpleNamespace(code="UNAVAILABLE"))
        provider = ProviderGemini(
            client=SimpleNamespace(models=SimpleNamespace(generate_content_stream=_levantar(erro)))
        )

        with self.assertRaises(ErroProviderGeracao) as contexto:
            list(provider.transmitir([]))

        self.assertIsNone(contexto.exception.status_code)

    def test_geracao_e_streaming_desligam_afc(self):
        """Verifica que as duas vias passam AFC desligado, o que evita o aviso do SDK."""
        chamadas = []

        def stream(**kwargs):
            """Registra a chamada de streaming."""
            chamadas.append(kwargs)
            return iter([SimpleNamespace(text="ok")])

        def gerar(**kwargs):
            """Registra a chamada síncrona."""
            chamadas.append(kwargs)
            return SimpleNamespace(text="ok")

        provider = ProviderGemini(
            client=SimpleNamespace(models=SimpleNamespace(generate_content_stream=stream, generate_content=gerar))
        )
        list(provider.transmitir([{"role": "user", "content": "P"}]))
        provider.gerar([{"role": "user", "content": "P"}])

        self.assertEqual(len(chamadas), 2)
        for chamada in chamadas:
            self.assertEqual(chamada["config"], {"automatic_function_calling": {"disable": True}})


def _ExcecaoComAtributos(origem):
    """Cria uma exceção que copia os atributos de ``origem``."""
    erro = Exception("detalhe-interno")
    erro.__dict__.update(vars(origem))
    return erro


class RoteadorRepeteComRetryAfterDoGeminiTest(unittest.TestCase):
    """FIN-04: com ``retry-after`` derivado, o roteador repete uma vez antes de avançar."""

    def test_repete_uma_vez_quando_o_atraso_e_curto(self):
        """Verifica a repetição curta da ADR-003 com atraso vindo dos detalhes do erro."""
        erro = _ExcecaoComAtributos(
            SimpleNamespace(
                code=503,
                details={"error": {"details": [{"retryDelay": "1s"}]}},
            )
        )
        tentativas = []

        def stream(**_kwargs):
            """Falha na primeira chamada e responde na segunda."""
            tentativas.append(1)
            if len(tentativas) == 1:
                raise erro
            return iter([SimpleNamespace(text="ok")])

        provider = ProviderGemini(client=SimpleNamespace(models=SimpleNamespace(generate_content_stream=stream)))
        esperas = []
        execucao = ExecucaoGeracao([provider], [], esperas.append)

        self.assertEqual("".join(execucao), "ok")
        self.assertEqual(esperas, [1.0])
        self.assertEqual(len(tentativas), 2)


if __name__ == "__main__":
    unittest.main()
