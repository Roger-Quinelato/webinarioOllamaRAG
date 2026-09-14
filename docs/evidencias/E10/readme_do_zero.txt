[04:39:43] Cópia limpa (equivalente ao git clone): arquivos versionáveis, sem .venv/chroma_db/PDFs
[04:39:44] Passo 4: python -m venv .venv + ativar + pip install -r requirements.txt
[04:40:36]   → exit 0 em 52s: python -m venv .venv
[05:02:28]   → exit 0 em 1311s: python -m pip install -r requirements.txt
[05:02:28] Passo 4: registrar kernel (nome alterado para não sobrescrever o kernel real: webinario-rag-teste)
[05:02:48]   → exit 0 em 20s: python -m ipykernel install --user --name webinario-rag-teste --display-name Python (webinario-rag-teste)
[05:02:48] Passo 5
[05:03:32]   → exit 0 em 43s: python scripts/00_checar_ambiente.py
[05:03:32] Passo 6
[05:04:03]   → exit 0 em 30s: python scripts/01_preparar_corpus.py
[05:04:03] Passo 7
[05:24:46]   → exit 0 em 1243s: python scripts/02_indexar.py
[05:24:47] Passo 8
[05:25:04]   → exit 0 em 16s: python scripts/03_buscar.py
[05:25:13]   → exit 0 em 8s: python scripts/04_dois_estagios.py
[05:27:17]   → exit 0 em 124s: python scripts/05_shap.py
[05:31:06]   → exit 0 em 229s: python scripts/06_com_sem_contexto.py
[05:32:58]   → exit 0 em 111s: python scripts/07_ollama.py Como o Self-RAG decide quando buscar documentos?
[05:32:58] Passo 9: streamlit run app.py (porta 8502, headless) e checagem HTTP
[05:33:10]   → HTTP 200 em http://localhost:8502
[05:33:12] Fim
