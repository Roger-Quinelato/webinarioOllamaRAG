import os

import streamlit as st
from chromadb.errors import ChromaError
from streamlit.errors import StreamlitSecretNotFoundError

from generation_providers import NenhumProviderGeracaoConfigurado, criar_generation_router
from generation_router import ErroProviderGeracao
from hybrid_index import ColecaoHibridaIncompativel, abrir_colecao_hibrida
from ollama_embedding_provider import ErroProviderEmbeddingsOllama, ProviderEmbeddingsOllama
from openai_rag import MAX_CHUNKS_RETRIEVAL, OpenAIRAG, BaseAtiva
import config

st.set_page_config(page_title="Assistente RAG — CIIA", page_icon="📚", layout="wide")

def _secrets_geracao():
    """Auxilia secrets geração."""
    try:
        return dict(st.secrets)
    except (FileNotFoundError, KeyError, StreamlitSecretNotFoundError):
        return {}

@st.cache_resource
def providers():
    """Descreve providers."""
    return ProviderEmbeddingsOllama(), criar_generation_router(
        secrets=_secrets_geracao(), environ=os.environ
    )

@st.cache_resource
def base_oficial():
    """Descreve base oficial."""
    return BaseAtiva("Corpus Oficial", abrir_colecao_hibrida())

try:
    emb_provider, gen_provider = providers()
except NenhumProviderGeracaoConfigurado as erro:
    st.warning(f"⚠️ {erro}")
    st.stop()
rag = OpenAIRAG(emb_provider, gen_provider)

def montar_filtro(ano_minimo, temas, idiomas):
    """Monta filtro."""
    if not (ano_minimo or temas or idiomas):
        return None
    condicoes = []
    if ano_minimo:
        condicoes.append({"ano": {"$gte": ano_minimo}})
    if temas:
        condicoes.append({"tema": {"$in": temas}})
    if idiomas:
        condicoes.append({"idioma": {"$in": idiomas}})
    
    if not condicoes:
        return None
    if len(condicoes) == 1:
        return condicoes[0]
    return {"$and": condicoes}

def _mostrar_lista_fontes(fontes):
    """Mostra lista fontes."""
    for indice, fonte in enumerate(fontes, start=1):
        referencia = fonte.get("posicao", indice)
        ano_texto = f" · {fonte.get('ano', '?')}" if "ano" in fonte else ""
        st.markdown(
            f"**[{referencia}]** — `{fonte.get('arquivo', '?')}`, p. {fonte.get('pagina', '?')} "
            f"· distância {fonte.get('distancia', 0.0):.4f}{ano_texto}"
        )
        st.text(fonte["texto"][:700])


def mostrar_fontes(busca):
    """Mostra fontes."""
    chunks = busca["chunks_recuperados"]
    citadas = busca["fontes_citadas"]
    if busca["status"] == "Resposta Parcial":
        st.warning("A geração foi interrompida antes da conclusão.")
    provider = busca.get("generation_provider")
    detalhe_provider = f" · Geração: {provider}" if provider else ""
    if busca.get("fallback_used"):
        detalhe_provider += " (fallback)"
    st.caption(f"Base Ativa: {busca['base_ativa']} · Classe: {busca['classe_fontes']}{detalhe_provider}")
    if busca["classe_fontes"] == "recusa":
        return
    if citadas:
        with st.expander(f"Fontes Citadas ({len(citadas)})"):
            _mostrar_lista_fontes(citadas)
    elif chunks:
        with st.expander(f"Chunks Recuperados ({len(chunks)})"):
            _mostrar_lista_fontes(chunks)

st.title("📚 Assistente RAG sobre artigos de RAG")
st.caption("RAG híbrido com bge-m3 local e geração OpenAI, NVIDIA ou Gemini")

with st.sidebar:
    st.header("Configuração")
    if st.button("Limpar conversa"):
        st.session_state.mensagens = []
        st.rerun()
        
    k = st.slider("k (trechos no contexto)", 1, MAX_CHUNKS_RETRIEVAL, config.K_PADRAO)
    
    st.subheader("Filtros de metadados (Corpus Oficial)")
    ano_minimo = st.slider("Ano mínimo", 2020, 2026, 2020)
    temas = st.multiselect("Tema", config.TEMAS)
    idiomas = st.multiselect("Idioma", config.IDIOMAS)
    
    if not config.UPLOADS_STREAMLIT_HABILITADOS:
        st.info("Upload de PDFs ficará disponível após a apresentação.")
            
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

try:
    base_ativa = base_oficial()
    erro_base = None
except (ChromaError, ColecaoHibridaIncompativel):
    base_ativa = None
    erro_base = "Corpus Oficial indisponível. Execute a reindexação antes de consultar."

if not base_ativa:
    st.error(erro_base)
    st.stop()

identidade_base = base_ativa.colecao.name
if st.session_state.get("historico_base_ativa") not in (None, identidade_base):
    st.session_state.mensagens = []
st.session_state.historico_base_ativa = identidade_base

for mensagem in st.session_state.mensagens:
    if mensagem["papel"] in ["user", "assistant"]:
        with st.chat_message(mensagem["papel"]):
            st.markdown(mensagem["texto"])
            if mensagem["papel"] == "assistant" and "busca" in mensagem:
                mostrar_fontes(mensagem["busca"])

pergunta = st.chat_input("Pergunte algo...")
if pergunta:
    st.session_state.mensagens.append({"papel": "user", "texto": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)
    with st.chat_message("assistant"):
        try:
            if base_ativa.tipo == "Corpus Oficial":
                filtro = montar_filtro(ano_minimo, temas, idiomas)
            else:
                filtro = None
                
            # Manter apenas as últimas 2 interações (4 mensagens: user, assistant, user, assistant)
            historico = []
            for msg in st.session_state.mensagens[-5:-1]:
                if msg["papel"] in ["user", "assistant"]:
                    historico.append({"role": msg["papel"], "content": msg["texto"]})
            
            resposta_stream = rag.transmitir(pergunta, base_ativa, historico=historico, k=k, where=filtro)
            texto_gerado = st.write_stream(resposta_stream)
            
            busca = resposta_stream.resultado
            mostrar_fontes(busca)
            
            st.session_state.mensagens.append({
                "papel": "assistant",
                "texto": busca["texto"],
                "busca": busca
            })
            
        except ErroProviderGeracao as erro:
            st.error(f"⚠️ {erro}")
            st.session_state.mensagens.pop()
        except ErroProviderEmbeddingsOllama as erro:
            st.error(f"⚠️ {erro}")
            st.session_state.mensagens.pop()
        except ValueError as erro:
            st.error(f"⚠️ {erro}")
            st.session_state.mensagens.pop()
        except ChromaError:
            st.error("⚠️ Não foi possível consultar a Base Ativa. Confira a configuração e tente novamente.")
            st.session_state.mensagens.pop()
        except Exception:
            st.error("⚠️ Não foi possível concluir a resposta. Tente novamente.")
            st.session_state.mensagens.pop()
