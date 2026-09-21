# Evidência FIN-01, FIN-02, FIN-07, FIN-08 (RODADA-2)

- **FIN-01 (OPS-09/NV-14):** causa — "Lewis et al." não aparece no texto dos chunks e a pergunta
  genérica sobre "arquitetura RAG" fica mais próxima do survey de Gao. A pergunta 1 passou a
  citar termos do artigo (RAG, retriever DPR, gerador BART): 5/5 chunks do top-5 vêm de
  `lewis2020_rag.pdf`. Limiar (`config.DISTANCIA_MAXIMA_RETRIEVAL`) **não** foi alterado.
  Ver `lewis-antes-depois.txt`.
- **FIN-02 (ARQ-08):** `retrieval_calibration.ARQUIVOS_ESPERADOS` e `medir_retrieval` reprovam quando o
  chunk mais próximo vem de outro documento. Calibração real em `calibracao.json`.
- **FIN-07 (OPS-01):** `scripts/00_checar_ambiente.py` exige só `bge-m3`; `OLLAMA_MODELS` virou aviso.
  Saída real em `checar_ambiente.txt` (exit 0, `Ambiente pronto.`).
- **FIN-08 (DEAD-01):** `salvar_metadados` movido para `corpus.py` (`rag.salvar_metadados` segue como
  reexport); `tests/test_corpus.py` cobre a escrita.

Reproduzir: `python -m unittest tests.test_corpus tests.test_retrieval_calibration`,
`python scripts/calibrar_retrieval_hibrido.py`, `python scripts/00_checar_ambiente.py`.
