"""Matriz real de quatro perguntas no corpus pt-br: provider isolado e cadeia. Registra só metadados."""
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
    ("recuperação", "Quais modelos de embeddings tiveram melhor desempenho em RAG para português?", None, "medeiros2025_embeddings_pt.pdf"),
    ("citação", "Como a segmentação ancorada e o enriquecimento com pré-contexto otimizam os chunks no domínio jurídico?", None, "brakes2025_rag_juridico.pdf"),
    ("recusa", "Qual é a receita de pão de queijo mineiro?", None, None),
    # Exclusão: o filtro remove o único artigo relevante (Xavier, 2024); a resposta correta é Recusa.
    ("filtro", "O que são grafos de conhecimento e como eles se integram ao RAG?", {"ano": {"$gte": 2025}}, None),
    # Filtro com resposta: só artigos de tema avaliacao/retrieval podem sustentar a resposta.
    ("filtro-tema", "O que é geração aumentada por recuperação?", {"tema": {"$in": ["avaliacao", "retrieval"]}}, None),
]
colecao = abrir_colecao_hibrida()
base = BaseAtiva("Corpus Oficial", colecao)
emb = ProviderEmbeddingsOllama()

def fora_do_filtro(cenario, fonte):
    if cenario == "filtro-tema":
        return fonte.get("tema") not in ("avaliacao", "retrieval")
    return fonte.get("ano", 0) < 2025


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
                             fontes_fora_filtro=[f for f in r["fontes_citadas"] if where and fora_do_filtro(cenario, f)],
                             tamanho_resposta=len(r["texto"]))
            except ErroProviderGeracao as e:
                linha.update(status="erro", erro_status=e.status_code, erro_provider=e.provider)
            linha.update(ttft=None if ttft is None else round(ttft, 2), total=round(time.perf_counter() - inicio, 2))
            print(json.dumps(linha, ensure_ascii=False), flush=True)

# Uso: medir_matriz.py [cenarios,separados,por,virgula] [alvos: NVIDIA,Gemini,OpenAI,cadeia]
SO_CENARIOS = set(sys.argv[1].split(",")) if len(sys.argv) > 1 else None
SO_ALVOS = set(sys.argv[2].split(",")) if len(sys.argv) > 2 else None
if SO_CENARIOS:
    MATRIZ = [m for m in MATRIZ if m[0] in SO_CENARIOS]
for nome, classe in (("NVIDIA", ProviderNVIDIA), ("Gemini", ProviderGemini), ("OpenAI", ProviderOpenAI)):
    if not SO_ALVOS or nome in SO_ALVOS:
        rodar(GenerationRouter([classe(secrets=SECRETS, environ={})]), nome, 1 if nome == "OpenAI" else 3)
if not SO_ALVOS or "cadeia" in SO_ALVOS:
    rodar(criar_generation_router(secrets=SECRETS, environ={}), "cadeia", 1)
