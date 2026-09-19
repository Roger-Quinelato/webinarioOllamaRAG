import unittest
from types import SimpleNamespace
from unittest.mock import patch

import httpx

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
    def test_embeddings_usam_modelo_configurado_na_fronteira_openai(self):
        chamadas = []

        def criar(**kwargs):
            chamadas.append(kwargs)
            return SimpleNamespace(data=[SimpleNamespace(embedding=[0.1, 0.2])])

        provider = ProviderOpenAI(client=SimpleNamespace(embeddings=SimpleNamespace(create=criar)))

        self.assertEqual(provider.gerar_embeddings(["chunk recuperado"]), [[0.1, 0.2]])
        self.assertEqual(chamadas, [{"model": "text-embedding-3-small", "input": ["chunk recuperado"]}])

    def test_erro_de_autenticacao_tem_mensagem_acionavel_sem_detalhe_do_provider(self):
        class ErroAutenticacao(Exception):
            status_code = 401

        def criar(**_kwargs):
            raise ErroAutenticacao("sk-nao-exiba")

        provider = ProviderOpenAI(client=SimpleNamespace(embeddings=SimpleNamespace(create=criar)))

        with self.assertRaisesRegex(ErroProviderOpenAI, "chave OPENAI_API_KEY") as contexto:
            provider.gerar_embeddings(["chunk recuperado"])
        self.assertNotIn("sk-nao-exiba", str(contexto.exception))

    def test_erro_de_limite_tem_orientacao_de_espera(self):
        class ErroLimite(Exception):
            status_code = 429

        def criar(**_kwargs):
            raise ErroLimite()

        provider = ProviderOpenAI(client=SimpleNamespace(embeddings=SimpleNamespace(create=criar)))

        with self.assertRaisesRegex(ErroProviderOpenAI, "Aguarde"):
            provider.gerar_embeddings(["chunk recuperado"])

    def test_erro_de_rede_tem_orientacao_de_conexao(self):
        def criar(**_kwargs):
            raise httpx.ConnectError("rede indisponível")

        provider = ProviderOpenAI(client=SimpleNamespace(embeddings=SimpleNamespace(create=criar)))

        with self.assertRaisesRegex(ErroProviderOpenAI, "conexão"):
            provider.gerar_embeddings(["chunk recuperado"])

    def test_geracao_e_streaming_usam_modelo_configurado(self):
        chamadas = []

        def criar(**kwargs):
            chamadas.append(kwargs)
            if kwargs.get("stream"):
                return iter([
                    SimpleNamespace(type="response.created"),
                    SimpleNamespace(type="response.output_text.delta", delta="Resposta"),
                ])
            return SimpleNamespace(output_text="Resposta completa ")

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


if __name__ == "__main__":
    unittest.main()
