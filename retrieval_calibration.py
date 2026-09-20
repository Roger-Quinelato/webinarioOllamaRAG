"""Matriz versionada e calibração do retrieval do Corpus Oficial."""


PERGUNTAS_POSITIVAS = [
    "Como funciona a arquitetura RAG proposta por Lewis et al.?",
    "O que é Dense Passage Retrieval (DPR)?",
    "Quais métricas o Ragas usa para avaliar fidelidade e relevância?",
    "O que são os tokens de reflexão do Self-RAG?",
    "Por que a posição da informação no contexto afeta a performance, segundo Lost in the Middle?",
    "Quais são os principais desafios de RAG discutidos no survey de Gao et al.?",
    "Como o DPR treina o retriever com exemplos negativos?",
    "O que é retrieval-augmented generation?",
]
PERGUNTAS_NEGATIVAS = [
    "Qual é a receita de pão de queijo mineiro?",
    "Qual é a capital da Mongólia?",
    "Quais são as regras do xadrez?",
    "Como trocar o óleo de um carro?",
    "Qual é a previsão do tempo para amanhã em Belo Horizonte?",
]


def avaliar_limiar(distancias_positivas, distancias_negativas, *, limiar):
    """Valida um limiar contra intervalos medidos, sem sugerir valor arbitrário."""
    maior_positiva = max(distancias_positivas)
    menor_negativa = min(distancias_negativas)
    if maior_positiva >= menor_negativa:
        raise ValueError(
            "As distâncias positivas e negativas se sobrepõem; o corpus não admite um limiar separador."
        )
    if limiar < maior_positiva or limiar >= menor_negativa:
        raise ValueError(
            f"O limiar {limiar} não separa perguntas positivas e negativas "
            f"no intervalo medido ({maior_positiva}, {menor_negativa})."
        )
    return {
        "limiar_validado": limiar,
        "maior_distancia_positiva": maior_positiva,
        "menor_distancia_negativa": menor_negativa,
        "intervalo_seguro": [maior_positiva, menor_negativa],
    }


def medir_retrieval(colecao, provider, *, limiar):
    """Mede a matriz versionada na coleção híbrida e valida o limiar ativo."""
    perguntas = PERGUNTAS_POSITIVAS + PERGUNTAS_NEGATIVAS
    vetores = provider.gerar_embeddings(perguntas)
    if len(vetores) != len(perguntas):
        raise ValueError("O Provider Ollama não gerou um embedding por pergunta de calibração.")
    dimensao = (colecao.metadata or {}).get("dimensao_embedding")
    if any(len(vetor) != dimensao for vetor in vetores):
        raise ValueError("A dimensão das perguntas não corresponde à coleção híbrida.")
    resposta = colecao.query(
        query_embeddings=vetores,
        n_results=1,
        include=["distances", "metadatas"],
    )
    distancias = [valores[0] for valores in resposta["distances"]]
    corte = len(PERGUNTAS_POSITIVAS)
    resultado = avaliar_limiar(distancias[:corte], distancias[corte:], limiar=limiar)
    resultado["positivas"] = [
        {"pergunta": pergunta, "distancia": distancia, "arquivo": metadados[0].get("arquivo")}
        for pergunta, distancia, metadados in zip(
            PERGUNTAS_POSITIVAS, distancias[:corte], resposta["metadatas"][:corte]
        )
    ]
    resultado["negativas"] = [
        {"pergunta": pergunta, "distancia": distancia, "arquivo": metadados[0].get("arquivo")}
        for pergunta, distancia, metadados in zip(
            PERGUNTAS_NEGATIVAS, distancias[corte:], resposta["metadatas"][corte:]
        )
    ]
    return resultado
