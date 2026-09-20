import unittest
from types import SimpleNamespace

import chromadb

from generation_router import GenerationRouter
from ollama_embedding_provider import ProviderEmbeddingsOllama
from openai_provider import ErroProviderOpenAI
from openai_rag import BaseAtiva, OpenAIRAG


def chunks():
    """Descreve chunks."""
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
    """Representa Colecao Fake."""
    def __init__(self, resultados, metadata=None):
        """Inicializa instância com dependências e parâmetros."""
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
        """Descreve query."""
        self.chamadas.append(kwargs)
        resultados = self.resultados[: kwargs["n_results"]]
        return {
            "documents": [[resultado["texto"] for resultado in resultados]],
            "metadatas": [[{chave: valor for chave, valor in resultado.items() if chave not in {"texto", "distancia"}}
                           for resultado in resultados]],
            "distances": [[resultado["distancia"] for resultado in resultados]],
        }


class ProviderFake:
    """Representa Provider Fake."""
    def __init__(self, eventos_por_tentativa):
        """Inicializa instância com dependências e parâmetros."""
        self.eventos_por_tentativa = list(eventos_por_tentativa)
        self.perguntas_embedding = []
        self.mensagens = []

    def gerar_embeddings(self, textos):
        """Gera embeddings."""
        self.perguntas_embedding.extend(textos)
        return [[0.1] * 1024]

    def transmitir(self, mensagens):
        """Transmite valor do fluxo."""
        self.mensagens.append(mensagens)
        eventos = self.eventos_por_tentativa.pop(0)
        for evento in eventos:
            if isinstance(evento, Exception):
                raise evento
            if evento != "__COMPLETO__":
                yield evento


class EmbeddingProviderFake:
    """Representa Embedding Provider Fake."""
    def __init__(self):
        """Inicializa instância com dependências e parâmetros."""
        self.textos = []

    def gerar_embeddings(self, textos):
        """Gera embeddings."""
        self.textos.extend(textos)
        return [[0.1] * 1024]


class GenerationProviderFake:
    """Representa Generation Provider Fake."""
    def __init__(self):
        """Inicializa instância com dependências e parâmetros."""
        self.mensagens = []

    def transmitir(self, mensagens):
        """Transmite valor do fluxo."""
        self.mensagens.append(mensagens)
        yield "Resposta [1]"


class OpenAIRAGTest(unittest.TestCase):
    """Agrupa testes de OpenAI RAG Test. Herda de unittest.TestCase."""
    def criar_rag(self, provider=None, resultados=None):
        """Cria RAG."""
        provider = provider or ProviderFake([["Resposta [1]", "__COMPLETO__"]])
        colecao = ColecaoFake(resultados if resultados is not None else chunks())
        return OpenAIRAG(provider, provider), BaseAtiva("Corpus Oficial", colecao), provider, colecao

    def test_retrieval_e_geracao_usam_providers_distintos(self):
        """Verifica que retrieval e geração usam providers distintos."""
        embedding_provider = EmbeddingProviderFake()
        generation_provider = GenerationProviderFake()
        colecao = ColecaoFake(chunks())
        rag = OpenAIRAG(embedding_provider, generation_provider)

        resultado = rag.responder("pergunta atual", BaseAtiva("Corpus Oficial", colecao))

        self.assertEqual(embedding_provider.textos, ["pergunta atual"])
        self.assertEqual(len(generation_provider.mensagens), 1)
        self.assertEqual(resultado["texto"], "Resposta [1]")

    def test_resultado_registra_provider_que_concluiu_geracao(self):
        """Verifica que resultado registra provider que concluiu geração."""
        class ProviderNVIDIAFake:
            """Representa Provider NVIDIA Fake."""
            nome = "NVIDIA"
            modelo = "modelo-nvidia"

            def transmitir(self, _mensagens):
                """Transmite valor do fluxo."""
                yield "Resposta [1]"

        embedding_provider = EmbeddingProviderFake()
        rag = OpenAIRAG(embedding_provider, GenerationRouter([ProviderNVIDIAFake()]))

        resultado = rag.responder("pergunta", BaseAtiva("Corpus Oficial", ColecaoFake(chunks())))

        self.assertEqual(resultado["generation_provider"], "NVIDIA")
        self.assertEqual(resultado["generation_model"], "modelo-nvidia")
        self.assertFalse(resultado["fallback_used"])
        self.assertEqual(resultado["attempted_providers"], ["NVIDIA"])

    def test_router_com_todos_os_providers_em_falha_nao_refaz_retrieval(self):
        """Verifica que router com todos os providers em falha não refaz retrieval."""
        openai = ProviderFake([[ErroProviderOpenAI("limite", status_code=429)]])
        nvidia = ProviderFake([[ErroProviderOpenAI("indisponível", status_code=503)]])
        embedding_provider = EmbeddingProviderFake()
        rag = OpenAIRAG(embedding_provider, GenerationRouter([openai, nvidia]))

        with self.assertRaisesRegex(Exception, "Nenhum provider de geração"):
            rag.responder("pergunta", BaseAtiva("Corpus Oficial", ColecaoFake(chunks())))

        self.assertEqual(embedding_provider.textos, ["pergunta"])
        self.assertEqual(len(openai.mensagens), 1)
        self.assertEqual(len(nvidia.mensagens), 1)

    def test_base_ativa_rejeita_cada_metadado_incompativel_e_orienta_reindexacao(self):
        """Verifica que Base Ativa rejeita cada metadado incompativel e orienta reindexação."""
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

    def test_retrieval_recusa_dimensao_real_incompativel_antes_de_consultar_chroma(self):
        """Verifica que retrieval Recusa dimensão real incompativel antes de consultar chroma."""
        cliente = chromadb.EphemeralClient()
        nome_colecao = "issue-69-dimensao-consulta"
        if nome_colecao in {item.name for item in cliente.list_collections()}:
            cliente.delete_collection(nome_colecao)
        colecao = cliente.create_collection(
            nome_colecao,
            embedding_function=None,
            metadata={
                "provedor_embedding": "Ollama",
                "modelo_embedding": "bge-m3",
                "dimensao_embedding": 3,
                "versao_colecao": "bge-m3-v1",
                "status": "ready",
            },
        )
        self.addCleanup(cliente.delete_collection, nome_colecao)
        colecao.add(
            ids=["chunk-1"],
            documents=["Trecho recuperado"],
            metadatas=[{"arquivo": "artigo.pdf", "pagina": 1, "ano": 2025}],
            embeddings=[[0.1, 0.2, 0.3]],
        )

        def embed(**_kwargs):
            """Descreve embed."""
            return SimpleNamespace(embeddings=[[0.1, 0.2]])

        provider = ProviderEmbeddingsOllama(client=SimpleNamespace(embed=embed))
        rag = OpenAIRAG(provider, GenerationProviderFake())
        base = BaseAtiva("Corpus Oficial", colecao, dimensao_embedding=3)

        with self.assertRaisesRegex(ValueError, "dimensão.*reindexação|reindexação.*dimensão"):
            rag.buscar("pergunta", base)

    def test_retrieval_exige_exatamente_um_embedding_para_a_pergunta(self):
        """Verifica que retrieval exige exatamente um embedding para a pergunta."""
        for vetores in ([], [[0.1] * 1024, [0.2] * 1024]):
            with self.subTest(quantidade=len(vetores)):
                colecao = ColecaoFake(chunks())
                provider = SimpleNamespace(gerar_embeddings=lambda _textos: vetores)
                rag = OpenAIRAG(provider, GenerationProviderFake())

                with self.assertRaisesRegex(ValueError, "exatamente um embedding"):
                    rag.buscar("pergunta", BaseAtiva("Corpus Oficial", colecao))

                self.assertEqual(colecao.chamadas, [])

    def test_retrieval_usa_somente_pergunta_atual_e_no_maximo_cinco_chunks(self):
        """Verifica que retrieval usa somente pergunta atual e no maximo cinco chunks."""
        rag, base, provider, colecao = self.criar_rag()

        recuperados = rag.buscar("pergunta atual", base, k=10)

        self.assertEqual(provider.perguntas_embedding, ["pergunta atual"])
        self.assertEqual(len(recuperados), 5)
        self.assertEqual(colecao.chamadas[0]["n_results"], 5)

    def test_retrieval_aceita_limite_positivo_e_recusa_limite_negativo_calibrados(self):
        """Verifica que retrieval aceita limite positivo e Recusa limite negativo calibrados."""
        positivo = chunks()[0]
        positivo["distancia"] = 0.44007039070129395
        rag, base, _provider, _colecao = self.criar_rag(resultados=[positivo])

        self.assertEqual(len(rag.buscar("pergunta positiva", base)), 1)

        negativo = chunks()[0]
        negativo["distancia"] = 0.5800204873085022
        provider = ProviderFake([])
        rag, base, _provider, _colecao = self.criar_rag(provider, resultados=[negativo])

        resultado = rag.responder("pergunta negativa", base)

        self.assertEqual(resultado["status"], "Recusa")
        self.assertEqual(provider.mensagens, [])

    def test_retrieval_preserva_filtro_da_base_ativa(self):
        """Verifica que retrieval preserva filtro da Base Ativa."""
        rag, base, _provider, colecao = self.criar_rag()

        rag.buscar("pergunta", base, where={"ano": {"$gte": 2024}})

        self.assertEqual(colecao.chamadas[0]["where"], {"ano": {"$gte": 2024}})

    def test_resposta_grounded_classifica_apenas_marcador_valido_como_fonte_citada(self):
        """Verifica que resposta grounded classifica apenas marcador valido como fonte citada."""
        rag, base, _provider, _colecao = self.criar_rag()

        resultado = rag.responder("pergunta", base, k=5)

        self.assertEqual(resultado["texto"], "Resposta [1]")
        self.assertEqual(resultado["classe_fontes"], "citadas")
        self.assertEqual([fonte["arquivo"] for fonte in resultado["fontes_citadas"]], ["artigo-1.pdf"])

    def test_sem_evidencia_produz_recusa_sem_chamar_geracao(self):
        """Verifica que sem evidencia produz Recusa sem chamar geração."""
        provider = ProviderFake([])
        rag, base, _provider, _colecao = self.criar_rag(provider, resultados=[])

        resultado = rag.responder("fora da base", base)

        self.assertEqual(resultado["classe_fontes"], "sem_resultados")
        self.assertEqual(resultado["texto"], "Não encontrei essa informação nos documentos.")
        self.assertEqual(provider.mensagens, [])

    def test_resposta_sem_marcador_e_fallback_sem_fonte_citada(self):
        """Verifica que resposta sem marcador e fallback sem fonte citada."""
        provider = ProviderFake([["Explicação sem marcador", "__COMPLETO__"]])
        rag, base, _provider, _colecao = self.criar_rag(provider)

        resultado = rag.responder("pergunta", base)

        self.assertEqual(resultado["classe_fontes"], "fallback")
        self.assertEqual(resultado["fontes_citadas"], [])
        self.assertEqual(len(resultado["chunks_recuperados"]), 5)

    def test_transmitir_expoe_deltas_do_provider(self):
        """Verifica que transmitir expõe deltas do provider."""
        provider = ProviderFake([["Parte 1", "Parte 2", "__COMPLETO__"]])
        rag, base, _provider, _colecao = self.criar_rag(provider)

        fluxo = list(rag.transmitir("pergunta", base))

        self.assertEqual(fluxo, ["Parte 1", "Parte 2"])

    def test_falha_antes_do_primeiro_token_faz_uma_repeticao(self):
        """Verifica que falha antes do primeiro token faz uma repeticao."""
        erro = RuntimeError("falha transitória")
        provider = ProviderFake([[erro], ["Resposta [1]", "__COMPLETO__"]])
        rag, base, _provider, _colecao = self.criar_rag(provider)

        resultado = rag.responder("pergunta", base)

        self.assertEqual(resultado["texto"], "Resposta [1]")
        self.assertEqual(len(provider.mensagens), 2)

    def test_apos_retry_preserva_erro_seguro_de_autenticacao_openai(self):
        """Verifica que após retry preserva erro seguro de autenticação OpenAI."""
        mensagem = "Não foi possível autenticar na OpenAI. Confira a chave OPENAI_API_KEY e tente novamente."
        provider = ProviderFake(
            [
                [ErroProviderOpenAI(mensagem, status_code=401)],
                [ErroProviderOpenAI(mensagem, status_code=401)],
            ]
        )
        rag, base, _provider, _colecao = self.criar_rag(provider)

        with self.assertRaises(ErroProviderOpenAI) as contexto:
            rag.responder("pergunta", base)

        self.assertEqual(str(contexto.exception), mensagem)
        self.assertEqual(contexto.exception.status_code, 401)
        self.assertIsNone(contexto.exception.retry_after)
        self.assertEqual(len(provider.mensagens), 2)

    def test_apos_retry_preserva_erro_seguro_de_limite_openai(self):
        """Verifica que após retry preserva erro seguro de limite OpenAI."""
        mensagem = "A OpenAI atingiu o limite de requisições. Aguarde um momento e tente novamente."
        provider = ProviderFake(
            [
                [ErroProviderOpenAI(mensagem, status_code=429, retry_after=12.0)],
                [ErroProviderOpenAI(mensagem, status_code=429, retry_after=12.0)],
            ]
        )
        rag, base, _provider, _colecao = self.criar_rag(provider)

        with self.assertRaises(ErroProviderOpenAI) as contexto:
            rag.responder("pergunta", base)

        self.assertEqual(str(contexto.exception), mensagem)
        self.assertEqual(contexto.exception.status_code, 429)
        self.assertEqual(contexto.exception.retry_after, 12.0)
        self.assertEqual(len(provider.mensagens), 2)

    def test_apos_retry_preserva_erro_seguro_de_rede_openai(self):
        """Verifica que após retry preserva erro seguro de rede OpenAI."""
        mensagem = "Não foi possível conectar à OpenAI. Confira a conexão e tente novamente."
        provider = ProviderFake(
            [
                [ErroProviderOpenAI(mensagem)],
                [ErroProviderOpenAI(mensagem)],
            ]
        )
        rag, base, _provider, _colecao = self.criar_rag(provider)

        with self.assertRaises(ErroProviderOpenAI) as contexto:
            rag.responder("pergunta", base)

        self.assertEqual(str(contexto.exception), mensagem)
        self.assertIsNone(contexto.exception.status_code)
        self.assertIsNone(contexto.exception.retry_after)
        self.assertEqual(len(provider.mensagens), 2)

    def test_falha_openai_nao_aciona_geracao_local(self):
        """Verifica que falha OpenAI não aciona geração local."""
        class GenerationProviderComFalha:
            """Representa Generation Provider Com Falha."""
            def __init__(self):
                """Inicializa instância com dependências e parâmetros."""
                self.chamadas = 0

            def transmitir(self, _mensagens):
                """Transmite valor do fluxo."""
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
        """Verifica que falha depois do primeiro token preserva e marca Resposta Parcial."""
        provider = ProviderFake([["Começo", RuntimeError("falha")]])
        rag, base, _provider, _colecao = self.criar_rag(provider)

        resultado = rag.responder("pergunta", base)

        self.assertTrue(resultado["texto"].startswith("Começo"))
        self.assertIn("Resposta Parcial", resultado["texto"])
        self.assertEqual(resultado["status"], "Resposta Parcial")
        self.assertEqual(len(provider.mensagens), 1)

    def test_geracao_recebe_somente_as_duas_ultimas_turnos(self):
        """Verifica que geração recebe somente as duas ultimas turnos."""
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
