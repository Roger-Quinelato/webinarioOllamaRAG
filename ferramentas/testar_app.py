import sys
import time
from pathlib import Path

from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))


def rotulos_expanders(app):
    return [e.label for e in app.expander]


def perguntar(app, texto, timeout=900):
    inicio = time.perf_counter()
    app.chat_input[0].set_value(texto).run(timeout=timeout)
    return time.perf_counter() - inicio


app = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=900)
app.run()
print(f"8.1 app carregou sem exceção: {not app.exception} | avisos: {[w.value for w in app.warning]}")

slider_k = next(s for s in app.sidebar.slider if s.label.startswith("k"))
slider_k.set_value(2)
app.run()
duracao = perguntar(app, "Como o Ragas avalia a fidelidade de uma resposta?")
mensagens = app.session_state["mensagens"]
print(f"\n8.2 pergunta 1 respondida em {duracao:.0f}s | exceção: {bool(app.exception)} | erros: {[e.value for e in app.error]}")
print(f"    resposta: {mensagens[-1]['texto'][:300]!r}")
print(f"    legendas: {[c.value for c in app.caption if c.value.startswith('Caminho')]}")
print(f"8.4 k=2 → expanders: {rotulos_expanders(app)} | fontes na sessão: {len(mensagens[-1]['resultados'])} "
      f"| citadas: {sorted(mensagens[-1]['citadas'])}")

slider_k = next(s for s in app.sidebar.slider if s.label.startswith("k"))
slider_k.set_value(5)
app.sidebar.radio[0].set_value("Dois estágios")
app.sidebar.multiselect[0].set_value(["avaliacao", "limitacoes"])
app.run()
duracao = perguntar(app, "Quais problemas aparecem quando o contexto é muito longo?")
mensagens = app.session_state["mensagens"]
ultima = mensagens[-1]
print(f"\n8.3 histórico após 2 perguntas: {len(mensagens)} mensagens → papéis {[m['papel'] for m in mensagens]}")
print(f"    pergunta 2 respondida em {duracao:.0f}s | resposta: {ultima['texto'][:300]!r}")
print(f"8.4 k=5 → fontes na última resposta: {len(ultima['resultados'])} | citadas: {sorted(ultima['citadas'])} "
      f"| expanders: {rotulos_expanders(app)}")
print(f"8.5 filtro tema ∈ [avaliacao, limitacoes] → temas das fontes: {sorted({f['tema'] for f in ultima['resultados']})}")
print(f"8.6 caminho usado: {ultima['caminho']!r} | artigos do estágio 1: {[a['arquivo'] for a in ultima['artigos']]}")
expander = app.expander[-1]
print(f"8.7/T04 rótulo do último expander: {expander.label!r}")
print(f"T04 trechos citados marcados '✅ citado': "
      f"{[m.value.split('**')[1] for m in expander.markdown if '✅ citado' in m.value]}")
print("8.7 conteúdo do último expander:")
for rotulo, elementos in (("markdown", expander.markdown), ("caption (resumo)", expander.caption),
                          ("text (trecho)", expander.text)):
    for elemento in list(elementos)[:2]:
        print(f"    [{rotulo}] {elemento.value[:220]}")
app.sidebar.radio[0].set_value("Simples")
app.sidebar.multiselect[0].set_value([])
app.run()
duracao = perguntar(app, "Qual é a receita de pão de queijo mineiro?")
mensagens = app.session_state["mensagens"]
ultima = mensagens[-1]
expander = app.expander[-1]
print(f"\nT04 recusa ({duracao:.0f}s): resposta={ultima['texto'][:120]!r} | citadas={sorted(ultima['citadas'])} "
      f"| rótulo do expander={expander.label!r} "
      f"| avisos 'Nenhuma fonte usada': {[i.value for i in expander.info if 'Nenhuma fonte usada' in i.value]}")

print(f"\nexceções finais: {[str(e.value)[:200] for e in app.exception] or 'nenhuma'}")
