import streamlit as st

from corpus import extrair_paginas, dividir_texto
from hybrid_index import abrir_colecao_hibrida
from ollama_embedding_provider import ProviderEmbeddingsOllama
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
    return ProviderEmbeddingsOllama(), ProviderOpenAI(secrets=st.secrets, environ=None)

@st.cache_resource
def base_oficial():
    try:
        from hybrid_index import abrir_colecao_hibrida
        return BaseAtiva("Corpus Oficial", abrir_colecao_hibrida())
    except Exception as e:
        return None

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
        import uuid
        sessao_id = st.session_state.get("sessao_id")
        if not sessao_id:
            sessao_id = str(uuid.uuid4())
            st.session_state.sessao_id = sessao_id
        
        st.session_state.base_sessao = criar_indice_sessao(emb_provider, sessao_id, chunks)

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

def mostrar_fontes(busca):
    fontes = busca["chunks_recuperados"]
    citadas = busca["fontes_citadas"]
    
    status_label = busca["status"]
    if status_label == "Resposta Parcial":
        st.warning("A geração foi interrompida antes da conclusão.")
    
    with st.expander(f"Fontes (citadas {len(citadas)} de {len(fontes)}) — Base Ativa: {busca['base_ativa']} - Classe: {busca['classe_fontes']}"):
        if not fontes:
            st.info("Nenhum trecho recuperado com esses filtros.")
        elif not citadas and busca["classe_fontes"] != "sem_resultados":
            st.info("Nenhuma fonte usada (Fallback recuperado).")
            
        for i, fonte in enumerate(fontes, start=1):
            marca = " ✅ citado" if fonte in citadas else ""
            ano_texto = f" · {fonte.get('ano', '?')}" if 'ano' in fonte else ""
            st.markdown(f"**[{i}]**{marca} — `{fonte.get('arquivo', '?')}`, p. {fonte.get('pagina', '?')} "
                        f"· distância {fonte.get('distancia', 0.0):.4f}{ano_texto}")
            st.text(fonte["texto"][:700])

st.title("📚 Assistente RAG sobre artigos de RAG")
st.caption("Migração OpenAI RAG — Híbrido com bge-m3 local e OpenAI (gpt-5.6-luna)")

with st.sidebar:
    st.header("Configuração")
    if st.button("Limpar conversa"):
        st.session_state.mensagens = []
        if "base_sessao" in st.session_state:
            del st.session_state.base_sessao
        st.rerun()
        
    k = st.slider("k (trechos no contexto)", 1, 10, config.K_PADRAO)
    
    st.subheader("Filtros de metadados (Corpus Oficial)")
    ano_minimo = st.slider("Ano mínimo", 2020, 2026, 2020)
    temas = st.multiselect("Tema", config.TEMAS)
    idiomas = st.multiselect("Idioma", config.IDIOMAS)
    
    st.subheader("Upload de PDFs (Índice de Sessão)")
    arquivos = st.file_uploader("Até 3 PDFs", type=["pdf"], accept_multiple_files=True)
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

base_ativa = st.session_state.get("base_sessao") or base_oficial()

if not base_ativa:
    st.error("Nenhuma Base Ativa disponível. Verifique a reindexação do Corpus Oficial ou faça upload.")
    st.stop()

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
        except Exception as e:
            st.error(f"⚠️ Erro inesperado: {e}")
            st.session_state.mensagens.pop()
