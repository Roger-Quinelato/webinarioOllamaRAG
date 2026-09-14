import json
import platform
import sys
import time
from datetime import datetime
from pathlib import Path

import psutil

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import config  # noqa: E402
import rag  # noqa: E402

cenario = sys.argv[1] if len(sys.argv) > 1 else "sem_nome"
medidas = {"cenario": cenario, "inicio": datetime.now().isoformat(timespec="seconds"),
           "maquina": {"cpu": platform.processor(), "ram_gb": round(psutil.virtual_memory().total / 2**30, 1)},
           "etapas": []}


def ram_livre():
    return round(psutil.virtual_memory().available / 2**30, 2)


def registrar(nome, segundos, **extra):
    item = {"etapa": nome, "segundos": round(segundos, 2), "ram_livre_gb": ram_livre(), **extra}
    medidas["etapas"].append(item)
    print(json.dumps(item, ensure_ascii=False))


def cronometrar(nome, funcao, **extra):
    inicio = time.perf_counter()
    resultado = funcao()
    registrar(nome, time.perf_counter() - inicio, **extra)
    return resultado


print(f"Cenário: {cenario} | RAM livre no início: {ram_livre()} GB")
colecao = rag.abrir_colecao()
pergunta = "Como o Self-RAG decide quando buscar documentos?"

for rodada in (1, 2):
    cronometrar(f"embedding da pergunta (rodada {rodada})", lambda: rag.gerar_embeddings([pergunta]))
for rodada in (1, 2):
    resultados = cronometrar(f"busca top-4 completa (rodada {rodada})", lambda: rag.buscar(pergunta, k=4, colecao=colecao))
cronometrar("busca em dois estágios", lambda: rag.buscar_dois_estagios(pergunta, k=4, colecao=colecao))

pergunta_shap = "Quais métricas o Ragas usa para avaliar fidelidade e relevância das respostas?"
chunk = rag.buscar(pergunta_shap, k=1, colecao=colecao)[0]
cronometrar("SHAP da similaridade (1 chunk, max_evals=200)", lambda: rag.explicar_similaridade(pergunta_shap, chunk["texto"]))

# why: o Ollama reaproveita o prefixo de um prompt repetido; perguntas diferentes medem o processamento real do prompt.
perguntas_llm = iter([
    "Como o Self-RAG decide quando buscar documentos?",
    "Quais métricas o Ragas propõe para avaliar RAG?",
    "Como o DPR treina o retriever denso?",
    "O que o survey chama de Naive RAG, Advanced RAG e Modular RAG?",
    "O que acontece quando a informação relevante está no meio do contexto?",
    "Qual a diferença entre RAG-Sequence e RAG-Token?",
])
for modelo in (config.MODELO_CHAT, config.MODELO_CHAT_PLANO_B, config.MODELO_CHAT):
    for rodada in (1, 2):
        pergunta_llm = next(perguntas_llm)
        mensagens = rag.montar_mensagens(pergunta_llm, rag.buscar(pergunta_llm, k=4, colecao=colecao))
        inicio = time.perf_counter()
        resposta = rag.cliente_ollama().chat(model=modelo, messages=mensagens, options=rag._opcoes())
        total = time.perf_counter() - inicio
        registrar(f"resposta RAG k=4 com {modelo} (rodada {rodada}: {pergunta_llm})", total,
                  carga_modelo_s=round(resposta.load_duration / 1e9, 2),
                  tokens_prompt=resposta.prompt_eval_count,
                  prompt_tokens_por_s=round(resposta.prompt_eval_count / (resposta.prompt_eval_duration / 1e9), 1),
                  tokens_gerados=resposta.eval_count,
                  geracao_tokens_por_s=round(resposta.eval_count / (resposta.eval_duration / 1e9), 1))

medidas["fim"] = datetime.now().isoformat(timespec="seconds")
saida = RAIZ / "docs" / "evidencias" / "E9" / f"medicao_{cenario}.json"
saida.parent.mkdir(parents=True, exist_ok=True)
saida.write_text(json.dumps(medidas, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Salvo em {saida.relative_to(RAIZ)}")
