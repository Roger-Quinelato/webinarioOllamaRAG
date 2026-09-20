"""Sonda do eixo A4 (aplicacao Streamlit) — auditoria RODADA-1, so leitura.

Exercita casos de borda do app.py que ferramentas/testar_app.py nao cobre:
legenda "Caminho usado" apos rerender do historico, filtro que zera o resultado
(simples e dois estagios), Ollama que cai no meio da conversa, botao "Limpar
conversa", seletor de modelo com MODELO_CHAT alterado, e o _definir_slider()
usado por ferramentas/capturar_evidencias_e8.py.

Nao escreve nada no projeto. Nao reindexa. Nao executa o notebook.

Uso:
    .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/A4-sonda.py apptest
    .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/A4-sonda.py selectbox
    OLLAMA_HOST=http://localhost:1 ... A4-sonda.py ollama-off
    .venv/Scripts/python docs/auditoria/rodadas/RODADA-1/A4-sonda.py slider
"""
import os
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RAIZ))

TIMEOUT = 900
PERGUNTA_A = "O que o artigo Lost in the Middle descobriu sobre contextos longos?"
PERGUNTA_B = "Como o Ragas mede a fidelidade de uma resposta?"


def _novo_app():
    """Auxilia novo app."""
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=TIMEOUT)
    app.run()
    return app


def _slider(app, prefixo):
    """Auxilia slider."""
    return next(s for s in app.sidebar.slider if s.label.startswith(prefixo))


def _perguntar(app, texto):
    """Envia pergunta valor do fluxo."""
    inicio = time.perf_counter()
    app.chat_input[0].set_value(texto).run(timeout=TIMEOUT)
    return time.perf_counter() - inicio


def _legendas(app):
    """Auxilia legendas."""
    return [c.value for c in app.caption if c.value.startswith("Caminho usado")]


def _rotulos(app):
    """Auxilia rotulos."""
    return [e.label for e in app.expander]


def _dump(app, titulo):
    """Auxilia dump."""
    print(f"  [{titulo}] legendas 'Caminho usado' visiveis: {_legendas(app)}")
    print(f"  [{titulo}] expanders: {_rotulos(app)}")
    print(f"  [{titulo}] erros: {[e.value[:120] for e in app.error]} | avisos: {[w.value[:120] for w in app.warning]}")


def apptest():
    """Descreve AppTest."""
    import rag
    app = _novo_app()
    print("== A4-S1 carga inicial ==")
    print(f"  excecao={bool(app.exception)} avisos={[w.value for w in app.warning]}")
    print(f"  opcoes do seletor de modelo: {app.sidebar.selectbox[0].options}")

    print("\n== A4-S2 pergunta padrao (Simples, k=4, sem filtro) ==")
    d = _perguntar(app, PERGUNTA_A)
    m = app.session_state["mensagens"][-1]
    print(f"  respondida em {d:.0f}s | citadas={sorted(m['citadas'])} de {len(m['resultados'])}")
    print(f"  resposta[:160]={m['texto'][:160]!r}")
    _dump(app, "logo apos responder")

    print("\n== A4-S3 rerender do historico: mexe no slider k e roda de novo, sem perguntar ==")
    _slider(app, "k").set_value(5)
    app.run()
    _dump(app, "apos rerun")
    print(f"  mensagens no historico: {len(app.session_state['mensagens'])}")

    print("\n== A4-S4 filtro que zera o resultado (Ano minimo = 2026), modo Simples ==")
    _slider(app, "Ano").set_value(2026)
    app.run()
    d = _perguntar(app, PERGUNTA_B)
    m = app.session_state["mensagens"][-1]
    print(f"  respondida em {d:.0f}s | resultados={len(m['resultados'])} citadas={sorted(m['citadas'])}")
    print(f"  caminho={m['caminho']!r}")
    print(f"  resposta COMPLETA={m['texto']!r}")
    print(f"  eh_recusa={rag.eh_recusa(m['texto'])}")
    e = app.expander[-1]
    print(f"  rotulo do expander={e.label!r} | info={[i.value for i in e.info]}")

    print("\n== A4-S5 filtro que zera o resultado, modo Dois estagios ==")
    app.sidebar.radio[0].set_value("Dois estágios")
    app.run()
    d = _perguntar(app, PERGUNTA_B)
    m = app.session_state["mensagens"][-1]
    print(f"  respondida em {d:.0f}s | resultados={len(m['resultados'])} artigos={len(m['artigos'])}")
    print(f"  caminho={m['caminho']!r}")
    print(f"  resposta COMPLETA={m['texto']!r}")
    e = app.expander[-1]
    print(f"  rotulo do expander={e.label!r} | info={[i.value for i in e.info]}")

    print("\n== A4-S6 Ollama cai NO MEIO da conversa (cliente apontado para porta morta) ==")
    antes = len(app.session_state["mensagens"])
    import ollama
    rag._cliente = ollama.Client(host="http://localhost:1")
    try:
        _perguntar(app, PERGUNTA_A)
    finally:
        rag._cliente = None
    depois = len(app.session_state["mensagens"])
    print(f"  mensagens antes={antes} depois={depois} (pop() da pergunta do usuario)")
    print(f"  excecao nao tratada={bool(app.exception)}")
    print(f"  st.error={[e.value[:200] for e in app.error]}")
    print(f"  ultima mensagem do historico={app.session_state['mensagens'][-1]['texto'][:80]!r}")

    print("\n== A4-S7 botao 'Limpar conversa' ==")
    botao = next(b for b in app.sidebar.button if b.label == "Limpar conversa")
    botao.click().run()
    print(f"  mensagens apos clique: {len(app.session_state['mensagens'])}")
    print(f"  expanders apos clique: {_rotulos(app)}")
    print(f"  excecao={bool(app.exception)}")


def selectbox():
    """Roda com MODELO_CHAT=qwen2.5:3b, como o README:181 manda fazer."""
    app = _novo_app()
    sel = app.sidebar.selectbox[0]
    print(f"MODELO_CHAT={os.environ.get('MODELO_CHAT')!r}")
    print(f"opcoes do seletor: {sel.options}")
    print(f"valor selecionado: {sel.value!r}")
    print(f"opcoes distintas: {len(set(sel.options))} de {len(sel.options)}")
    print(f"excecao={bool(app.exception)}")


def ollama_off():
    """Roda com OLLAMA_HOST invalido: aviso na subida + erro ao perguntar."""
    app = _novo_app()
    print(f"OLLAMA_HOST={os.environ.get('OLLAMA_HOST')!r}")
    print(f"avisos na subida: {[w.value[:160] for w in app.warning]}")
    print(f"excecao na subida={bool(app.exception)}")
    app.chat_input[0].set_value(PERGUNTA_A).run(timeout=120)
    print(f"st.error ao perguntar: {[e.value[:200] for e in app.error]}")
    print(f"excecao nao tratada={bool(app.exception)}")
    print(f"mensagens no historico: {len(app.session_state['mensagens'])}")


def slider():
    """Reproduz o _definir_slider() de ferramentas/capturar_evidencias_e8.py num app real."""
    sys.path.insert(0, str(RAIZ / "ferramentas"))
    from playwright.sync_api import sync_playwright

    from capturar_app import subir_app
    from capturar_evidencias_e8 import _definir_slider, _esperar_resposta, _perguntar

    processo, url = subir_app()
    try:
        with sync_playwright() as p:
            navegador = p.chromium.launch(channel="msedge")
            pagina = navegador.new_page(viewport={"width": 1440, "height": 900})
            pagina.goto(url)
            pagina.wait_for_selector("text=Assistente RAG", timeout=60000)
            for alvo in (6, 2):
                _definir_slider(pagina, "k (trechos no contexto)", alvo)
                pagina.wait_for_timeout(1000)
                visual = pagina.evaluate(
                    """() => Array.from(document.querySelectorAll('input[type=range]'))
                        .find(s => s.getAttribute('aria-label') === 'k (trechos no contexto)').value"""
                )
                antes = _perguntar(pagina, PERGUNTA_A)
                _esperar_resposta(pagina, antes)
                legenda = pagina.evaluate(
                    """() => { const n = Array.from(document.querySelectorAll('*'))
                        .filter(e => e.children.length === 0 && e.textContent.startsWith('Caminho usado'));
                        return n.length ? n[n.length - 1].textContent : '(nenhuma)'; }"""
                )
                rotulo = pagina.evaluate(
                    """() => { const n = Array.from(document.querySelectorAll('*'))
                        .filter(e => e.children.length === 0 && e.textContent.includes('Fontes (citadas'));
                        return n.length ? n[n.length - 1].textContent : '(nenhum)'; }"""
                )
                print(f"  _definir_slider({alvo}) -> slider no DOM={visual!r}")
                print(f"    legenda da resposta = {legenda!r}")
                print(f"    rotulo do expander  = {rotulo!r}")
            navegador.close()
    finally:
        processo.terminate()
        processo.wait(timeout=10)


if __name__ == "__main__":
    {"apptest": apptest, "selectbox": selectbox,
     "ollama-off": ollama_off, "slider": slider}[sys.argv[1]]()
