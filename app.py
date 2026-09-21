import os

import streamlit as st
from chromadb.errors import ChromaError
from streamlit.errors import StreamlitSecretNotFoundError

from generation_providers import (
    NenhumProviderGeracaoConfigurado,
    OrdemProvidersInvalida,
    criar_generation_router,
)
from generation_router import ErroProviderGeracao
from hybrid_index import ColecaoHibridaIncompativel, abrir_colecao_hibrida
from ollama_embedding_provider import ErroProviderEmbeddingsOllama, ProviderEmbeddingsOllama
from openai_rag import MAX_CHUNKS_RETRIEVAL, OpenAIRAG, BaseAtiva
import config

st.set_page_config(
    page_title="Assistente RAG — CIIA", page_icon=":material/menu_book:", layout="wide"
)

st.markdown(
    """
    <style>
    h1 { font-size: 1.9rem !important; }
    [data-testid="stCaptionContainer"] { color: #B8BFCC !important; opacity: 1 !important; font-size: 0.85rem; }
    [data-testid="stChatInputSubmitButton"] { min-width: 44px; min-height: 44px; }
    </style>
    """,
    unsafe_allow_html=True,
)

AVATAR_USUARIO = ":material/person:"
AVATAR_ASSISTENTE = ":material/smart_toy:"


def _avatar(papel):
    """Escolhe o avatar do papel."""
    return AVATAR_USUARIO if papel == "user" else AVATAR_ASSISTENTE

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
except (NenhumProviderGeracaoConfigurado, OrdemProvidersInvalida) as erro:
    st.warning(f"⚠️ {erro}")
    st.stop()
rag = OpenAIRAG(emb_provider, gen_provider)

def montar_filtro(ano_minimo, temas):
    """Monta filtro."""
    if not (ano_minimo or temas):
        return None
    condicoes = []
    if ano_minimo:
        condicoes.append({"ano": {"$gte": ano_minimo}})
    if temas:
        condicoes.append({"tema": {"$in": temas}})
    
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


def _resumo_arquivos(fontes):
    """Resume os arquivos das fontes para o cabeçalho do expander."""
    arquivos = list(dict.fromkeys(f.get("arquivo", "?") for f in fontes))
    return arquivos[0] if len(arquivos) == 1 else f"{arquivos[0]} e mais {len(arquivos) - 1}"


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
    classe = busca["classe_fontes"]
    detalhe_classe = "" if classe == "citadas" else f" · Classe: {classe}"
    st.caption(f"Base Ativa: {busca['base_ativa']}{detalhe_classe}{detalhe_provider}")
    if classe == "recusa":
        return
    if citadas:
        with st.expander(f"Fontes Citadas ({len(citadas)}) · {_resumo_arquivos(citadas)}", expanded=True):
            _mostrar_lista_fontes(citadas)
    elif chunks:
        with st.expander(f"Chunks Recuperados ({len(chunks)})"):
            _mostrar_lista_fontes(chunks)

st.title("Assistente RAG sobre artigos de RAG")
st.caption(f"RAG híbrido com {config.MODELO_EMBEDDING} local e geração OpenAI, NVIDIA ou Gemini")

with st.sidebar:
    st.header("Configuração")
    if st.button("Limpar conversa", icon=":material/delete:"):
        st.session_state.mensagens = []
        st.rerun()

    k = st.slider(
        "Trechos consultados (k)",
        1,
        MAX_CHUNKS_RETRIEVAL,
        config.K_PADRAO,
        help="Quantidade de trechos do corpus enviados ao modelo para responder cada pergunta.",
    )

    st.subheader("Filtros do Corpus")
    ano_minimo = st.slider("Ano mínimo", 2020, 2026, 2020)
    temas = st.multiselect("Tema", config.TEMAS, placeholder="Selecione os temas")
    
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
        with st.chat_message(mensagem["papel"], avatar=_avatar(mensagem["papel"])):
            st.markdown(mensagem["texto"])
            if mensagem["papel"] == "assistant" and "busca" in mensagem:
                mostrar_fontes(mensagem["busca"])

pergunta = st.chat_input("Pergunte algo...")
if pergunta:
    st.session_state.mensagens.append({"papel": "user", "texto": pergunta})
    with st.chat_message("user", avatar=AVATAR_USUARIO):
        st.markdown(pergunta)
    with st.chat_message("assistant", avatar=AVATAR_ASSISTENTE):
        try:
            if base_ativa.tipo == "Corpus Oficial":
                filtro = montar_filtro(ano_minimo, temas)
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
