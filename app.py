import streamlit as st

import config
import rag

st.set_page_config(page_title="Assistente RAG — CIIA", page_icon="📚", layout="wide")


@st.cache_resource
def colecao():
    return rag.abrir_colecao()


def montar_filtro(ano_minimo, temas, idiomas):
    condicoes = [{"ano": {"$gte": ano_minimo}}]
    if temas:
        condicoes.append({"tema": {"$in": temas}})
    if idiomas:
        condicoes.append({"idioma": {"$in": idiomas}})
    return rag.combinar_filtros(*condicoes)


def mostrar_fontes(fontes, caminho, artigos):
    with st.expander(f"Fontes ({len(fontes)}) — {caminho}"):
        if artigos:
            st.markdown("**Estágio 1 — artigos escolhidos pelos resumos:** "
                        + ", ".join(f"`{a['arquivo']}`" for a in artigos))
        if not fontes:
            st.info("Nenhum trecho recuperado com esses filtros.")
        for i, fonte in enumerate(fontes, start=1):
            st.markdown(f"**[{i}] {fonte['titulo']}** — `{fonte['arquivo']}`, p. {fonte['pagina']} "
                        f"· distância {fonte['distancia']:.4f} · {fonte['ano']} · {fonte['tema']} · {fonte['idioma']}")
            st.caption(f"Resumo do artigo: {fonte['resumo']}")
            st.text(fonte["texto"][:700])


st.title("📚 Assistente RAG sobre artigos de RAG")
st.caption("Webinário CIIA — Encontro 2 · Ollama + ChromaDB + Streamlit")

with st.sidebar:
    st.header("Configuração")
    modelo = st.selectbox("Modelo de chat", [config.MODELO_CHAT, config.MODELO_CHAT_PLANO_B])
    modo = st.radio("Busca", ["Simples", "Dois estágios"], horizontal=True)
    k = st.slider("k (trechos no contexto)", 1, 10, config.K_PADRAO)
    st.subheader("Filtros de metadados")
    ano_minimo = st.slider("Ano mínimo", 2020, 2026, 2020)
    temas = st.multiselect("Tema", config.TEMAS)
    idiomas = st.multiselect("Idioma", config.IDIOMAS)
    if st.button("Limpar conversa"):
        st.session_state.mensagens = []

try:
    _, faltando = rag.verificar_ollama([config.MODELO_EMBEDDING, modelo])
    if faltando:
        st.warning("Modelos não encontrados no Ollama: " + ", ".join(faltando)
                   + ". Rode `ollama pull <modelo>` no terminal.")
except rag.OllamaIndisponivel as erro:
    st.warning(f"⚠️ {erro}")

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

for mensagem in st.session_state.mensagens:
    with st.chat_message(mensagem["papel"]):
        st.markdown(mensagem["texto"])
        if mensagem["papel"] == "assistant":
            mostrar_fontes(mensagem["fontes"], mensagem["caminho"], mensagem["artigos"])

pergunta = st.chat_input("Pergunte algo sobre os artigos…")
if pergunta:
    st.session_state.mensagens.append({"papel": "user", "texto": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)
    with st.chat_message("assistant"):
        try:
            filtro = montar_filtro(ano_minimo, temas, idiomas)
            if modo == "Dois estágios":
                busca = rag.buscar_dois_estagios(pergunta, k=k, where=filtro, colecao=colecao())
            else:
                busca = {"caminho": "busca simples", "artigos": [],
                         "resultados": rag.buscar(pergunta, k=k, where=filtro, colecao=colecao())}
            st.caption(f"Caminho usado: {busca['caminho']} · k = {k} · modelo {modelo}")
            resposta = st.write_stream(
                rag.responder(pergunta, busca["resultados"], modelo=modelo, incluir_fontes=False)
            )
            mostrar_fontes(busca["resultados"], busca["caminho"], busca["artigos"])
            st.session_state.mensagens.append({
                "papel": "assistant", "texto": resposta, "fontes": busca["resultados"],
                "caminho": busca["caminho"], "artigos": busca["artigos"],
            })
        except rag.OllamaIndisponivel as erro:
            st.error(f"⚠️ {erro}")
            st.session_state.mensagens.pop()
