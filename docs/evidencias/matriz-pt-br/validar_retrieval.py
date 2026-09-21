"""Valida só o retrieval das perguntas da matriz (sem geração). Uso: python docs/evidencias/matriz-pt-br/validar_retrieval.py"""
import sys
sys.path.insert(0, ".")
from hybrid_index import abrir_colecao_hibrida
from ollama_embedding_provider import ProviderEmbeddingsOllama
from openai_rag import BaseAtiva, OpenAIRAG

col = abrir_colecao_hibrida()
rag = OpenAIRAG(ProviderEmbeddingsOllama(), None)
base = BaseAtiva("Corpus Oficial", col)
print(f"colecao={col.name} chunks={col.count()}")
CASOS = [
    ("recuperação", "Quais modelos de embeddings tiveram melhor desempenho em RAG para português?", None),
    ("citação", "Como a segmentação ancorada e o enriquecimento com pré-contexto otimizam os chunks no domínio jurídico?", None),
    ("recusa", "Qual é a receita de pão de queijo mineiro?", None),
    ("filtro (sem filtro)", "O que são grafos de conhecimento e como eles se integram ao RAG?", None),
    ("filtro (ano>=2025)", "O que são grafos de conhecimento e como eles se integram ao RAG?", {"ano": {"$gte": 2025}}),
    ("filtro-tema (sem filtro)", "O que é geração aumentada por recuperação?", None),
    ("filtro-tema (tema avaliacao/retrieval)", "O que é geração aumentada por recuperação?", {"tema": {"$in": ["avaliacao", "retrieval"]}}),
]
for rotulo, pergunta, where in CASOS:
    chunks = rag.buscar(pergunta, base, where=where, k=5)
    arquivos = [f"{c['arquivo']}({c['ano']},{c['distancia']:.3f})" for c in chunks]
    print(f"{rotulo}: {len(chunks)} chunks | {', '.join(arquivos) or '-'}")
