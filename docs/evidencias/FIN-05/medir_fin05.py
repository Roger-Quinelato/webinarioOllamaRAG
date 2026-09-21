"""FIN-05: matriz real por provider e cadeia completa. Registra só metadados."""
import json, sys, time, tomllib
sys.path.insert(0, ".")
from generation_providers import criar_generation_router
from generation_router import ErroProviderGeracao, GenerationRouter
from gemini_provider import ProviderGemini
from hybrid_index import abrir_colecao_hibrida
from nvidia_provider import ProviderNVIDIA
from ollama_embedding_provider import ProviderEmbeddingsOllama
from openai_provider import ProviderOpenAI
from openai_rag import BaseAtiva, OpenAIRAG

SECRETS = tomllib.load(open(".streamlit/secrets.toml", "rb"))
MATRIZ = [
    ("recuperação", "Como o modelo RAG combina o retriever DPR com o gerador BART?", None, "lewis2020_rag.pdf"),
    ("citação", "Quais métricas o Ragas usa para avaliar fidelidade e relevância?", None, "es2023_ragas.pdf"),
    ("recusa", "Qual é a receita de pão de queijo mineiro?", None, None),
    ("filtro", "O que é Dense Passage Retrieval (DPR)?", {"ano": {"$gte": 2023}}, "gao2023_survey.pdf"),
]
colecao = abrir_colecao_hibrida()
base = BaseAtiva("Corpus Oficial", colecao)
emb = ProviderEmbeddingsOllama()

def rodar(roteador, rotulo, repeticoes):
    rag = OpenAIRAG(emb, roteador)
    for cenario, pergunta, where, esperado in MATRIZ:
        for rep in range(1 if cenario == "recusa" else repeticoes):
            inicio = time.perf_counter(); ttft = None; linha = {"alvo": rotulo, "cenario": cenario, "rep": rep + 1}
            try:
                fluxo = rag.transmitir(pergunta, base, where=where)
                for _ in fluxo:
                    if ttft is None: ttft = time.perf_counter() - inicio
                r = fluxo.resultado
                fontes = sorted({f"{f.get('arquivo')} p.{f.get('pagina')}" for f in r["fontes_citadas"]})
                linha.update(status=r["status"], classe=r["classe_fontes"], provider=r["generation_provider"],
                             modelo=r["generation_model"], tentados=r["attempted_providers"],
                             chunks=len(r["chunks_recuperados"]), fontes=fontes,
                             fonte_esperada_citada=bool(esperado) and any(esperado in f for f in fontes),
                             fontes_fora_filtro=[f for f in r["fontes_citadas"] if where and f.get("ano", 0) < 2023],
                             tamanho_resposta=len(r["texto"]))
            except ErroProviderGeracao as e:
                linha.update(status="erro", erro_status=e.status_code, erro_provider=e.provider)
            linha.update(ttft=None if ttft is None else round(ttft, 2), total=round(time.perf_counter() - inicio, 2))
            print(json.dumps(linha, ensure_ascii=False), flush=True)

for nome, classe in (("NVIDIA", ProviderNVIDIA), ("Gemini", ProviderGemini), ("OpenAI", ProviderOpenAI)):
    rodar(GenerationRouter([classe(secrets=SECRETS, environ={})]), nome, 1 if nome == "OpenAI" else 3)
rodar(criar_generation_router(secrets=SECRETS, environ={}), "cadeia", 1)
