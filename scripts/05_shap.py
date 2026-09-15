import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config  # noqa: E402
import rag  # noqa: E402

with rag.cli_seguro():
    pergunta = "Quais métricas o Ragas usa para avaliar fidelidade e relevância das respostas?"
    resultados = rag.buscar(pergunta, k=2)

    config.PASTA_RESULTADOS.mkdir(exist_ok=True)
    for resultado in resultados:
        print(f"\nChunk {resultado['posicao']}: {resultado['arquivo']} p.{resultado['pagina']} "
              f"(similaridade {resultado['similaridade']:.4f})")
        inicio = time.perf_counter()
        explicacao, funcao = rag.explicar_similaridade(pergunta, resultado["texto"])
        duracao = time.perf_counter() - inicio

        tokens = [str(t) for t in explicacao.data[0]]
        valores = [float(v) for v in explicacao.values[0]]
        base = float(explicacao.base_values[0])
        real = float(funcao([pergunta])[0])
        print(f"SHAP em {duracao:.1f}s")
        for token, valor in sorted(zip(tokens, valores), key=lambda par: -abs(par[1])):
            if token.strip():
                print(f"   {valor:+.4f}  {token.strip()}")
        print(f"Aditividade: base {base:.4f} + soma {sum(valores):+.4f} = {base + sum(valores):.4f} "
              f"| similaridade real {real:.4f} | diferença {abs(base + sum(valores) - real):.6f}")

        import shap

        html = shap.plots.text(explicacao[0], display=False)
        saida = config.PASTA_RESULTADOS / f"shap_similaridade_chunk{resultado['posicao']}.html"
        saida.write_text(html, encoding="utf-8")
        (config.PASTA_RESULTADOS / f"shap_similaridade_chunk{resultado['posicao']}.json").write_text(
            json.dumps({"pergunta": pergunta, "chunk_id": resultado["chunk_id"], "tokens": tokens,
                        "valores": valores, "base": base, "similaridade_real": real, "segundos": duracao},
                       ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Gráfico salvo em {saida.relative_to(config.RAIZ)}")
