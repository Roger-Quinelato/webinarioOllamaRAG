"""LACUNA A4: com que frequencia o modelo padrao emite citacoes [n]?

Le a colecao existente (nao reindexa), faz uma pergunta por vez e conta quantas respostas
trazem pelo menos um indice valido. Sem isso, o consolidado nao consegue dizer se a
demonstracao do criterio 6.5 e confiavel ao vivo.
"""
import sys
import time
from pathlib import Path

RAIZ = Path(r"D:\webinarioOllamaRAG")
sys.path.insert(0, str(RAIZ))

import config  # noqa: E402
import rag  # noqa: E402

PERGUNTAS = [
    "Quais métricas o Ragas usa para avaliar fidelidade e relevância?",
    "O que são os tokens de reflexão do Self-RAG?",
    "Por que a posição da informação no contexto afeta a performance?",
    "Como o DPR treina o retriever com exemplos negativos?",
    "Como funciona a arquitetura RAG proposta por Lewis et al.?",
    "Quais são os principais desafios de RAG discutidos no survey de Gao et al.?",
    "O que o artigo em português sobre ajuste fino sequencial propõe?",
    "Como comparar modelos de embeddings para RAG em português?",
]

colecao = rag.abrir_colecao()
print(f"modelo: {config.MODELO_CHAT} | k: {config.K_PADRAO} | seed fixo: {rag._opcoes()['seed']}")
print(f"colecao: {colecao.count()} vetores\n")

com_citacao = 0
for numero, pergunta in enumerate(PERGUNTAS, start=1):
    resultados = rag.buscar(pergunta, k=config.K_PADRAO, colecao=colecao)
    inicio = time.perf_counter()
    texto = rag.gerar_texto(rag.montar_mensagens(pergunta, resultados))
    duracao = time.perf_counter() - inicio
    indices = rag.indices_citados(texto, len(resultados))
    fontes = [i for i, _ in rag.fontes_da_resposta(texto, resultados)]
    recusa = rag.eh_recusa(texto)
    citou = bool(indices)
    com_citacao += citou
    print(f"{numero}. citou={'sim' if citou else 'NAO'} indices={indices} "
          f"fontes_exibidas={fontes} recusa={recusa} ({duracao:.1f}s)")
    print(f"   {texto[:100]!r}")

total = len(PERGUNTAS)
print(f"\nrespostas com pelo menos uma citacao valida: {com_citacao}/{total}")
print(f"respostas em que o fallback listou todo o top-k: {total - com_citacao}/{total}")
