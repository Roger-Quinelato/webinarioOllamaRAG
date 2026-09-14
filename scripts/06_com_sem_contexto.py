import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config  # noqa: E402
import rag  # noqa: E402

# TODO(autor): substituir pelas perguntas-teste definitivas da aula.
PERGUNTAS = [
    "Segundo o artigo Lost in the Middle, em que posições do contexto os modelos usam melhor a informação?",
    "Quais são os tokens de reflexão (reflection tokens) propostos no Self-RAG?",
    "Qual é a receita de pão de queijo mineiro?",
]

colecao = rag.abrir_colecao()
registros = []
for pergunta in PERGUNTAS:
    print("=" * 100)
    print(f"Pergunta: {pergunta}")
    resultados = rag.buscar(pergunta, k=config.K_PADRAO, colecao=colecao)
    mensagens = rag.montar_mensagens(pergunta, resultados)
    prompt = rag.formatar_mensagens(mensagens)
    print(f"\n--- Prompt enriquecido ({len(prompt)} caracteres), início:\n{prompt[:1100]}\n[…]\n{prompt[-250:]}")

    inicio = time.perf_counter()
    sem = rag.gerar_texto(rag.montar_mensagens(pergunta))
    tempo_sem = time.perf_counter() - inicio
    inicio = time.perf_counter()
    com = rag.gerar_texto(mensagens)
    tempo_com = time.perf_counter() - inicio

    fontes = "" if config.RESPOSTA_NAO_ENCONTRADA in com else f"\n\nFontes:\n{rag.formatar_fontes(resultados)}"
    print(f"\n--- SEM contexto ({tempo_sem:.1f}s):\n{sem}")
    print(f"\n--- COM contexto ({tempo_com:.1f}s):\n{com}{fontes}")
    registros.append({"pergunta": pergunta, "modelo": config.MODELO_CHAT, "prompt": prompt,
                      "sem_contexto": sem, "com_contexto": com,
                      "fontes": rag.formatar_fontes(resultados).splitlines(),
                      "segundos_sem": tempo_sem, "segundos_com": tempo_com})

config.PASTA_RESULTADOS.mkdir(exist_ok=True)
saida = config.PASTA_RESULTADOS / "com_sem_contexto.json"
saida.write_text(json.dumps(registros, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nSalvo em {saida.relative_to(config.RAIZ)}")
