"""Fonte dos slides da aula prática de RAG (issue #136): gera os arquivos do deck no formato do tipo "Slides".

Conteúdo: derivado de aula 28-09/aula_rag_colab.ipynb (cada slide aponta a seção do notebook).
Identidade visual: extraída de docs/slides/parte1-rag-python-puro.pdf — paleta com os hex exatos abaixo,
Cambria/Calibri/Courier New substituídas pelas equivalentes web de mesma métrica (Caladea/Carlito/Cousine),
canvas 1920×1080 (o PDF é 960×540 pt → escala 2×).

Uso:
    python "aula 28-09/gerar_deck_aula.py"      # escreve aula 28-09/deck_aula/project/{deck.json,slides/*.html}

O deck publicado vive como Artifact no claude.ai; para atualizá-lo, republique os arquivos de
aula 28-09/deck_aula/project/ no mesmo Artifact (ver aula 28-09/README.md).
"""
import json
import datetime
from html import escape as e
from pathlib import Path

RAIZ = Path(__file__).with_name("deck_aula")
(RAIZ / "project" / "slides").mkdir(parents=True, exist_ok=True)

# ── Paleta (hex exatos extraídos do PDF anterior) ─────────────────────────────
# navy #16202E capa, cabeçalho de tabela, faixas · navy-deep #0F1722 código · navy-2 #22304A cards no escuro
# ink #1D2530 texto · muted #5B6675 legendas e rodapé
# teal #1F8F7C / #E3F3F0  → etapa 1, preparar/indexar, local, certo
# amber #E09A2C / #FBF1E0 / #F2B84B → eyebrow, etapa 2, recuperar, números
# coral #C9503F / #F9E7E4 → etapa 3, gerar, erro, recusa
# card #EEF2F6 → card neutro e zebra de tabela · texto no escuro #E6EDF3 #B7C3CF #7FD1C0
NAVY, NAVY_DEEP, NAVY2 = "#16202E", "#0F1722", "#22304A"
INK, MUTED = "#1D2530", "#5B6675"
TEAL, TEAL_BG = "#1F8F7C", "#E3F3F0"
AMBER, AMBER_BG, AMBER_LIGHT = "#E09A2C", "#FBF1E0", "#F2B84B"
CORAL, CORAL_BG = "#C9503F", "#F9E7E4"
CARD, WHITE = "#EEF2F6", "#FFFFFF"
ON_DARK, ON_DARK2, MINT = "#E6EDF3", "#B7C3CF", "#7FD1C0"

F_TIT = "Caladea, Cambria, Georgia, serif"
F_TXT = "Carlito, Calibri, Arial, sans-serif"
F_MONO = "Cousine, 'Courier New', monospace"
TOTAL = 27

slides = []  # (id, html)


# ── Blocos reutilizáveis ───────────────────────────────────────────────────────
def eyebrow(texto, cor=AMBER):
    return (f'<p style="font-size:24px; font-weight:700; letter-spacing:5px; text-transform:uppercase; '
            f'color:{cor}">{texto}</p>')


def titulo(texto, cor=NAVY, tam=60):
    return (f'<h2 style="font-family:{F_TIT}; font-size:{tam}px; font-weight:700; line-height:1.1; '
            f'color:{cor}">{texto}</h2>')


def lead(texto, cor=INK, tam=28):
    return f'<p style="font-size:{tam}px; line-height:1.4; color:{cor}">{texto}</p>'


def p(texto, tam=24, cor=INK, extra=""):
    return f'<p style="font-size:{tam}px; line-height:1.4; color:{cor}{extra}">{texto}</p>'


def h3(texto, cor=NAVY, tam=32):
    return f'<h3 style="font-family:{F_TIT}; font-size:{tam}px; font-weight:700; line-height:1.15; color:{cor}">{texto}</h3>'


def circulo(n, cor, tam=56, fonte=28, texto_cor=WHITE):
    return (f'<div style="width:{tam}px; height:{tam}px; border-radius:50%; background:{cor}; display:flex; '
            f'align-items:center; justify-content:center; flex:none"><p style="font-family:{F_TIT}; '
            f'font-size:{fonte}px; font-weight:700; color:{texto_cor}; line-height:1">{n}</p></div>')


def lista(itens, tam=24, cor=INK):
    lis = "".join(f"<li>{i}</li>" for i in itens)
    return f'<ul style="font-size:{tam}px; line-height:1.4; color:{cor}">{lis}</ul>'


def card(conteudo, bg=CARD, pad=32, gap=12, extra=""):
    return (f'<div style="flex:1; display:flex; flex-direction:column; gap:{gap}px; background:{bg}; '
            f'padding:{pad}px; border-radius:12px{extra}">{conteudo}</div>')


def linha(conteudo, gap=24, extra=""):
    return f'<div style="display:flex; gap:{gap}px{extra}">{conteudo}</div>'


def faixa(rotulo, texto, bg=NAVY, cor_rot=AMBER_LIGHT, cor=ON_DARK):
    return (f'<div style="background:{bg}; padding:24px 32px; border-radius:12px">'
            f'<p style="font-size:26px; line-height:1.4; color:{cor}"><b><span style="color:{cor_rot}">{rotulo}</span></b> {texto}</p></div>')


def codigo(texto, tam=24):
    linhas = "<br>".join(e(l).replace("  ", "&#160;&#160;") for l in texto.strip("\n").split("\n"))
    return (f'<div style="background:{NAVY_DEEP}; padding:32px; border-radius:12px; flex:1">'
            f'<p style="font-family:{F_MONO}; font-size:{tam}px; line-height:1.5; color:{ON_DARK}">{linhas}</p></div>')


def tabela(cab, linhas_, larguras, tam=24, primeira_negrito=True):
    th = "".join(f'<th style="width:{w}%; padding:12px 16px; color:{WHITE}; font-weight:700; text-align:left">{c}</th>'
                 for c, w in zip(cab, larguras))
    corpo = ""
    for i, l in enumerate(linhas_):
        bg = CARD if i % 2 else WHITE
        tds = "".join(
            f'<td style="padding:12px 16px">{("<b>" + c + "</b>") if (j == 0 and primeira_negrito) else c}</td>'
            for j, c in enumerate(l))
        corpo += f'<tr style="background:{bg}">{tds}</tr>'
    return (f'<table style="width:1728px; font-size:{tam}px; color:{INK}; font-family:{F_TXT}">'
            f'<tr style="background:{NAVY}">{th}</tr>{corpo}</table>')


def secao(id_, n, corpo, notebook=None, notas="", escuro=False, pad="64px 96px 120px", gap=24,
          transicao="fade"):
    bg = NAVY if escuro else WHITE
    cor = ON_DARK if escuro else INK
    rodape = ""
    if not escuro:
        rodape = (f'<p style="position:absolute; left:96px; bottom:40px; width:1000px; font-size:24px; color:{MUTED}">'
                  f'Aula prática de RAG · Webinário CIIA</p>'
                  f'<p style="position:absolute; right:96px; bottom:40px; width:200px; font-size:24px; color:{MUTED}; '
                  f'text-align:right">{n} / {TOTAL}</p>')
    pilula = ""
    if notebook:
        cor_pil, bg_pil = (MINT, NAVY2) if escuro else (TEAL, TEAL_BG)
        pilula = (f'<p style="position:absolute; right:96px; top:56px; width:340px; font-size:24px; font-weight:700; '
                  f'color:{cor_pil}; background:{bg_pil}; padding:6px 20px; border-radius:999px; text-align:center">'
                  f'Notebook · {notebook}</p>')
    aside = f"<aside>{e(notas)}</aside>" if notas else ""
    html = (f'<section id="{id_}" data-transition="{transicao}" style="background:{bg}; color:{cor}; '
            f'font-family:{F_TXT}; padding:{pad}; display:flex; flex-direction:column; gap:{gap}px">'
            f'{corpo}{pilula}{rodape}{aside}</section>')
    slides.append((id_, html))


def seta(cor=MUTED, tam=40):
    return f'<p style="font-size:{tam}px; font-weight:700; color:{cor}; line-height:1; align-self:center">→</p>'


def caixa(titulo_, sub="", bg=WHITE, borda=CARD, cor=NAVY, largura=None):
    w = f"width:{largura}px; flex:none" if largura else "flex:1"
    s = f'<p style="font-size:24px; color:{MUTED}; line-height:1.3">{sub}</p>' if sub else ""
    return (f'<div style="{w}; background:{bg}; border:2px solid {borda}; border-radius:10px; padding:18px 16px; '
            f'display:flex; flex-direction:column; gap:4px; align-items:center">'
            f'<p style="font-size:26px; font-weight:700; color:{cor}; line-height:1.2; text-align:center">{titulo_}</p>{s}</div>')


# ═════════════════════════════════════════════════════════════════════════════
# 1. Capa
# ═════════════════════════════════════════════════════════════════════════════
def kpi(num, legenda):
    return (f'<div style="background:{NAVY2}; border-radius:12px; padding:32px 24px; display:flex; flex-direction:column; '
            f'align-items:center; gap:8px"><p style="font-family:{F_TIT}; font-size:96px; font-weight:700; color:{AMBER}; '
            f'line-height:1">{num}</p><p style="font-size:26px; color:{ON_DARK2}; text-align:center; line-height:1.3">{legenda}</p></div>')


secao("capa", 1, (
    '<div style="display:flex; gap:64px; flex:1; align-items:center">'
    '<div style="flex:1; display:flex; flex-direction:column; gap:36px">'
    + eyebrow("Webinário CIIA · Aula prática")
    + f'<h1 style="font-family:{F_TIT}; font-size:88px; font-weight:700; line-height:1.08; color:{WHITE}">RAG na prática: do documento à resposta com fonte</h1>'
    + lead("O que é RAG, por que ele existe e como cada etapa funciona — preparando você para montar um RAG "
           "completo no Google Colab, sem chave de API e sem instalar nada.", cor="#C9D3DE", tam=30)
    + '</div>'
    '<div style="width:720px; flex:none; display:grid; grid-template-columns:1fr 1fr; gap:24px">'
    + kpi("1", "notebook no Google Colab") + kpi("0", "chaves de API ou cadastros")
    + kpi("1", "GPU T4 gratuita do Colab") + kpi("10", "etapas, do documento à fonte")
    + '</div></div>'
    + p("Material: slides (teoria) + notebook aula_rag_colab.ipynb (prática) · Python · pypdf · "
        "sentence-transformers · Chroma · transformers · Qwen3", cor=ON_DARK2)
), escuro=True, pad="96px 96px 72px", notas=(
    "Abertura. A aula tem duas partes: estes slides apresentam cada conceito; o notebook no Colab põe cada "
    "conceito para rodar, uma célula por ideia. Nada de chave de API: tudo roda na GPU do próprio Colab."))

# ═════════════════════════════════════════════════════════════════════════════
# 2. Objetivos
# ═════════════════════════════════════════════════════════════════════════════
OBJ = [
    ("Explicar o que é RAG e que problema ele resolve", TEAL),
    ("Ler um PDF e ver o texto extraído de cada página", TEAL),
    ("Dividir o texto em chunks com sobreposição", TEAL),
    ("Transformar texto em embedding e interpretar similaridade", TEAL),
    ("Criar um banco vetorial e saber o que ele guarda", TEAL),
    ("Buscar por significado e ler trecho, página e nota", AMBER),
    ("Montar o prompt e ler o que o modelo recebe", AMBER),
    ("Rodar um LLM na GPU do Colab e ver a memória usada", CORAL),
    ("Ligar cada [n] da resposta ao arquivo e à página", CORAL),
    ("Reconhecer limites: recusa, extração, chunk e alucinação", NAVY),
]


def objetivo(i, texto, cor):
    return (f'<div style="display:flex; gap:20px; align-items:center; background:{CARD}; border-radius:10px; '
            f'padding:14px 20px">{circulo(i, cor, 48, 24)}<p style="font-size:26px; line-height:1.3; color:{INK}">{texto}</p></div>')


col1 = "".join(objetivo(i + 1, t, c) for i, (t, c) in enumerate(OBJ[:5]))
col2 = "".join(objetivo(i + 6, t, c) for i, (t, c) in enumerate(OBJ[5:]))
secao("objetivos", 2, (
    eyebrow("Objetivos") + titulo("O que você vai aprender hoje")
    + lead("Ao final dos slides e do notebook, você consegue:")
    + linha(f'<div style="flex:1; display:flex; flex-direction:column; gap:14px">{col1}</div>'
            f'<div style="flex:1; display:flex; flex-direction:column; gap:14px">{col2}</div>')
    + faixa("Roteiro:", "teoria nos slides (cada conceito explicado com exemplo) → prática no notebook (cada "
            "conceito vira uma célula que você roda e observa).")
), notebook="§0", notas=(
    "Estes dez resultados são o contrato da aula. As cores seguem as fases: teal = preparar o material, "
    "âmbar = recuperar, coral = gerar, navy = senso crítico."))

# ═════════════════════════════════════════════════════════════════════════════
# 3. O que um LLM sabe
# ═════════════════════════════════════════════════════════════════════════════
def card_num(n, cor, tit, texto, bg=CARD, sub=""):
    s = f'<p style="font-size:24px; font-style:italic; color:{MUTED}">{sub}</p>' if sub else ""
    return card(linha(circulo(n, cor) + f'<div style="display:flex; flex-direction:column; gap:2px">{h3(tit)}{s}</div>',
                      gap=20, extra="; align-items:center") + texto, bg=bg)


secao("llm-sabe", 3, (
    eyebrow("O problema") + titulo("O que um LLM sabe — e o que ele não sabe")
    + lead("Um <b>modelo de linguagem</b> (LLM) aprendeu a escrever lendo uma quantidade enorme de textos. Esse "
           "conhecimento fica guardado nos seus parâmetros — e tem três limites:")
    + linha(
        card_num(1, TEAL, "Tem data de corte", p("Aprendeu com textos até uma data. O que veio depois — um artigo, "
                                                  "uma norma, um relatório — ele não viu."))
        + card_num(2, AMBER, "Não leu os seus arquivos", p("Documentos internos, contratos, apostilas e PDFs "
                                                            "privados nunca fizeram parte do treino."))
        + card_num(3, CORAL, "Não mostra a fonte", p("A resposta sai da “memória” do modelo, sem página nem "
                                                      "documento para você conferir.")))
    + faixa("Alucinação:", "quando não sabe, o modelo pode <b>inventar</b> uma resposta fluente e convincente. Sem "
            "fonte, você não consegue distinguir o acerto do chute.", bg=CORAL_BG, cor_rot=CORAL, cor=INK)
    + p("<b>Analogia:</b> um especialista brilhante que ficou anos isolado, sem internet. Pergunte sobre um relatório de "
        "ontem: ou ele admite que não leu, ou dá um palpite convincente.", cor=MUTED)
), notebook="§2", notas=(
    "No notebook (seção 2) o aluno pergunta ao modelo sobre um artigo de 2025 que ele nunca leu e observa a "
    "resposta sem fonte. Essa resposta volta na seção 12 para comparação."))

# ═════════════════════════════════════════════════════════════════════════════
# 4. LLM sozinho × LLM + recuperação
# ═════════════════════════════════════════════════════════════════════════════
def painel(bg, cor, tit, itens, exemplo, fonte_ex):
    return card(h3(tit, cor=cor) + lista(itens, tam=26)
                + f'<div style="background:{WHITE}; border-radius:10px; padding:20px 24px; display:flex; flex-direction:column; gap:6px">'
                + p(exemplo, tam=26, extra="; font-style:italic") + p(fonte_ex, cor=cor, extra="; font-weight:700") + "</div>",
                bg=bg, gap=16)


secao("sozinho-vs-rag", 4, (
    eyebrow("A ideia central") + titulo("LLM sozinho × LLM + recuperação")
    + lead("Mesma pergunta, mesmo modelo: <i>“Quais modelos tiveram o melhor desempenho no estudo de Medeiros e "
           "Oliveira (2025)?”</i>")
    + linha(
        painel(CORAL_BG, CORAL, "LLM sozinho: prova de memória",
               ["Responde com o que lembra do treino", "Pode dizer que não sabe — ou inventar nomes plausíveis",
                "Nenhuma fonte para conferir"],
               "“Provavelmente modelos como BERT e GPT-3…”", "Sem fonte")
        + painel(TEAL_BG, TEAL, "LLM + RAG: prova com consulta",
                 ["Antes de responder, busca os trechos certos do documento", "Lê os trechos e responde a partir deles",
                  "Cita [1], [2]… que levam ao arquivo e à página"],
                 "“O Multilingual E5 large e o Gemma 2 9B tiveram o melhor desempenho [1].”",
                 "[1] → artigo de exemplo, p. 1 (resumo)"))
    + faixa("RAG =", "<i>Retrieval-Augmented Generation</i>, Geração Aumentada por Recuperação: <b>recuperar</b> "
            "trechos relevantes para <b>aumentar</b> o prompt antes da <b>geração</b>.")
), notebook="§2 · §12", notas=(
    "A resposta do lado direito vem do resumo do artigo de exemplo (Medeiros e Oliveira, SEMISH 2025). A do "
    "lado esquerdo é um exemplo típico de chute: o objetivo é mostrar a diferença de natureza, não citar uma "
    "resposta real do modelo."))

# ═════════════════════════════════════════════════════════════════════════════
# 5. RAG em um minuto
# ═════════════════════════════════════════════════════════════════════════════
def fase(n, cor, tit, sub, itens, ref):
    return card(linha(circulo(n, cor, 64, 32) + f'<div style="display:flex; flex-direction:column; gap:2px">{h3(tit, tam=36)}'
                      f'<p style="font-size:24px; font-style:italic; color:{MUTED}">{sub}</p></div>', gap=20,
                      extra="; align-items:center")
                + lista(itens, tam=26) + '<div style="flex:1"></div>'
                + f'<p style="font-family:{F_MONO}; font-size:24px; color:{MUTED}">{ref}</p>', gap=16)


secao("rag-minuto", 5, (
    eyebrow("Fundamentos") + titulo("RAG em um minuto: preparar, recuperar, gerar")
    + lead("Em vez de confiar no que o modelo memorizou, o sistema <b>busca</b> trechos relevantes nos seus documentos e "
           "entrega só esses trechos ao LLM, que <b>responde com base neles</b>.")
    + linha(
        fase(1, TEAL, "Preparar", "Uma vez, antes das perguntas",
             ["PDF → texto por página", "Texto → chunks de ~700 caracteres", "Chunk → vetor de 768 números",
              "Vetores + metadados → banco vetorial"], "notebook §3–§6")
        + fase(2, AMBER, "Recuperar", "A cada pergunta",
               ["Pergunta → vetor, com o mesmo modelo", "O banco devolve os k chunks mais próximos",
                "Cada trecho vem com arquivo e página"], "notebook §7")
        + fase(3, CORAL, "Gerar", "A cada pergunta, na GPU",
               ["O LLM recebe regras + trechos numerados + pergunta", "Responde citando [1], [2]…",
                "Sem evidência: recusa com frase fixa"], "notebook §8–§11"), extra="; flex:1")
    + p("<b>Por que não perguntar direto ao LLM?</b> Conhecimento atualizado sem retreinar o modelo · resposta "
        "rastreável até o arquivo e a página · recusa explícita quando não há evidência.", tam=26)
), notebook="§0", notas="Modelo mental da aula inteira. Cada fase tem uma cor que se repete em todos os slides.")

# ═════════════════════════════════════════════════════════════════════════════
# 6. O caminho completo
# ═════════════════════════════════════════════════════════════════════════════
def zona(rotulo, cor, bg, caixas):
    return (f'<div style="background:{bg}; border-radius:12px; padding:24px 28px; display:flex; flex-direction:column; gap:16px">'
            f'<p style="font-size:24px; font-weight:700; letter-spacing:4px; text-transform:uppercase; color:{cor}">{rotulo}</p>'
            f'<div style="display:flex; gap:12px; align-items:stretch">{caixas}</div></div>')


prep = seta(TEAL).join([caixa("Documento", "§3 texto por página"), caixa("Chunks", "§4 pedaços"),
                        caixa("Embeddings", "§5 vetores"), caixa("Banco vetorial", "§6 coleção")])
resp = seta(AMBER).join([caixa("Pergunta", "sua dúvida"), caixa("Retrieval", "§7 top-k"), caixa("Contexto", "§8 [1] [2]…"),
                         caixa("Prompt", "§9 regras"), caixa("LLM", "§10 na GPU"), caixa("Resposta", "§11 com fonte",
                                                                                        borda=CORAL, cor=CORAL)])
secao("caminho", 6, (
    eyebrow("Mapa da aula") + titulo("O caminho completo, etapa por etapa")
    + zona("Preparar o material · uma vez", TEAL, TEAL_BG, prep)
    + f'<p style="font-size:26px; color:{MUTED}; text-align:center">↓ &#160;o banco vetorial é consultado a cada pergunta&#160; ↓</p>'
    + zona("Responder · a cada pergunta", AMBER, AMBER_BG, resp)
    + linha(card(p("<b>§1</b> prepara o Colab e a GPU · <b>§2</b> mostra o problema (LLM sozinho)"), pad=20)
            + card(p("<b>§12</b> compara com e sem RAG · <b>§13</b> junta tudo · <b>§14</b> limites e glossário"), pad=20))
    + p("Cada caixa é uma seção do notebook — e cada seção termina com um resultado que você vê: texto, pedaços, "
        "vetores, registros, trechos, prompt, resposta e fontes.", tam=26)
), notebook="§13", notas="Use este slide como índice: toda vez que o notebook abrir uma seção, volte a esta figura.")

# ═════════════════════════════════════════════════════════════════════════════
# 7. Documentos
# ═════════════════════════════════════════════════════════════════════════════
registro = tabela(["Campo", "Exemplo"], [["arquivo", "artigo.pdf"], ["pagina", "3"],
                                         ["texto", "“Os resultados mostram que…”"]], [35, 65], tam=26)
secao("documentos", 7, (
    eyebrow("Documentos") + titulo("Documentos: do PDF ao texto com endereço")
    + lead("Um PDF guarda <b>desenhos de letras</b> em posições da página. Para usar o conteúdo, <b>extraímos</b> o "
           "texto página por página — e anotamos de onde cada página veio.")
    + linha(
        '<div style="flex:1; display:flex; flex-direction:column; gap:20px">'
        + card(h3("PDF é desenho, não texto") + p("Colunas, tabelas e rodapés podem sair embaralhados. Se o texto "
                                                  "extraído estiver ruim, nenhuma etapa seguinte conserta: <b>olhe o "
                                                  "texto primeiro</b>.", tam=26))
        + card(h3("PDF escaneado = sem texto", cor=CORAL) + p("Se a página é uma foto, não há letras para extrair. "
                                                             "Seria preciso OCR, que fica fora desta aula.", tam=26),
               bg=CORAL_BG)
        + "</div>"
        + '<div style="flex:1; display:flex; flex-direction:column; gap:20px">'
        + h3("Um registro por página") + registro.replace("width:1728px", "width:820px")
        + card(p("<b>Metadados</b> = informações <i>sobre</i> o texto (arquivo, página). São eles que permitem "
                 "<b>citar a fonte</b> no fim.", tam=26, cor=INK), bg=TEAL_BG)
        + "</div>", gap=32)
    + p("<b>Analogia:</b> tirar uma cópia de cada página e anotar no canto: <i>livro X, página 3</i>.", cor=MUTED, tam=26)
), notebook="§3", notas="Formatos aceitos no notebook: PDF, TXT e MD. O exemplo padrão é um artigo em português.")

# ═════════════════════════════════════════════════════════════════════════════
# 8. Chunk
# ═════════════════════════════════════════════════════════════════════════════
secao("chunk", 8, (
    eyebrow("Chunking") + titulo("Chunk: por que cortar o texto em pedaços")
    + lead("Não entregamos o documento inteiro ao modelo: cortamos o texto em pedaços menores, os <b>chunks</b> — como "
           "fichas de estudo, cada uma sobre um trecho.")
    + linha(card_num(1, TEAL, "Busca mais precisa", p("Um pedaço pequeno fala de um assunto só: fica fácil saber se "
                                                        "ele combina com a pergunta.", tam=26))
            + card_num(2, AMBER, "Cabe no modelo", p("O modelo lê uma quantidade limitada de texto por vez: mandamos "
                                                      "só os pedaços relevantes.", tam=26))
            + card_num(3, CORAL, "Citação exata", p("Dá para apontar o trecho — e a página — que sustenta cada "
                                                     "afirmação.", tam=26)))
    + tabela(["", "Pequeno (~300)", "Médio (~700, o da aula)", "Grande (~2000)"],
             [["Busca", "precisa", "equilibrada", "genérica, mistura assuntos"],
              ["Contexto para o modelo", "pode faltar informação", "suficiente", "traz mais ruído"],
              ["Citação", "trecho curto", "um parágrafo", "trecho longo"]], [28, 22, 26, 24], tam=26)
), notebook="§4", notas="Não existe tamanho ideal universal. No notebook o aluno muda TAMANHO_CHUNK e vê o efeito.")

# ═════════════════════════════════════════════════════════════════════════════
# 9. Sobreposição
# ═════════════════════════════════════════════════════════════════════════════
def bloco(texto, bg, borda=None, w=None):
    b = f"; border:2px dashed {borda}" if borda else ""
    return (f'<div style="width:{w}px; flex:none; background:{bg}; padding:16px 20px; border-radius:8px{b}">'
            f'<p style="font-size:24px; line-height:1.35; color:{INK}">{texto}</p></div>')


faixa1 = linha(bloco("<b>chunk 1</b> · …os modelos foram avaliados com três bases de dados", TEAL_BG, w=820)
               + bloco("<b>em português. Os melhores resultados</b>", AMBER_BG, AMBER, 420), gap=0)
faixa2 = linha('<div style="width:820px; flex:none"></div>'
               + bloco("<b>em português. Os melhores resultados</b>", AMBER_BG, AMBER, 420)
               + bloco("<b>chunk 2</b> · foram obtidos com…", CARD, w=488), gap=0)


def pilula(texto, bg, cor=WHITE):
    return (f'<p style="font-family:{F_MONO}; font-size:26px; font-weight:700; color:{cor}; background:{bg}; '
            f'padding:10px 20px; border-radius:8px">{texto}</p>')


secao("sobreposicao", 9, (
    eyebrow("Chunking") + titulo("Tamanho e sobreposição: sem partir ideias ao meio")
    + lead("A <b>sobreposição</b> (<i>overlap</i>) repete o final de um chunk no começo do seguinte. Se uma frase "
           "importante cai na divisa, ela aparece inteira em pelo menos um dos dois.")
    + f'<div style="display:flex; flex-direction:column; gap:12px">{faixa1}{faixa2}</div>'
    + p("Em âmbar tracejado: o trecho que aparece nos <b>dois</b> chunks.", cor=MUTED)
    + linha(
        card(h3("Tamanho: 700 caracteres") + p("Limite de cada pedaço. O cortador prefere quebrar entre parágrafos → "
                                               "linhas → frases → palavras.", tam=26))
        + card(h3("Sobreposição: 150 caracteres") + p("Cerca de 20% repetidos entre vizinhos: nenhuma ideia fica "
                                                      "partida sem aparecer inteira em algum chunk.", tam=26))
        + card(h3("Endereço do chunk") + linha(pilula("artigo.pdf", NAVY) + pilula(":p3", AMBER) + pilula(":c1", TEAL),
                                               gap=6, extra="; flex-wrap:wrap")
               + p("arquivo · página 3 · 1º chunk da página", cor=MUTED)))
), notebook="§4", notas="No notebook, uma célula destaca a sobreposição real entre dois chunks do documento enviado.")

# ═════════════════════════════════════════════════════════════════════════════
# 10. Embedding
# ═════════════════════════════════════════════════════════════════════════════
def ponto(x, y, cor, rotulo, lx, ly, lw=300):
    return (f'<div style="position:absolute; left:{x}px; top:{y}px; width:26px; height:26px; border-radius:50%; background:{cor}"></div>'
            f'<p style="position:absolute; left:{lx}px; top:{ly}px; width:{lw}px; font-size:24px; font-weight:700; color:{INK}">{rotulo}</p>')


mapa = (f'<div style="position:relative; width:760px; height:440px; flex:none; background:{CARD}; border-radius:12px">'
        + ponto(150, 110, TEAL, "“gato dormindo”", 186, 104)
        + ponto(210, 180, TEAL, "“felino descansa”", 246, 174)
        + ponto(120, 250, TEAL, "“cat sleeping”", 156, 244)
        + ponto(560, 330, CORAL, "“taxa de juros”", 420, 370, 320)
        + f'<p style="position:absolute; left:24px; top:392px; width:380px; font-size:24px; color:{MUTED}">mapa ilustrativo</p>'
        + "</div>")
fluxo_emb = (
    '<div style="flex:1; display:flex; flex-direction:column; gap:16px">'
    + f'<div style="background:{WHITE}; border:2px solid {CARD}; border-radius:10px; padding:20px 24px">'
    + p("“O gato está dormindo no sofá.”", tam=28, extra="; font-style:italic") + "</div>"
    + p("↓ &#160;modelo de embedding (na GPU)", tam=26, cor=TEAL, extra="; font-weight:700")
    + f'<div style="background:{NAVY_DEEP}; border-radius:10px; padding:20px 24px">'
      f'<p style="font-family:{F_MONO}; font-size:26px; color:{ON_DARK}">[0.021, -0.043, 0.117, …]</p>'
      f'<p style="font-size:24px; color:{ON_DARK2}">um vetor: uma lista de 768 números</p></div>'
    + card(p("<b>Analogia:</b> como latitude e longitude. Brasília e Goiânia ficam perto no mapa porque suas "
             "coordenadas são parecidas. Aqui, as coordenadas são de <b>significado</b>.", tam=26), bg=TEAL_BG)
    + "</div>")
secao("embedding", 10, (
    eyebrow("Embeddings") + titulo("Embedding: transformar significado em coordenadas")
    + lead("Imagine que transformamos cada trecho de texto em uma <b>coordenada num espaço matemático</b>. Textos "
           "parecidos ficam próximos uns dos outros. Essa representação numérica é chamada de <b>embedding</b>.")
    + linha(fluxo_emb + mapa, gap=40)
), notebook="§5", notas="O mapa é ilustrativo: 768 dimensões desenhadas em 2. No notebook o aluno vê o formato (768,) e os primeiros números.")

# ═════════════════════════════════════════════════════════════════════════════
# 11. Similaridade
# ═════════════════════════════════════════════════════════════════════════════
def v(x, alto=0.6):
    cor = TEAL if x >= alto else (MUTED if x < 0.5 else INK)
    peso = "font-weight:700; " if x >= alto else ""
    return f'<span style="color:{cor}">{"<b>" if peso else ""}{x:.2f}{"</b>" if peso else ""}</span>'.replace(".", ",")


lab = ["gato dormindo", "felino descansa", "cat sleeping", "taxa de juros"]
M = [[1, .86, .81, .12], [.86, 1, .78, .10], [.81, .78, 1, .09], [.12, .10, .09, 1]]
sim_tab = tabela([""] + lab, [[lab[i]] + [v(M[i][j]) for j in range(4)] for i in range(4)], [24, 19, 19, 19, 19], tam=26)
secao("similaridade", 11, (
    eyebrow("Embeddings") + titulo("Parecido = perto: similaridade de cosseno")
    + lead("A proximidade entre dois vetores é medida pela <b>similaridade de cosseno</b>: perto de <b>1</b> = mesmo "
           "sentido; perto de <b>0</b> = sem relação.")
    + linha('<div style="width:1080px; flex:none; display:flex; flex-direction:column; gap:12px">'
            + sim_tab.replace("width:1728px", "width:1080px")
            + p("Valores ilustrativos. No notebook (§5) você calcula os de verdade.", cor=MUTED) + "</div>"
            + card(h3("Como ler") + lista(["<b>gato × felino: 0,86</b> — mesmo sentido, quase nenhuma palavra em comum",
                                           "<b>gato × cat: 0,81</b> — o modelo entende várias línguas",
                                           "<b>gato × juros: 0,12</b> — assuntos diferentes"], tam=26), bg=TEAL_BG),
            gap=32)
    + faixa("A conta:", "com vetores normalizados, o cosseno é só multiplicar os números par a par e somar — o "
            "produto escalar, np.dot(a, b). É uma linha de código.")
), notebook="§5", notas="Destaque que 'felino' e 'gato dormindo' não compartilham palavras importantes, e mesmo assim ficam perto.")

# ═════════════════════════════════════════════════════════════════════════════
# 12. Modelo de embedding
# ═════════════════════════════════════════════════════════════════════════════
secao("modelo-embedding", 12, (
    eyebrow("Embeddings") + titulo("Qual modelo de embedding usamos, e por quê")
    + lead("O modelo de embedding decide o que é “parecido”. Para esta aula ele precisa ser bom em português, leve, "
           "gratuito e simples de usar.")
    + tabela(["Modelo", "Tamanho", "Dimensões", "Recuperação em PT*", "Prefixo obrigatório?"],
             [["granite-embedding-311m-multilingual-r2 (o da aula)", "623 MB", "768", "<b>0,607</b>", "não"],
              ["bge-m3 (alternativa maior)", "2,3 GB", "1024", "0,635", "não"],
              ["multilingual-e5-small (versão anterior)", "471 MB", "384", "0,507", "sim"],
              ["paraphrase-multilingual-MiniLM", "471 MB", "384", "0,023", "não"]],
             [42, 13, 13, 16, 16], tam=24)
    + p("* Média das 6 tarefas de recuperação do benchmark MTEB-BR (2026), em português do Brasil.", cor=MUTED)
    + linha(card(h3("Sem prefixo") + p("É só model.encode(texto): nada de “query:” e “passage:” para esquecer.", tam=26))
            + card(h3("Um modelo para tudo") + p("Chunks e pergunta passam pelo mesmo modelo: vetores de modelos "
                                                 "diferentes não se comparam.", tam=26))
            + card(h3("Roda na GPU") + p("Cerca de 1 GB de memória; centenas de chunks em segundos.", tam=26)))
), notebook="§5", notas="Trocar de modelo é mudar uma linha — e recalcular todos os vetores.")

# ═════════════════════════════════════════════════════════════════════════════
# 13. Banco vetorial
# ═════════════════════════════════════════════════════════════════════════════
campos = tabela(["Campo", "Exemplo", "Para que serve"],
                [["id", "artigo.pdf:p3:c1", "identificar o chunk"],
                 ["texto", "“Os resultados mostram…”", "ser lido pelo LLM"],
                 ["vetor", "[0.021, -0.043, …] (768)", "ser comparado com a pergunta"],
                 ["metadados", "arquivo, página", "citar a fonte"]], [18, 44, 38], tam=24).replace("width:1728px", "width:1000px")
secao("banco", 13, (
    eyebrow("Banco vetorial") + titulo("Banco vetorial: uma biblioteca por assunto")
    + lead("Um <b>banco vetorial</b> guarda cada chunk com o seu vetor e responde rápido à pergunta: <i>quais vetores "
           "estão mais perto deste?</i> Um grupo de registros é uma <b>coleção</b>.")
    + linha(f'<div style="width:1000px; flex:none; display:flex; flex-direction:column; gap:16px">{h3("O que cada registro guarda")}{campos}</div>'
            + '<div style="flex:1; display:flex; flex-direction:column; gap:20px">'
            + card(h3("Analogia") + p("Biblioteca comum: ordem alfabética. Banco vetorial: por <b>assunto</b> — "
                                      "textos parecidos na mesma prateleira.", tam=26), bg=TEAL_BG)
            + card(h3("Chroma, em memória") + p("Roda dentro do Colab e some quando a sessão termina: nada fica "
                                                "gravado.", tam=26))
            + "</div>", gap=32)
    + faixa("Atenção:", "o banco não entende texto — ele <b>compara vetores</b>. Texto e metadados vão junto para "
            "sabermos <i>o que</i> foi encontrado e <i>de onde</i> veio.")
), notebook="§6", notas="Curiosidade: com milhões de vetores, bancos usam índices que acham vizinhos sem olhar um por um.")

# ═════════════════════════════════════════════════════════════════════════════
# 14. Busca semântica × palavra-chave
# ═════════════════════════════════════════════════════════════════════════════
def painel2(bg, cor, tit, itens, resultado):
    return card(h3(tit, cor=cor, tam=36) + lista(itens, tam=26) + '<div style="flex:1"></div>'
                + f'<p style="font-size:28px; font-weight:700; color:{cor}; background:{WHITE}; padding:14px 20px; '
                  f'border-radius:10px">{resultado}</p>', bg=bg, gap=16)


secao("busca-semantica", 14, (
    eyebrow("Busca") + titulo("Busca semântica × busca por palavra-chave")
    + lead("Pergunta: <i>“Quanto custa manter um carro?”</i> — e o documento fala em <i>“despesas com automóvel”</i>.")
    + linha(painel2(AMBER_BG, "#9A6310", "Busca por palavra-chave",
                    ["Procura as <b>mesmas palavras</b>", "“carro” não encontra “automóvel”",
                     "Ótima para nomes, siglas e códigos exatos (Art. 5º, CID J45)"],
                    "Resultado: não encontra o trecho")
            + painel2(TEAL_BG, TEAL, "Busca semântica (a desta aula)",
                      ["Compara <b>significados</b> (vetores)", "“carro” encontra “automóvel”",
                       "Ótima para perguntas em linguagem natural"],
                      "Resultado: encontra o trecho"), gap=32, extra="; flex:1")
    + p("<b>Curiosidade:</b> em aplicações reais é comum combinar as duas (busca híbrida). Nesta aula usamos só a semântica.",
        cor=MUTED, tam=26)
), notebook="§7", notas="A busca semântica é possível por causa dos embeddings do slide 10.")

# ═════════════════════════════════════════════════════════════════════════════
# 15. Retrieval
# ═════════════════════════════════════════════════════════════════════════════
fluxo_ret = linha(seta(AMBER).join([caixa("Pergunta", "texto"), caixa("Vetor", "768 números"),
                                    caixa("Banco vetorial", "compara"), caixa("Top-4", "trechos + endereço", borda=AMBER)]),
                  gap=12, extra="; align-items:stretch")
res_tab = tabela(["#", "Arquivo", "Página", "Similaridade", "Início do trecho"],
                 [["1", "artigo.pdf", "1", "0,82", "Os resultados indicam que…"],
                  ["2", "artigo.pdf", "5", "0,79", "Na avaliação com três bases…"],
                  ["3", "artigo.pdf", "6", "0,74", "Entre os LLMs avaliados…"],
                  ["4", "artigo.pdf", "5", "0,71", "Os modelos de embedding…"]], [6, 20, 12, 18, 44], tam=24
                 ).replace("width:1728px", "width:1180px")
secao("retrieval", 15, (
    eyebrow("Retrieval") + titulo("Retrieval: os k trechos mais próximos da pergunta")
    + lead("A pergunta vira um vetor <b>com o mesmo modelo</b> dos chunks, e o banco devolve os <b>k</b> vizinhos mais "
           "próximos — o <b>top-k</b>. É o “R” de RAG.")
    + fluxo_ret
    + linha(f'<div style="width:1180px; flex:none; display:flex; flex-direction:column; gap:10px">{res_tab}'
            + p("Exemplo ilustrativo de resultado com K = 4.", cor=MUTED) + "</div>"
            + '<div style="flex:1; display:flex; flex-direction:column; gap:16px">'
            + card(p("<b>K pequeno (1–2):</b> contexto enxuto; risco de faltar informação."), pad=20)
            + card(p("<b>K grande (8–10):</b> mais chance de trazer o certo; mais ruído para o modelo."), pad=20)
            + card(p("<b>Na aula: K = 4</b>, ajustável num controle deslizante."), pad=20, bg=AMBER_BG)
            + "</div>", gap=32)
), notebook="§7", notas="No notebook o aluno primeiro faz os três passos à mão e só depois os guarda na função buscar().")

# ═════════════════════════════════════════════════════════════════════════════
# 16. Quando nada é relevante
# ═════════════════════════════════════════════════════════════════════════════
def barra(rotulo, valor, cor):
    return (f'<div style="display:flex; gap:20px; align-items:center"><p style="width:500px; flex:none; font-size:24px; '
            f'text-align:right; color:{INK}">{rotulo}</p><div style="width:{int(valor * 600)}px; height:36px; flex:none; '
            f'background:{cor}; border-radius:4px"></div><p style="font-size:24px; color:{MUTED}">{valor:.2f}</p></div>'
            ).replace(f">{valor:.2f}<", f">{valor:.2f}<".replace(".", ","))


barras = "".join([barra("Quais modelos tiveram melhor desempenho?", .82, TEAL),
                  barra("Quais bases de dados foram usadas?", .78, TEAL),
                  barra("Como o estudo avaliou as respostas?", .74, TEAL),
                  barra("Qual a receita de bolo de cenoura?", .41, CORAL),
                  barra("Qual é a capital da Austrália?", .37, CORAL),
                  barra("Vai chover amanhã em Brasília?", .33, CORAL)])
secao("nada-relevante", 16, (
    eyebrow("Retrieval") + titulo("Quando nada é relevante, o banco não percebe")
    + lead("O banco <b>sempre devolve k trechos</b> — mesmo quando nenhum serve. A nota ajuda você a perceber, mas quem "
           "precisa saber recusar é o <b>prompt</b>.")
    + linha('<div style="flex:1; display:flex; flex-direction:column; gap:14px">' + barras
            + linha(p(f'<span style="color:{TEAL}"><b>■</b></span> sobre o documento (devem ser respondidas)')
                    + p(f'<span style="color:{CORAL}"><b>■</b></span> fora do assunto (devem ser recusadas)'), gap=40)
            + p("Similaridade do trecho mais próximo · valores ilustrativos", cor=MUTED) + "</div>"
            + '<div style="width:440px; flex:none; display:flex; flex-direction:column; gap:16px">'
            + card(h3("O que fazer") + lista(["Olhar as notas (§7) para criar intuição",
                                              "Autorizar o modelo a responder “não encontrei” (§9)"], tam=26))
            + card(p("<b>Curiosidade:</b> sistemas reais calibram um limiar de nota com perguntas de teste.", tam=24),
                   bg=AMBER_BG) + "</div>", gap=32)
), notebook="§7 · §12", notas="No notebook: a mesma busca com a pergunta do documento e com 'receita de bolo de cenoura'.")

# ═════════════════════════════════════════════════════════════════════════════
# 17. Contexto
# ═════════════════════════════════════════════════════════════════════════════
def anotacao(n, cor, tit, texto):
    return linha(circulo(n, cor, 52, 26) + f'<div style="display:flex; flex-direction:column; gap:4px">'
                 f'<p style="font-size:26px; font-weight:700; color:{NAVY}">{tit}</p>{p(texto)}</div>', gap=20,
                 extra="; align-items:start")


ctx = """
[1] (artigo.pdf, p. 1)
Os resultados indicam que …

[2] (artigo.pdf, p. 5)
Na avaliação com três bases …

[3] (artigo.pdf, p. 6)
Entre os LLMs avaliados …

[4] (artigo.pdf, p. 5)
Os modelos de embedding …
"""
secao("contexto", 17, (
    eyebrow("Contexto") + titulo("Contexto: os trechos que o modelo vai ler")
    + lead("O <b>contexto</b> é o conjunto de trechos recuperados, numerados e com endereço. É <b>todo</b> o "
           "conhecimento sobre o seu documento que o modelo vai receber.")
    + linha(f'<div style="width:820px; flex:none; display:flex">{codigo(ctx, 26)}</div>'
            + '<div style="flex:1; display:flex; flex-direction:column; gap:28px">'
            + anotacao(1, TEAL, "Número [n]", "É o que o modelo usa para citar a fonte de cada afirmação.")
            + anotacao(2, AMBER, "Endereço (arquivo, página)", "Vem dos metadados do chunk, guardados no banco.")
            + anotacao(3, CORAL, "Só os k trechos", "Não o documento inteiro. Se a resposta não está aqui, o modelo "
                                                    "não tem como sabê-la.")
            + card(p("<b>Analogia:</b> na prova com consulta, é a folha com os recortes numerados, com a página "
                     "anotada ao lado de cada um.", tam=26), bg=TEAL_BG)
            + "</div>", gap=40, extra="; flex:1")
), notebook="§8", notas="No notebook: montar_contexto() e a contagem de caracteres e tokens do contexto.")

# ═════════════════════════════════════════════════════════════════════════════
# 18. Prompt
# ═════════════════════════════════════════════════════════════════════════════
prompt_txt = """
<|im_start|>system
Você é um assistente que responde perguntas usando
SOMENTE os trechos numerados fornecidos.
Regras: 1. português · 2. cite [n] · 3. sem resposta:
"Não encontrei essa informação nos documentos
enviados." · 4. nada de conhecimento externo<|im_end|>
<|im_start|>user
Trechos:
[1] (artigo.pdf, p. 1) Os resultados indicam …
[2] (artigo.pdf, p. 5) Na avaliação com …
Pergunta: Quais modelos tiveram o melhor desempenho?<|im_end|>
<|im_start|>assistant
"""
secao("prompt", 18, (
    eyebrow("Prompt") + titulo("Anatomia do prompt: regras + contexto + pergunta")
    + lead("O <b>prompt</b> é tudo o que o modelo lê antes de responder. No RAG, não há mágica: é um texto bem montado.")
    + linha(f'<div style="width:1000px; flex:none; display:flex">{codigo(prompt_txt, 24)}</div>'
            + '<div style="flex:1; display:flex; flex-direction:column; gap:24px">'
            + anotacao(1, TEAL, "Mensagem de sistema", "As regras de comportamento do assistente.")
            + anotacao(2, AMBER, "Mensagem do usuário", "O contexto da etapa anterior + a pergunta.")
            + anotacao(3, CORAL, "Marcações do template", "&lt;|im_start|&gt; e &lt;|im_end|&gt; separam as mensagens "
                                                            "no formato em que o modelo foi treinado.")
            + anotacao(4, NAVY, "Você vê este texto", "No notebook, o prompt real é impresso e os tokens são contados.")
            + "</div>", gap=40, extra="; flex:1")
), notebook="§9", notas="O texto à esquerda é resumido; no notebook as regras aparecem completas.")

# ═════════════════════════════════════════════════════════════════════════════
# 19. Grounding
# ═════════════════════════════════════════════════════════════════════════════
def regra_card(n, cor, tit, evita):
    return card(linha(circulo(n, cor, 52, 26) + h3(tit), gap=20, extra="; align-items:center")
                + p(f"<b>Evita:</b> {evita}", tam=26), pad=28)


secao("grounding", 19, (
    eyebrow("Grounding") + titulo("Grounding: responder só com o que foi recuperado")
    + lead("<b>Grounding</b> (ancoragem) é prender a resposta aos trechos recuperados, proibindo o uso da “memória” "
           "do modelo. Cada regra do prompt evita um problema:")
    + f'<div style="display:grid; grid-template-columns:1fr 1fr; gap:20px">'
    + regra_card(1, TEAL, "Use SOMENTE os trechos", "completar com a memória do modelo, ou inventar.")
    + regra_card(2, AMBER, "Cite [n] após cada afirmação", "resposta sem fonte, impossível de conferir.")
    + regra_card(3, CORAL, "Frase exata de recusa", "chutar quando o documento não responde (e é fácil de detectar).")
    + regra_card(4, NAVY, "Responda em português", "resposta em inglês quando os trechos estão em inglês.")
    + "</div>"
    + faixa("Limite:", "grounding <b>reduz</b>, mas não elimina, erros — o modelo ainda pode interpretar mal um trecho "
            "ou citar o número errado. Por isso o notebook mostra as fontes para você conferir.", bg=CORAL_BG,
            cor_rot=CORAL, cor=INK)
), notebook="§9", notas="Analogia: as instruções no topo da prova com consulta.")

# ═════════════════════════════════════════════════════════════════════════════
# 20. Geração
# ═════════════════════════════════════════════════════════════════════════════
toks = ["Os", " melhores", " resulta", "dos", " foram", " do", " Multi", "lingual", " …", " [1]"]
tok_row = "".join(f'<p style="font-family:{F_MONO}; font-size:26px; color:{INK}; background:{AMBER_BG if t != " [1]" else TEAL_BG}; '
                  f'border:2px solid {AMBER if t != " [1]" else TEAL}; padding:10px 14px; border-radius:8px">{t.strip()}</p>'
                  for t in toks)
secao("geracao", 20, (
    eyebrow("Geração") + titulo("Geração: como o LLM escreve a resposta")
    + lead("O modelo escreve <b>um token</b> (pedaço de palavra) <b>por vez</b>. A cada passo escolhe o pedaço mais "
           "provável, dado o prompt e o que já escreveu — como o completar automático do celular, só que muito mais capaz.")
    + f'<div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center">{tok_row}</div>'
    + p("Cada caixa é um token, gerado em sequência; o [1] é a citação, escrita como qualquer outro token.", cor=MUTED)
    + linha(card(h3("O modelo da aula") + p("Qwen3-4B-Instruct: 4 bilhões de parâmetros, bom em português, gratuito e "
                                            "aberto. Ocupa ~8 GB na GPU.", tam=26))
            + card(h3("Respostas estáveis") + p("Sempre o token mais provável (do_sample=False): a mesma pergunta dá a "
                                                "mesma resposta.", tam=26))
            + card(h3("Streaming") + p("Os tokens aparecem conforme saem: você vê a resposta sendo escrita.", tam=26)),
            extra="; flex:1")
), notebook="§10", notas="No notebook a geração mostra tempo e tokens por segundo.")

# ═════════════════════════════════════════════════════════════════════════════
# 21. GPU
# ═════════════════════════════════════════════════════════════════════════════
def seg(gb, cor, total_px=1720, total_gb=15):
    return f'<div style="width:{round(gb / total_gb * total_px)}px; height:56px; flex:none; background:{cor}"></div>'


vram = (f'<div style="display:flex; border-radius:8px; overflow:hidden; border:2px solid {CARD}">'
        + seg(0.5, NAVY) + seg(1.2, TEAL) + seg(8.05, CORAL) + seg(1.5, AMBER) + seg(3.75, CARD) + "</div>")
leg = linha("".join(p(f'<span style="color:{c}"><b>■</b></span> {t}') for c, t in [
    (NAVY, "sistema 0,5 GB"), (TEAL, "embedding ~1,2 GB"), (CORAL, "LLM 8 GB"), (AMBER, "geração ~1,5 GB"),
    ("#9AA7B5", "livre ~3,8 GB")]), gap=32, extra="; flex-wrap:wrap")
secao("gpu", 21, (
    eyebrow("GPU do Colab") + titulo("Onde a GPU do Colab trabalha")
    + lead("<b>O modelo está sendo executado na GPU do Colab, e é isso que torna possível rodar a inferência dentro "
           "do próprio notebook.</b>")
    + tabela(["Etapa", "Onde roda", "Por quê"],
             [["Ler o PDF e cortar os chunks (§3–§4)", "CPU", "texto simples, rápido"],
              ["Embeddings dos chunks e da pergunta (§5, §7)", "GPU", "centenas de textos processados em paralelo"],
              ["Banco vetorial e busca (§6–§7)", "CPU", "poucas contas por pergunta"],
              ["LLM: carregar e gerar (§2, §10)", "GPU", "bilhões de contas para cada token"]], [44, 14, 42], tam=24)
    + h3("Memória da GPU T4 (15 GB) — estimativa", tam=28) + vram + leg
    + p("O desempenho depende da GPU que o Colab entregar. Sem GPU, o notebook usa um modelo menor (1,7 bilhão de "
        "parâmetros) e fica bem mais lento.", cor=MUTED)
), notebook="§1 · §2 · §10", notas="No notebook a função memoria_gpu() mostra os GB ocupados depois de cada modelo carregado.")

# ═════════════════════════════════════════════════════════════════════════════
# 22. Citações
# ═════════════════════════════════════════════════════════════════════════════
secao("citacoes", 22, (
    eyebrow("Fontes") + titulo("Citações: da resposta de volta à página")
    + lead("Cada <b>[n]</b> da resposta aponta para o trecho n do contexto — e, por ele, para um arquivo e uma página. "
           "Conferir as citações torna a resposta <b>verificável</b>.")
    + linha(f'<div style="flex:1; background:{WHITE}; border:2px solid {CARD}; border-radius:10px; padding:20px 24px">'
            + p("“…tiveram o melhor desempenho <b>[1]</b>, nas três bases avaliadas <b>[2]</b>.”", tam=26,
                extra="; font-style:italic") + "</div>" + seta(TEAL)
            + f'<div style="width:560px; flex:none; display:flex; flex-direction:column; gap:8px">'
            + pilula("[1] → artigo.pdf, p. 1", TEAL) + pilula("[2] → artigo.pdf, p. 5", TEAL) + "</div>",
            gap=20, extra="; align-items:center")
    + tabela(["Situação", "Quando acontece", "O que o notebook mostra"],
             [[f'<span style="color:{TEAL}">citada</span>', "há pelo menos um [n] válido", "tabela com arquivo, página e trecho"],
              [f'<span style="color:{AMBER}">sem fonte</span>', "resposta sem nenhum [n] válido", "aviso: confira com cuidado"],
              [f'<span style="color:{CORAL}">inválida</span>', "[7] quando só existem 4 trechos", "aviso com o número inválido"],
              [f'<span style="color:{NAVY}">recusa</span>', "“Não encontrei essa informação…”", "nenhuma fonte: comportamento correto"]],
             [20, 38, 42], tam=24)
    + p("<b>Recuperado ≠ citado:</b> nem todo trecho encontrado pela busca é usado na resposta.", tam=26)
), notebook="§11", notas="Analogia: a nota de rodapé de um trabalho — o leitor desconfiado pode ir até a página e conferir.")

# ═════════════════════════════════════════════════════════════════════════════
# 23. Com × sem RAG
# ═════════════════════════════════════════════════════════════════════════════
secao("com-sem-rag", 23, (
    eyebrow("Resultado") + titulo("Com RAG × sem RAG: o que esperar no notebook")
    + lead("Na §12 você faz as mesmas perguntas ao mesmo modelo, com e sem RAG. Estes são os comportamentos esperados:")
    + tabela(["Pergunta", "LLM sozinho", "LLM + RAG"],
             [["Sobre o artigo de exemplo", "não conhece o artigo, ou inventa; sem fonte",
               "responde a partir dos trechos e cita [n] → página"],
              ["Conhecimento geral: capital da Austrália", "acerta de memória: Camberra",
               "recusa: “Não encontrei essa informação nos documentos enviados.”"],
              ["Sobre um PDF que você enviou", "não tem como saber", "responde com as páginas do seu arquivo"]],
             [30, 32, 38], tam=26)
    + faixa("Recusar não é defeito:", "é o sistema sendo honesto sobre o que o documento diz. Se o modelo responder "
            "“Camberra” mesmo com as regras, você viu um limite real do grounding.", bg=TEAL_BG, cor_rot=TEAL, cor=INK)
), notebook="§12", notas="O comportamento real depende do modelo; registre o que acontecer na sua execução.")

# ═════════════════════════════════════════════════════════════════════════════
# 24. Limites
# ═════════════════════════════════════════════════════════════════════════════
secao("limites", 24, (
    eyebrow("Limites") + titulo("Limitações: onde um RAG pode errar")
    + tabela(["Sintoma", "Causa provável", "O que olhar"],
             [["“Não encontrei” para algo que está no documento", "texto mal extraído (escaneado, colunas misturadas)", "o texto extraído (§3)"],
              ["A busca traz trechos que não respondem", "chunk pequeno ou grande demais", "TAMANHO_CHUNK (§4)"],
              ["Falta informação na resposta", "K pequeno demais", "K (§7)"],
              ["Resposta confusa, com muito ruído", "K grande demais", "K (§7)"],
              ["Afirmação que não está no trecho citado", "o modelo interpretou mal", "a tabela de fontes (§11)"],
              ["Respostas fracas em geral", "modelo pequeno (sem GPU)", "o modelo escolhido (§2)"],
              ["Pergunta vaga traz trechos aleatórios", "a pergunta não tem assunto claro", "reescrever a pergunta"]],
             [40, 36, 24], tam=24)
), notebook="§14", notas="Use a tabela como roteiro de depuração: sempre começar pelo texto extraído.")

# ═════════════════════════════════════════════════════════════════════════════
# 25. Glossário
# ═════════════════════════════════════════════════════════════════════════════
GLOS = [("RAG", "buscar trechos relevantes e entregá-los ao modelo antes de ele responder"),
        ("LLM", "modelo de linguagem: aprendeu a escrever lendo muitos textos"),
        ("Alucinação", "informação inventada com aparência de verdade"),
        ("Token", "pedaço de palavra que o modelo lê e escreve"),
        ("Chunk", "pedaço do texto: a unidade de busca"),
        ("Embedding", "lista de números que representa o significado"),
        ("Similaridade", "nota de proximidade entre vetores: perto de 1 = mesmo sentido"),
        ("Banco vetorial", "guarda chunks e vetores para buscar por proximidade"),
        ("Retrieval (top-k)", "a busca: os k trechos mais próximos da pergunta"),
        ("Contexto e prompt", "trechos numerados + regras + pergunta: tudo o que o modelo lê"),
        ("Grounding", "ancorar a resposta nos trechos, sem usar a memória do modelo"),
        ("Citação", "o [n] que liga a afirmação ao arquivo e à página")]
cores_g = [TEAL, TEAL, CORAL, CORAL, TEAL, TEAL, TEAL, TEAL, AMBER, AMBER, CORAL, CORAL]
grid = "".join(f'<div style="background:{CARD}; border-radius:10px; padding:28px 26px; display:flex; flex-direction:column; gap:6px">'
               f'{h3(t, cor=c, tam=32)}{p(d, tam=27)}</div>' for (t, d), c in zip(GLOS, cores_g))
secao("glossario", 25, (
    eyebrow("Revisão") + titulo("Glossário de uma tela")
    + f'<div style="display:grid; grid-template-columns:1fr 1fr 1fr 1fr; gap:18px">{grid}</div>'
), notebook="§14", notas="O glossário completo, com mais termos, está no fim do notebook.")

# ═════════════════════════════════════════════════════════════════════════════
# 26. Mão na massa
# ═════════════════════════════════════════════════════════════════════════════
PASSOS = [("Abra o notebook", "No repositório, clique no badge “Abrir no Colab” de aula_rag_colab.ipynb.", TEAL),
          ("Ative a GPU", "Ambiente de execução → Alterar o tipo de ambiente → T4 GPU → Salvar.", TEAL),
          ("Rode de cima para baixo", "Shift + Enter em cada célula. A primeira vez baixa ~9 GB de modelos.", AMBER),
          ("Envie o seu PDF", "Ou clique em Cancelar upload para usar o artigo de exemplo.", AMBER),
          ("Pergunte", "Troque a pergunta na §7 ou na §13 e rode de novo.", CORAL),
          ("Confira as fontes", "Veja arquivo e página de cada [n] — e teste uma pergunta que o documento não responde.", CORAL)]
passos = "".join(card(linha(circulo(i + 1, c, 56, 28) + h3(t, tam=30), gap=18, extra="; align-items:center") + p(d, tam=26),
                      pad=28) for i, (t, d, c) in enumerate(PASSOS))
secao("mao-na-massa", 26, (
    eyebrow("Prática") + titulo("Mão na massa: abrindo o notebook no Colab")
    + f'<div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:20px">{passos}</div>'
    + faixa("Onde:", "github.com/Roger-Quinelato/webinarioOllamaRAG → aula 28-09/aula_rag_colab.ipynb · sem chave "
            "de API, sem cadastro, sem instalar nada.")
), notebook="§0", notas="Se a GPU não estiver disponível, o notebook avisa e usa um modelo menor na CPU.")

# ═════════════════════════════════════════════════════════════════════════════
# 27. Para discutir
# ═════════════════════════════════════════════════════════════════════════════
PERG = [("Recusar ou arriscar?", "No seu contexto, o que custa mais: uma recusa indevida ou uma resposta inventada?"),
        ("Que documentos você usaria?", "Seus PDFs têm texto extraível, ou são escaneados?"),
        ("Qual o tamanho certo de chunk?", "Teste 300, 700 e 2000 no notebook e compare as respostas."),
        ("Quanto confiar na citação?", "Uma fonte citada garante que a resposta está correta?"),
        ("Framework ou código próprio?", "Agora que você viu cada etapa, o que um framework esconderia?")]
perguntas = "".join(linha(circulo(i + 1, AMBER, 56, 28) + '<div style="display:flex; flex-direction:column; gap:4px">'
                          + f'<p style="font-size:30px; font-weight:700; color:{WHITE}">{t}</p>'
                          + f'<p style="font-size:26px; color:{ON_DARK2}">{d}</p></div>', gap=24,
                          extra="; align-items:center") for i, (t, d) in enumerate(PERG))
secao("discutir", 27, (
    eyebrow("Para discutir") + titulo("Cinco perguntas para depois da prática", cor=WHITE)
    + linha(f'<div style="flex:1; display:flex; flex-direction:column; gap:26px">{perguntas}</div>'
            + f'<div style="width:560px; flex:none; background:{NAVY2}; border-radius:12px; padding:32px; display:flex; '
              f'flex-direction:column; gap:14px">'
            + h3("Curiosidades para depois", cor=AMBER_LIGHT, tam=34)
            + lista(["<b>Reranking:</b> reordenar os trechos com um 2º modelo", "<b>Busca híbrida:</b> significado + "
                     "palavra-chave", "<b>Avaliação:</b> medir a qualidade a cada mudança", "<b>Quantização:</b> "
                     "modelos maiores em GPUs menores", "<b>LangChain e LlamaIndex:</b> as mesmas etapas, em menos linhas"],
                    tam=26, cor=ON_DARK) + "</div>", gap=48, extra="; flex:1; align-items:center")
), escuro=True, notebook="§14", notas="Encerramento. Abra o debate a partir das perguntas; as curiosidades são caminhos para depois da aula.")

# ═════════════════════════════════════════════════════════════════════════════
# Arquivos
# ═════════════════════════════════════════════════════════════════════════════
for id_, html in slides:
    (RAIZ / "project" / "slides" / f"{id_}.html").write_text(html, encoding="utf-8")

deck = {
    "v": 4,
    "createdOnFiles": {"v": 1, "at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
    "title": "Aula prática de RAG",
    "cover": "capa",
    "order": [i for i, _ in slides],
    "sections": {
        "abertura": {"description": "O problema que o RAG resolve, os objetivos e o mapa da aula", "start": "capa"},
        "preparar": {"description": "Preparar o material: documentos, chunks, embeddings e banco vetorial", "start": "documentos"},
        "responder": {"description": "Responder: busca, contexto, prompt, grounding, geração, GPU e citações", "start": "busca-semantica"},
        "fechamento": {"description": "Limites, glossário, prática no Colab e perguntas para discutir", "start": "limites"},
    },
    "faces": {
        "caladea": {"family": "Caladea", "href": "https://fonts.googleapis.com/css2?family=Caladea:wght@400;700&display=swap"},
        "carlito": {"family": "Carlito", "href": "https://fonts.googleapis.com/css2?family=Carlito:ital,wght@0,400;0,700;1,400&display=swap"},
        "cousine": {"family": "Cousine", "href": "https://fonts.googleapis.com/css2?family=Cousine:wght@400;700&display=swap"},
    },
    "designSystems": [],
}
(RAIZ / "project" / "deck.json").write_text(json.dumps(deck, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(slides), "slides")
