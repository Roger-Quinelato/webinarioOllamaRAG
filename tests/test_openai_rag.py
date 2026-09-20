import unittest
from types import SimpleNamespace

from openai_rag import BaseAtiva, OpenAIRAG


def chunks():
    return [
        {
            "arquivo": f"artigo-{numero}.pdf",
            "titulo": f"Artigo {numero}",
            "pagina": numero,
            "ano": 2025,
            "tema": "retrieval",
            "idioma": "pt",
            "texto": f"Trecho recuperado {numero}",
            "distancia": 0.1,
        }
        for numero in range(1, 7)
    ]


class ColecaoFake:
    def __init__(self, resultados, metadata=None):
        self.resultados = resultados
        self.chamadas = []
        self.metadata = metadata or {
            "provedor_embedding": "Ollama",
            "modelo_embedding": "bge-m3",
            "dimensao_embedding": 1024,
            "versao_colecao": "bge-m3-v1",
            "status": "ready",
        }

    def query(self, **kwargs):
        self.chamadas.append(kwargs)
        resultados = self.resultados[: kwargs["n_results"]]
        return {
            "documents": [[resultado["texto"] for resultado in resultados]],
            "metadatas": [[{chave: valor for chave, valor in resultado.items() if chave not in {"texto", "distancia"}}
                           for resultado in resultados]],
            "distances": [[resultado["distancia"] for resultado in resultados]],
        }


class ProviderFake:
    def __init__(self, eventos_por_tentativa):
        self.eventos_por_tentativa = list(eventos_por_tentativa)
        self.perguntas_embedding = []
        self.mensagens = []

    def gerar_embeddings(self, textos):
        self.perguntas_embedding.extend(textos)
        return [[0.1, 0.2]]

    def transmitir(self, mensagens):
        self.mensagens.append(mensagens)
        eventos = self.eventos_por_tentativa.pop(0)
        for evento in eventos:
            if isinstance(evento, Exception):
                raise evento
            if evento != "__COMPLETO__":
                yield evento


class EmbeddingProviderFake:
    def __init__(self):
        self.textos = []

    def gerar_embeddings(self, textos):
        self.textos.extend(textos)
        return [[0.1, 0.2]]


class GenerationProviderFake:
    def __init__(self):
        self.mensagens = []

    def transmitir(self, mensagens):
        self.mensagens.append(mensagens)
        yield "Resposta [1]"


class OpenAIRAGTest(unittest.TestCase):
    def criar_rag(self, provider=None, resultados=None):
        provider = provider or ProviderFake([["Resposta [1]", "__COMPLETO__"]])
        colecao = ColecaoFake(resultados if resultados is not None else chunks())
        return OpenAIRAG(provider, provider), BaseAtiva("Corpus Oficial", colecao), provider, colecao

    def test_retrieval_e_geracao_usam_providers_distintos(self):
        embedding_provider = EmbeddingProviderFake()
        generation_provider = GenerationProviderFake()
        colecao = ColecaoFake(chunks())
        rag = OpenAIRAG(embedding_provider, generation_provider)

        resultado = rag.responder("pergunta atual", BaseAtiva("Corpus Oficial", colecao))

        self.assertEqual(embedding_provider.textos, ["pergunta atual"])
        self.assertEqual(len(generation_provider.mensagens), 1)
        self.assertEqual(resultado["texto"], "Resposta [1]")

    def test_base_ativa_rejeita_cada_metadado_incompativel_e_orienta_reindexacao(self):
        casos = {
            "provedor_embedding": "OpenAI",
            "modelo_embedding": "modelo-antigo",
            "dimensao_embedding": 2,
            "versao_colecao": "schema-antigo",
            "status": "building",
        }
        for campo, valor in casos.items():
            with self.subTest(campo=campo):
                colecao = ColecaoFake(chunks())
                colecao.metadata[campo] = valor
                rag = OpenAIRAG(EmbeddingProviderFake(), GenerationProviderFake())

                with self.assertRaisesRegex(ValueError, "reindexação"):
                    rag.buscar("pergunta", BaseAtiva("Corpus Oficial", colecao))

    def test_retrieval_usa_somente_pergunta_atual_e_no_maximo_cinco_chunks(self):
        rag, base, provider, colecao = self.criar_rag()

        recuperados = rag.buscar("pergunta atual", base, k=10)

        self.assertEqual(provider.perguntas_embedding, ["pergunta atual"])
        self.assertEqual(len(recuperados), 5)
        self.assertEqual(colecao.chamadas[0]["n_results"], 5)

    def test_retrieval_preserva_filtro_da_base_ativa(self):
        rag, base, _provider, colecao = self.criar_rag()

        rag.buscar("pergunta", base, where={"ano": {"$gte": 2024}})

        self.assertEqual(colecao.chamadas[0]["where"], {"ano": {"$gte": 2024}})

    def test_resposta_grounded_classifica_apenas_marcador_valido_como_fonte_citada(self):
        rag, base, _provider, _colecao = self.criar_rag()

        resultado = rag.responder("pergunta", base, k=5)

        self.assertEqual(resultado["texto"], "Resposta [1]")
        self.assertEqual(resultado["classe_fontes"], "citadas")
        self.assertEqual([fonte["arquivo"] for fonte in resultado["fontes_citadas"]], ["artigo-1.pdf"])

    def test_sem_evidencia_produz_recusa_sem_chamar_geracao(self):
        provider = ProviderFake([])
        rag, base, _provider, _colecao = self.criar_rag(provider, resultados=[])

        resultado = rag.responder("fora da base", base)

        self.assertEqual(resultado["classe_fontes"], "sem_resultados")
        self.assertEqual(resultado["texto"], "Não encontrei essa informação nos documentos.")
        self.assertEqual(provider.mensagens, [])

    def test_resposta_sem_marcador_e_fallback_sem_fonte_citada(self):
        provider = ProviderFake([["Explicação sem marcador", "__COMPLETO__"]])
        rag, base, _provider, _colecao = self.criar_rag(provider)

        resultado = rag.responder("pergunta", base)

        self.assertEqual(resultado["classe_fontes"], "fallback")
        self.assertEqual(resultado["fontes_citadas"], [])
        self.assertEqual(len(resultado["chunks_recuperados"]), 5)

    def test_transmitir_expoe_deltas_do_provider(self):
        provider = ProviderFake([["Parte 1", "Parte 2", "__COMPLETO__"]])
        rag, base, _provider, _colecao = self.criar_rag(provider)

        fluxo = list(rag.transmitir("pergunta", base))

        self.assertEqual(fluxo, ["Parte 1", "Parte 2"])

    def test_falha_antes_do_primeiro_token_faz_uma_repeticao(self):
        erro = RuntimeError("falha transitória")
        provider = ProviderFake([[erro], ["Resposta [1]", "__COMPLETO__"]])
        rag, base, _provider, _colecao = self.criar_rag(provider)

        resultado = rag.responder("pergunta", base)

        self.assertEqual(resultado["texto"], "Resposta [1]")
        self.assertEqual(len(provider.mensagens), 2)

    def test_falha_openai_nao_aciona_geracao_local(self):
        class GenerationProviderComFalha:
            def __init__(self):
                self.chamadas = 0

            def transmitir(self, _mensagens):
                self.chamadas += 1
                raise RuntimeError("OpenAI indisponível")
                yield

        embedding_provider = EmbeddingProviderFake()
        generation_provider = GenerationProviderComFalha()
        rag = OpenAIRAG(embedding_provider, generation_provider)
        base = BaseAtiva("Corpus Oficial", ColecaoFake(chunks()))

        with self.assertRaisesRegex(RuntimeError, "antes do primeiro token"):
            rag.responder("pergunta", base)

        self.assertEqual(generation_provider.chamadas, 2)
        self.assertEqual(embedding_provider.textos, ["pergunta"])

    def test_falha_depois_do_primeiro_token_preserva_e_marca_resposta_parcial(self):
        provider = ProviderFake([["Começo", RuntimeError("falha")]])
        rag, base, _provider, _colecao = self.criar_rag(provider)

        resultado = rag.responder("pergunta", base)

        self.assertTrue(resultado["texto"].startswith("Começo"))
        self.assertIn("Resposta Parcial", resultado["texto"])
        self.assertEqual(resultado["status"], "Resposta Parcial")
        self.assertEqual(len(provider.mensagens), 1)

    def test_geracao_recebe_somente_as_duas_ultimas_turnos(self):
        historico = [
            {"role": "user", "content": "antiga 1"},
            {"role": "assistant", "content": "antiga 2"},
            {"role": "user", "content": "atual 1"},
            {"role": "assistant", "content": "atual 2"},
            {"role": "user", "content": "atual 3"},
        ]
        rag, base, provider, _colecao = self.criar_rag()

        rag.responder("pergunta", base, historico=historico)

        self.assertEqual(
            [mensagem["content"] for mensagem in provider.mensagens[0][1:-1]],
            ["antiga 2", "atual 1", "atual 2", "atual 3"],
        )


if __name__ == "__main__":
    unittest.main()
