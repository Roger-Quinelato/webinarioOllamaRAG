import unittest
from types import SimpleNamespace
from unittest.mock import patch

import openai_provider
from openai_provider import (
    ChaveOpenAIAusente,
    ErroProviderOpenAI,
    ProviderOpenAI,
    obter_chave_openai,
)


class ObterChaveOpenAITest(unittest.TestCase):
    def test_informa_como_configurar_quando_chave_esta_ausente(self):
        with self.assertRaisesRegex(ChaveOpenAIAusente, "OPENAI_API_KEY"):
            obter_chave_openai(secrets={}, environ={})

    def test_usa_ambiente_quando_secrets_nao_tem_chave(self):
        self.assertEqual(
            obter_chave_openai(secrets={}, environ={"OPENAI_API_KEY": "chave-de-ambiente"}),
            "chave-de-ambiente",
        )

    def test_cliente_desativa_retentativas_para_a_fachada_controlar_o_retry(self):
        cliente = object()
        with patch("openai.OpenAI", return_value=cliente) as criar_cliente:
            provider = ProviderOpenAI(secrets={}, environ={"OPENAI_API_KEY": "chave-de-ambiente"})

        self.assertIs(provider._client, cliente)
        criar_cliente.assert_called_once_with(api_key="chave-de-ambiente", max_retries=0)


class ProviderOpenAITest(unittest.TestCase):
    def test_expoe_somente_geracao_e_streaming(self):
        provider = ProviderOpenAI(client=object())

        self.assertFalse(hasattr(provider, "gerar_embeddings"))
        self.assertFalse(hasattr(openai_provider, "MODELO_EMBEDDING"))

    def test_geracao_e_streaming_usam_modelo_configurado(self):
        chamadas = []

        def criar(**kwargs):
            chamadas.append(kwargs)
            if kwargs.get("stream"):
                return iter([
                    SimpleNamespace(type="response.created"),
                    SimpleNamespace(type="response.output_text.delta", delta="Resposta"),
                    SimpleNamespace(type="response.completed"),
                ])
            return SimpleNamespace(status="completed", output_text="Resposta completa ")

        provider = ProviderOpenAI(client=SimpleNamespace(responses=SimpleNamespace(create=criar)))
        mensagens = [{"role": "user", "content": "Pergunta"}]

        self.assertEqual(provider.gerar(mensagens), "Resposta completa")
        self.assertEqual("".join(provider.transmitir(mensagens)), "Resposta")
        self.assertEqual(chamadas, [
            {"model": "gpt-5.6-luna", "input": mensagens},
            {"model": "gpt-5.6-luna", "input": mensagens, "stream": True},
        ])

    def test_streaming_reporta_falha_do_provider_apos_um_delta(self):
        def criar(**_kwargs):
            return iter([
                SimpleNamespace(type="response.output_text.delta", delta="Resposta parcial"),
                SimpleNamespace(type="response.failed"),
            ])

        provider = ProviderOpenAI(client=SimpleNamespace(responses=SimpleNamespace(create=criar)))

        fluxo = provider.transmitir([{"role": "user", "content": "Pergunta"}])
        self.assertEqual(next(fluxo), "Resposta parcial")
        with self.assertRaises(ErroProviderOpenAI):
            next(fluxo)

    def test_streaming_reporta_resposta_incompleta_antes_de_emitir_delta(self):
        def criar(**_kwargs):
            return iter([SimpleNamespace(type="response.incomplete")])

        provider = ProviderOpenAI(client=SimpleNamespace(responses=SimpleNamespace(create=criar)))

        with self.assertRaises(ErroProviderOpenAI):
            next(provider.transmitir([{"role": "user", "content": "Pergunta"}]))

    def test_geracao_incompleta_nao_retorna_texto_parcial_como_resposta(self):
        def criar(**_kwargs):
            return SimpleNamespace(status="incomplete", output_text="Trecho truncado")

        provider = ProviderOpenAI(client=SimpleNamespace(responses=SimpleNamespace(create=criar)))

        with self.assertRaises(ErroProviderOpenAI):
            provider.gerar([{"role": "user", "content": "Pergunta"}])

    def test_streaming_sem_evento_de_conclusao_reporta_falha(self):
        def criar(**_kwargs):
            return iter([SimpleNamespace(type="response.output_text.delta", delta="Trecho truncado")])

        provider = ProviderOpenAI(client=SimpleNamespace(responses=SimpleNamespace(create=criar)))
        fluxo = provider.transmitir([{"role": "user", "content": "Pergunta"}])

        self.assertEqual(next(fluxo), "Trecho truncado")
        with self.assertRaises(ErroProviderOpenAI):
            next(fluxo)


if __name__ == "__main__":
    unittest.main()
