import argparse
import json
import re
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config  # noqa: E402
import rag  # noqa: E402

parser = argparse.ArgumentParser(
    description="Métricas no estilo do Ragas (Es et al., 2023) usando o Ollama como juiz. Não roda ao vivo."
)
parser.add_argument("--modelo", default=config.MODELO_CHAT)
parser.add_argument("--k", type=int, default=config.K_PADRAO)
args = parser.parse_args()

# TODO(autor): trocar pelas perguntas-teste definitivas da aula.
PERGUNTAS = [
    "Quais são os tokens de reflexão (reflection tokens) propostos no Self-RAG?",
    "Segundo o artigo Lost in the Middle, em que posições do contexto os modelos usam melhor a informação?",
]


def linhas_numeradas(texto):
    return [re.sub(r"^\s*(?:\d+[.)]|[-*•])\s*", "", linha).strip()
            for linha in texto.splitlines() if linha.strip()]


def sim_ou_nao(texto):
    return texto.strip().lower().startswith(("sim", "yes"))


def fidelidade(resposta, contexto):
    afirmacoes = linhas_numeradas(rag.gerar_texto(
        "Quebre a resposta abaixo em afirmações curtas e independentes, uma por linha, numeradas.\n\n"
        f"Resposta:\n{resposta}", modelo=args.modelo, max_tokens=300))
    if not afirmacoes:
        return 0.0, []
    vereditos = [sim_ou_nao(rag.gerar_texto(
        f"Contexto:\n{contexto}\n\nA afirmação a seguir pode ser deduzida do contexto? "
        f"Responda apenas 'sim' ou 'não'.\nAfirmação: {afirmacao}", modelo=args.modelo, max_tokens=5))
        for afirmacao in afirmacoes]
    return sum(vereditos) / len(afirmacoes), list(zip(afirmacoes, vereditos))


def relevancia_resposta(pergunta, resposta, n=3):
    geradas = linhas_numeradas(rag.gerar_texto(
        f"Escreva {n} perguntas diferentes, uma por linha, numeradas, que a resposta abaixo responderia.\n\n"
        f"Resposta:\n{resposta}", modelo=args.modelo, max_tokens=200))[:n]
    if not geradas:
        return 0.0, []
    vetores = rag.gerar_embeddings([pergunta] + geradas)
    return float(np.mean([rag.similaridade_cosseno(vetores[0], v) for v in vetores[1:]])), geradas


def precisao_contexto(pergunta, resultados):
    relevantes = [sim_ou_nao(rag.gerar_texto(
        f"Pergunta: {pergunta}\n\nTrecho:\n{r['texto']}\n\nEste trecho ajuda a responder a pergunta? "
        "Responda apenas 'sim' ou 'não'.", modelo=args.modelo, max_tokens=5)) for r in resultados]
    return sum(relevantes) / len(resultados), relevantes


with rag.cli_seguro():
    avaliacoes = []
    for pergunta in PERGUNTAS:
        inicio = time.perf_counter()
        resultados = rag.buscar(pergunta, k=args.k)
        contexto = "\n\n".join(r["texto"] for r in resultados)
        resposta = rag.gerar_texto(rag.montar_mensagens(pergunta, resultados), modelo=args.modelo)
        fid, detalhes_fid = fidelidade(resposta, contexto)
        rel, perguntas_geradas = relevancia_resposta(pergunta, resposta)
        prec, relevantes = precisao_contexto(pergunta, resultados)
        avaliacao = {"pergunta": pergunta, "resposta": resposta, "fidelidade": fid, "relevancia_resposta": rel,
                     "precisao_contexto": prec, "afirmacoes": detalhes_fid, "perguntas_geradas": perguntas_geradas,
                     "trechos_relevantes": relevantes, "segundos": time.perf_counter() - inicio}
        avaliacoes.append(avaliacao)
        print(f"\n{pergunta}\n  fidelidade={fid:.2f}  relevância da resposta={rel:.2f}  "
              f"precisão do contexto={prec:.2f}  ({avaliacao['segundos']:.0f}s)")

    config.PASTA_RESULTADOS.mkdir(exist_ok=True)
    saida = config.PASTA_RESULTADOS / "avaliacao_estilo_ragas.json"
    saida.write_text(json.dumps(avaliacoes, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSalvo em {saida.relative_to(config.RAIZ)}")
