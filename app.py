import uuid

import streamlit as st
from chromadb.errors import ChromaError

from corpus import extrair_paginas, dividir_texto
from hybrid_index import ColecaoHibridaIncompativel, abrir_colecao_hibrida
from ollama_embedding_provider import ErroProviderEmbeddingsOllama, ProviderEmbeddingsOllama
from openai_provider import ProviderOpenAI, obter_chave_openai, ChaveOpenAIAusente, ErroProviderOpenAI
from openai_rag import OpenAIRAG, BaseAtiva
from session_index import criar_indice_sessao
import config

st.set_page_config(page_title="Assistente RAG — CIIA", page_icon="📚", layout="wide")

try:
    chave_openai = obter_chave_openai()
except ChaveOpenAIAusente as erro:
    st.warning(f"⚠️ {erro}")
    st.stop()

@st.cache_resource
def providers():
    return ProviderEmbeddingsOllama(), ProviderOpenAI(
        secrets={"OPENAI_API_KEY": chave_openai}, environ={}
    )

@st.cache_resource
def base_oficial():
    return BaseAtiva("Corpus Oficial", abrir_colecao_hibrida())

emb_provider, gen_provider = providers()
rag = OpenAIRAG(emb_provider, gen_provider)

def processar_upload(arquivos_upload, ano_opcional):
    chunks = []
    for arquivo in arquivos_upload:
        if arquivo.size > 20 * 1024 * 1024:
            st.warning(f"O arquivo {arquivo.name} excede o limite de 20MB.")
            continue
        try:
            from pypdf import PdfReader
            paginas = [p.extract_text() or "" for p in PdfReader(arquivo).pages]
            from corpus import limpar_texto
            paginas = [limpar_texto(p) for p in paginas]
            
            stem = arquivo.name.rsplit('.', 1)[0]
            for pagina, texto_pagina in enumerate(paginas, start=1):
                from corpus import dividir_texto
                for parte, texto in enumerate(dividir_texto(texto_pagina)):
                    chunk_id = f"{stem}-p{pagina:03d}-c{parte:02d}"
                    meta = {
                        "arquivo": arquivo.name,
                        "pagina": pagina,
                        "chunk_id": chunk_id,
                        "tipo_chunk": "pagina",
                        "tema": "upload",
                        "idioma": "pt"
                    }
                    if ano_opcional:
                        meta["ano"] = int(ano_opcional)
                    
                    chunks.append({"id": chunk_id, "texto": texto, "metadados": meta})
        except Exception as e:
            st.warning(f"Não foi possível ler o arquivo {arquivo.name}.")
    
    if chunks:
        # Create a unique session id based on st.session_state (or just a random uuid, but here we can just use a fixed one per streamlit session if we want to replace it)
        sessao_id = st.session_state.get("sessao_id")
        if not sessao_id:
            sessao_id = str(uuid.uuid4())
            st.session_state.sessao_id = sessao_id
        
        try:
            indice_novo = criar_indice_sessao(emb_provider, sessao_id, chunks)
        except ErroProviderEmbeddingsOllama as erro:
            st.warning(str(erro))
            return
        except (ChromaError, ValueError):
            st.warning("Não foi possível criar o Índice de Sessão com os PDFs enviados.")
            return
        indice_anterior = st.session_state.get("indice_sessao")
        st.session_state.indice_sessao = indice_novo
        if indice_anterior:
            indice_anterior.descartar()
    else:
        st.warning("Os PDFs enviados não contêm texto extraível. OCR não faz parte deste webinário.")

def montar_filtro(ano_minimo, temas, idiomas):
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
    for indice, fonte in enumerate(fontes, start=1):
        referencia = fonte.get("posicao", indice)
        ano_texto = f" · {fonte.get('ano', '?')}" if "ano" in fonte else ""
        st.markdown(
            f"**[{referencia}]** — `{fonte.get('arquivo', '?')}`, p. {fonte.get('pagina', '?')} "
            f"· distância {fonte.get('distancia', 0.0):.4f}{ano_texto}"
        )
        st.text(fonte["texto"][:700])


def mostrar_fontes(busca):
    chunks = busca["chunks_recuperados"]
    citadas = busca["fontes_citadas"]
    if busca["status"] == "Resposta Parcial":
        st.warning("A geração foi interrompida antes da conclusão.")
    st.caption(f"Base Ativa: {busca['base_ativa']} · Classe: {busca['classe_fontes']}")
    if busca["classe_fontes"] == "recusa":
        return
    if citadas:
        with st.expander(f"Fontes Citadas ({len(citadas)})"):
            _mostrar_lista_fontes(citadas)
    elif chunks:
        with st.expander(f"Chunks Recuperados ({len(chunks)})"):
            _mostrar_lista_fontes(chunks)

st.title("📚 Assistente RAG sobre artigos de RAG")
st.caption("Migração OpenAI RAG — Híbrido com bge-m3 local e OpenAI (gpt-5.6-luna)")

with st.sidebar:
    st.header("Configuração")
    base_escolhida = st.radio("Base Ativa", ("Corpus Oficial", "Índice de Sessão"))
    if st.button("Limpar conversa"):
        st.session_state.mensagens = []
        indice_sessao = st.session_state.pop("indice_sessao", None)
        if indice_sessao:
            indice_sessao.descartar()
        st.session_state.pop("sessao_id", None)
        st.session_state.upload_widget_id = str(uuid.uuid4())
        st.rerun()
        
    k = st.slider("k (trechos no contexto)", 1, 10, config.K_PADRAO)
    
    st.subheader("Filtros de metadados (Corpus Oficial)")
    ano_minimo = st.slider("Ano mínimo", 2020, 2026, 2020)
    temas = st.multiselect("Tema", config.TEMAS)
    idiomas = st.multiselect("Idioma", config.IDIOMAS)
    
    st.subheader("Upload de PDFs (Índice de Sessão)")
    arquivos = st.file_uploader(
        "Até 3 PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        key=f"upload_pdfs_{st.session_state.get('upload_widget_id', 'inicial')}",
    )
    ano_opcional = st.number_input("Ano (opcional)", min_value=1900, max_value=2100, value=None)
    if st.button("Criar Índice de Sessão"):
        if arquivos:
            if len(arquivos) > 3:
                st.warning("Máximo de 3 PDFs permitidos.")
            else:
                processar_upload(arquivos[:3], ano_opcional)
        else:
            st.warning("Envie ao menos um arquivo.")
            
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

indice_sessao = st.session_state.get("indice_sessao")
if base_escolhida == "Índice de Sessão":
    base_ativa = indice_sessao.base_ativa if indice_sessao else None
    erro_base = "Crie um Índice de Sessão antes de selecioná-lo."
else:
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
            
        except ErroProviderOpenAI as erro:
            st.error(f"⚠️ {erro}")
            st.session_state.mensagens.pop()
        except ErroProviderEmbeddingsOllama as erro:
            st.error(f"⚠️ {erro}")
            st.session_state.mensagens.pop()
        except (ChromaError, ValueError):
            st.error("⚠️ Não foi possível consultar a Base Ativa. Confira a configuração e tente novamente.")
            st.session_state.mensagens.pop()
        except Exception:
            st.error("⚠️ Não foi possível concluir a resposta. Tente novamente.")
            st.session_state.mensagens.pop()
