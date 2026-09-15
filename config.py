import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent

PASTA_ARTIGOS = RAIZ / "arquivosPDF" / "artigos"
ARQUIVO_METADADOS = RAIZ / "metadados.csv"
PASTA_CHROMA = RAIZ / "chroma_db"
PASTA_RESULTADOS = RAIZ / "resultados"
NOME_COLECAO = "artigos_rag"

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODELO_EMBEDDING = os.getenv("MODELO_EMBEDDING", "bge-m3")
MODELO_CHAT = os.getenv("MODELO_CHAT", "qwen2.5:3b")
MODELO_CHAT_PLANO_B = "qwen2.5:1.5b"

TAMANHO_CHUNK = 1000
SOBREPOSICAO = 150
K_PADRAO = 4
N_ARTIGOS_ESTAGIO_1 = 3
DISTANCIA_MAXIMA_ESTAGIO_1 = 0.60
TEMPERATURA = 0.1
MAX_TOKENS_RESPOSTA = 400

COLUNAS_METADADOS = ["arquivo", "titulo", "autores", "ano", "veiculo", "tema", "idioma", "resumo"]
TEMAS = ["fundamentos", "retrieval", "avaliacao", "survey", "limitacoes"]
IDIOMAS = ["en", "pt"]

ARTIGOS_ARXIV = {
    "lewis2020_rag.pdf": "https://arxiv.org/pdf/2005.11401",
    "karpukhin2020_dpr.pdf": "https://arxiv.org/pdf/2004.04906",
    "gao2023_survey.pdf": "https://arxiv.org/pdf/2312.10997",
    "es2023_ragas.pdf": "https://arxiv.org/pdf/2309.15217",
    "asai2023_selfrag.pdf": "https://arxiv.org/pdf/2310.11511",
    "liu2023_lost_middle.pdf": "https://arxiv.org/pdf/2307.03172",
}

RESPOSTA_NAO_ENCONTRADA = "Não encontrei essa informação nos documentos."
