import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent

PASTA_ARTIGOS = RAIZ / "artigos"
ARQUIVO_METADADOS = RAIZ / "metadados.csv"
PASTA_CHROMA = RAIZ / "chroma_db"
PASTA_RESULTADOS = RAIZ / "resultados"
NOME_COLECAO = "artigos_rag"

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODELO_EMBEDDING = os.getenv("MODELO_EMBEDDING", "bge-m3")
# T19/#19 (decisão parcial do autor, 2026-09-15): valida a pipeline com o 1.5b primeiro;
# o 3b vira o "plano B" para testar depois se a máquina/notebook aguenta. Perguntas-teste
# definitivas ainda pendentes (ticket segue aberto para a parte (a)).
MODELO_CHAT = os.getenv("MODELO_CHAT", "qwen2.5:1.5b")
MODELO_CHAT_PLANO_B = "qwen2.5:3b"

TAMANHO_CHUNK = 1000
SOBREPOSICAO = 150
K_PADRAO = 4
N_ARTIGOS_ESTAGIO_1 = 3
DISTANCIA_MAXIMA_ESTAGIO_1 = 0.60
# Ponto médio do intervalo real (0.37379246950149536, 0.5800204873085022) no corpus
# só em português (2026-09-21), com margem igual para perguntas positivas e negativas.
DISTANCIA_MAXIMA_RETRIEVAL = 0.4769064784049988
TEMPERATURA = 0.1
MAX_TOKENS_RESPOSTA = 400
UPLOADS_STREAMLIT_HABILITADOS = False

COLUNAS_METADADOS = ["arquivo", "titulo", "autores", "ano", "veiculo", "tema", "idioma", "resumo"]
TEMAS = ["fundamentos", "retrieval", "avaliacao", "aplicacoes"]
IDIOMAS = ["pt"]

ARTIGOS_CORPUS = {
    # Corpus só em português (decisão do autor, 2026-09-21); os artigos em inglês saíram.
    "rocha2025_ragsft.pdf": "https://sol.sbc.org.br/index.php/sbbd/article/download/37242/37025/",
    "medeiros2025_embeddings_pt.pdf": "https://sol.sbc.org.br/index.php/semish/article/download/36829/36615/",
    "brakes2025_rag_juridico.pdf": "https://sol.sbc.org.br/index.php/erigo/article/download/39531/39303/",
    "xavier2024_rag_grafos.pdf": "https://books-sol.sbc.org.br/index.php/sbc/catalog/download/153/658/1179",
}

RESPOSTA_NAO_ENCONTRADA = "Não encontrei essa informação nos documentos."
