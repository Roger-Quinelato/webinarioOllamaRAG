import unittest

from generation_router import ErroProviderGeracao, GenerationRouter
from openai_provider import ErroProviderOpenAI
from openai_rag import BaseAtiva, OpenAIRAG
from tests.test_openai_rag import ColecaoFake, EmbeddingProviderFake, chunks


class ProviderNomeado:
    """Provider que emite os deltas informados e depois, se pedido, falha."""

    def __init__(self, nome, deltas, erro=None):
        """Inicializa instância com dependências e parâmetros."""
        self.nome, self.modelo = nome, f"modelo-{nome}"
        self._deltas, self._erro = deltas, erro

    def transmitir(self, _mensagens):
        """Transmite valor do fluxo."""
        yield from self._deltas
        if self._erro:
            raise self._erro


class ProviderComFalhaInesperada:
    """Provider que levanta uma exceção que não é ErroProviderGeracao."""

    def transmitir(self, _mensagens):
        """Levanta antes de emitir qualquer token."""
        raise ValueError("defeito interno")
        yield


def _base():
    """Cria uma Base Ativa com chunks recuperáveis."""
    return BaseAtiva("Corpus Oficial", ColecaoFake(chunks()))


class FachadaAgnosticaTest(unittest.TestCase):
    """FIN-26: a fachada não atribui à OpenAI falhas de outro provider."""

    def test_falha_generica_antes_do_primeiro_token_nao_vira_erro_openai(self):
        """Verifica que a falha genérica sobe como ErroProviderGeracao, sem rótulo de provider."""
        rag = OpenAIRAG(EmbeddingProviderFake(), ProviderComFalhaInesperada())

        with self.assertRaises(ErroProviderGeracao) as contexto:
            rag.responder("pergunta", _base())

        self.assertNotIsInstance(contexto.exception, ErroProviderOpenAI)
        self.assertIsNone(contexto.exception.provider)

    def test_erro_de_provider_mantem_o_rotulo_de_quem_falhou(self):
        """Verifica que o erro tipado de um provider passa sem ser reescrito."""
        erro = ErroProviderGeracao("falhou", provider="NVIDIA", status_code=401)
        rag = OpenAIRAG(EmbeddingProviderFake(), ProviderNomeado("NVIDIA", [], erro))

        with self.assertRaises(ErroProviderGeracao) as contexto:
            rag.responder("pergunta", _base())

        self.assertEqual(contexto.exception.provider, "NVIDIA")


class TelemetriaPorExecucaoTest(unittest.TestCase):
    """FIN-25: o resultado usa a telemetria da própria execução."""

    def test_respostas_intercaladas_nao_trocam_provider_entre_si(self):
        """Verifica que duas respostas no mesmo roteador conservam cada uma o seu provider."""
        primeiro = ProviderNomeado("OpenAI", ["Resposta [1]"])
        rag = OpenAIRAG(EmbeddingProviderFake(), GenerationRouter([primeiro]))
        fluxo_a = rag.transmitir("pergunta a", _base())
        fluxo_b = rag.transmitir("pergunta b", _base())
        iterador_a, iterador_b = iter(fluxo_a), iter(fluxo_b)

        next(iterador_a)
        next(iterador_b)
        list(iterador_a)
        list(iterador_b)

        self.assertEqual(fluxo_a.resultado["generation_provider"], "OpenAI")
        self.assertEqual(fluxo_b.resultado["generation_provider"], "OpenAI")
        self.assertEqual(fluxo_a.resultado["attempted_providers"], ["OpenAI"])

    def test_resposta_parcial_usa_telemetria_da_execucao(self):
        """Verifica que a Resposta Parcial preserva o provider que emitiu o texto."""
        erro = ErroProviderGeracao("cortou", provider="NVIDIA", status_code=503)
        router = GenerationRouter(
            [
                ProviderNomeado("OpenAI", [], ErroProviderGeracao("x", provider="OpenAI", status_code=429)),
                ProviderNomeado("NVIDIA", ["Comeco"], erro),
            ]
        )
        rag = OpenAIRAG(EmbeddingProviderFake(), router)

        resultado = rag.responder("pergunta", _base())

        self.assertEqual(resultado["status"], "Resposta Parcial")
        self.assertEqual(resultado["generation_provider"], "NVIDIA")
        self.assertTrue(resultado["fallback_used"])


class RegistroMinimoTest(unittest.TestCase):
    """FIN-18: registro exigido pelo TDD, sem dados sensíveis."""

    def test_registra_campos_do_tdd_sem_prompt_chunk_ou_resposta(self):
        """Verifica que o registro traz Base Ativa, chunks, provider e modelo, e nada sensível."""
        rag = OpenAIRAG(
            EmbeddingProviderFake(), GenerationRouter([ProviderNomeado("Gemini", ["Resposta secreta [1]"])])
        )

        with self.assertLogs("rag.geracao", level="INFO") as registro:
            rag.responder("pergunta sigilosa", _base())

        saida = " | ".join(registro.output)
        for esperado in ("base_ativa=Corpus Oficial", "chunks=5", "provider=Gemini",
                         "modelo=modelo-Gemini", "status=completa", "recusa=False", "parcial=False"):
            self.assertIn(esperado, saida)
        for proibido in ("pergunta sigilosa", "Resposta secreta", "Trecho recuperado"):
            self.assertNotIn(proibido, saida)

    def test_registra_recusa_sem_resultados_e_resposta_parcial(self):
        """Verifica que Recusa e Resposta Parcial aparecem como sinalizadores no registro."""
        rag_recusa = OpenAIRAG(EmbeddingProviderFake(), GenerationRouter([]))
        with self.assertLogs("rag.geracao", level="INFO") as registro:
            rag_recusa.responder("pergunta", BaseAtiva("Corpus Oficial", ColecaoFake([])))
        self.assertIn("recusa=True", " | ".join(registro.output))

        erro = ErroProviderGeracao("cortou", provider="Gemini", status_code=503)
        rag_parcial = OpenAIRAG(
            EmbeddingProviderFake(), GenerationRouter([ProviderNomeado("Gemini", ["Inicio"], erro)])
        )
        with self.assertLogs("rag.geracao", level="INFO") as registro:
            rag_parcial.responder("pergunta", _base())
        self.assertIn("parcial=True", " | ".join(registro.output))


if __name__ == "__main__":
    unittest.main()
