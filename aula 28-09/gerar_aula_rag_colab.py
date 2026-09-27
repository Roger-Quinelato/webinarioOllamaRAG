"""Gera aula 28-09/aula_rag_colab.ipynb: aula prática de RAG 100% no Google Colab (épico #137).

O notebook é escrito aqui como uma lista de células para facilitar revisão em diff.
Nunca edite o .ipynb à mão: altere este arquivo e rode

    python "aula 28-09/gerar_aula_rag_colab.py"
    python "aula 28-09/checar_aula.py"

Regras pedagógicas (ver aula 28-09/decisoes.md):
- ciclo por etapa: 🧠 conceito → 🧩 analogia → ▶️ código → 👀 resultado → 💡 interpretação;
- uma célula de código = uma ideia (mediana ≤ 8 linhas, máximo 15);
- toda célula de código vem depois de uma célula de texto;
- nada de API externa: embeddings e LLM rodam no runtime do Colab.
"""

import json
import statistics
from pathlib import Path
from textwrap import dedent

DESTINO = Path(__file__).with_name("aula_rag_colab.ipynb")
URL_COLAB = (
    "https://colab.research.google.com/github/Roger-Quinelato/webinarioOllamaRAG/"
    "blob/main/aula%2028-09/aula_rag_colab.ipynb"
)
URL_REPO = "https://github.com/Roger-Quinelato/webinarioOllamaRAG"

celulas = []


def md(texto):
    celulas.append(("markdown", dedent(texto).strip("\n")))


def code(texto):
    celulas.append(("code", dedent(texto).strip("\n")))


# ═════════════════════════════════════════════════════════════════════════════
# §0 Boas-vindas
# ═════════════════════════════════════════════════════════════════════════════
md(f"""
# 🧭 Aula prática de RAG: do documento à resposta com fonte

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)]({URL_COLAB})

Nesta aula você vai montar, etapa por etapa, um assistente que **responde perguntas sobre os documentos
que você enviar**, dizendo **de qual página tirou cada informação** — e admitindo quando a resposta não
está lá. Essa técnica se chama **RAG** (*Retrieval-Augmented Generation*, ou **Geração Aumentada por
Recuperação**).

Tudo roda **aqui dentro do Google Colab**, usando a GPU gratuita dele. Você **não** precisa de chave de
API, cartão de crédito, cadastro em serviço de IA, Docker ou instalar nada no seu computador.
""")

md("""
## 0. Boas-vindas: o que você vai aprender

**Ao terminar esta aula, você vai conseguir:**

1. Explicar em uma frase o que é RAG e **que problema ele resolve**.
2. Ler um PDF e **ver o texto que o computador extraiu** de cada página.
3. Dividir o texto em pedaços (*chunks*) e explicar por que o **tamanho** e a **sobreposição** importam.
4. Transformar um texto em números (*embedding*) e entender **por que textos parecidos ficam perto**.
5. Criar um **banco vetorial** e dizer o que ele guarda.
6. Fazer uma **busca por significado** e ler o resultado: qual trecho, de qual página, com que nota.
7. Montar o **prompt** e ler exatamente o que o modelo de linguagem recebe.
8. Rodar um **modelo de linguagem na GPU do Colab** e ver quanta memória ele ocupa.
9. Ligar cada citação `[1]`, `[2]` da resposta ao **arquivo e à página** de origem.
10. Reconhecer os **limites** de um RAG: quando ele acerta ao recusar e onde ele pode errar.

**Uma analogia para a aula inteira: a prova com consulta.** Um modelo de linguagem sozinho é como um
aluno fazendo prova **de memória**: sabe muita coisa, mas não leu o *seu* material e, na dúvida, pode
"chutar" com confiança. O RAG transforma isso numa **prova com consulta**: antes de responder, o aluno
procura as páginas certas do material, lê os trechos e responde **citando de onde tirou**.
""")

md("""
### 🗺️ O caminho que vamos percorrer

```
 PREPARAR O MATERIAL (uma vez)
 seu documento ─► texto por página ─► pedaços (chunks) ─► números (embeddings) ─► banco vetorial
      §3                 §3                 §4                    §5                   §6

 RESPONDER (a cada pergunta)
 sua pergunta ─► busca dos trechos ─► contexto ─► prompt ─► modelo de linguagem ─► resposta com fonte
                        §7               §8         §9            §10                    §11
```

Antes disso, na §1 preparamos o Colab e, na §2, vemos **o problema** que o RAG resolve. Depois da
§11, comparamos **com e sem RAG** (§12), juntamos tudo numa função só (§13) e falamos dos limites (§14).
""")

md("""
### ▶️ Como usar este notebook

- O notebook tem **células de texto** (como esta) e **células de código** (com fundo cinza).
- Para rodar uma célula de código, clique nela e aperte **`Shift + Enter`**. O resultado aparece logo abaixo.
- Rode **de cima para baixo**, na ordem. Cada célula usa o que as anteriores prepararam.
- Algumas células têm **campos editáveis** à direita (formulários). Mude o valor e rode de novo para ver o efeito.

### ⚡ Antes de tudo: ative a GPU

No menu do Colab: **Ambiente de execução → Alterar o tipo de ambiente → T4 GPU → Salvar**.

> ⏱️ Na primeira execução o Colab baixa os modelos (cerca de 9 GB). Isso leva alguns minutos — é
> normal. Aproveite para ler as explicações enquanto espera.
>
> 🔒 Seus documentos ficam só nesta sessão do Colab. Nada é enviado para serviços de IA externos.
""")

# ═════════════════════════════════════════════════════════════════════════════
# §1 Preparar o Colab
# ═════════════════════════════════════════════════════════════════════════════
md("""
## 1. Preparar o Colab: a GPU, as bibliotecas e a memória

**🧠 Conceito.** Modelos de linguagem fazem bilhões de multiplicações para escrever cada palavra. Uma
**GPU** (placa de vídeo) é um processador feito para fazer milhares de contas **ao mesmo tempo**. A
memória dela se chama **VRAM** — e o modelo inteiro precisa caber ali para rodar rápido.

**🧩 Analogia.** A CPU é uma pequena equipe de cozinheiros muito habilidosos. A GPU é um exército de
ajudantes que só sabem picar legumes — mas picam milhares ao mesmo tempo. Para modelos de linguagem,
o que precisamos é justamente "picar muitos legumes".

**▶️ Primeiro, vamos ver qual GPU o Colab te entregou:**
""")

code(r'''
import torch

if torch.cuda.is_available():
    gpu = torch.cuda.get_device_properties(0)
    print(f"✅ GPU encontrada: {gpu.name}, com {gpu.total_memory / 1e9:.1f} GB de memória (VRAM)")
else:
    print("⚠️ Nenhuma GPU encontrada. O notebook funciona, mas vai ficar MUITO mais lento.")
    print("   Para ativar: Ambiente de execução → Alterar o tipo de ambiente → T4 GPU → Salvar.")
    print("   Depois, rode o notebook de novo desde o início.")
''')

md("""
**▶️ Agora instalamos as bibliotecas** que ainda não vêm no Colab. Cada uma cuida de uma etapa:

| Biblioteca | Para que serve nesta aula |
|---|---|
| `pypdf` | ler o texto de arquivos PDF (§3) |
| `langchain-text-splitters` | cortar o texto em pedaços (§4) |
| `sentence-transformers` | transformar texto em números — embeddings (§5) |
| `chromadb` | o banco vetorial (§6) |
| `transformers` | carregar e rodar o modelo de linguagem (§2 e §10) |

Leva de 1 a 2 minutos. Avisos em vermelho sobre versões de outros pacotes do Colab podem ser ignorados.
""")

code(r'''
%pip install -q "pypdf>=5.0" "langchain-text-splitters>=0.3" "sentence-transformers>=5.0" "chromadb>=1.0" "transformers>=4.56"
''')

md("""
**▶️ Ferramentas de apoio.** Estas bibliotecas não são de RAG: servem para medir tempo, lidar com
arquivos, fazer contas com listas de números e mostrar tabelas.
""")

code(r'''
import html                      # para mostrar textos com destaque colorido
import time                      # para medir quanto tempo cada etapa leva
from pathlib import Path         # para lidar com pastas e arquivos

import numpy as np               # contas com vetores (listas de números)
import pandas as pd              # tabelas para ver os resultados
from IPython.display import HTML, display

pd.set_option("display.max_colwidth", 200)
TEMPOS = {}  # guardamos aqui os tempos de cada etapa (usados no diagnóstico do final)
DISPOSITIVO = "cuda" if torch.cuda.is_available() else "cpu"
print("Tudo pronto. Os modelos vão rodar em:", "GPU" if DISPOSITIVO == "cuda" else "CPU")
''')

md("""
**▶️ Um medidor de memória.** Vamos usar esta pequena função várias vezes para **ver** a GPU
trabalhando: quanto da memória ela está usando depois de cada modelo carregado.
""")

code(r'''
def memoria_gpu(momento):
    """Mostra quanta memória da GPU (VRAM) está ocupada agora."""
    if not torch.cuda.is_available():
        return print(f"{momento}: sem GPU (tudo roda na CPU)")
    usada = torch.cuda.memory_allocated() / 1e9
    total = torch.cuda.get_device_properties(0).total_memory / 1e9
    print(f"{momento}: {usada:.1f} GB ocupados de {total:.1f} GB da GPU")


memoria_gpu("Antes de carregar qualquer modelo")
''')

md("""
**💡 O que isso significa.** A memória está vazia (ou quase): ainda não carregamos nenhum modelo. Nesta
aula a GPU vai trabalhar em **dois lugares**:

- no **modelo de linguagem**, que escreve as respostas (§2 e §10) — é a parte mais pesada;
- no **modelo de embeddings**, que transforma textos em números (§5).
""")

# ═════════════════════════════════════════════════════════════════════════════
# §2 O problema: um LLM sozinho
# ═════════════════════════════════════════════════════════════════════════════
md("""
## 2. O problema: um modelo de linguagem sozinho

**🧠 Conceito.** Um **modelo de linguagem** (em inglês, *Large Language Model*, ou **LLM**) é um programa
que aprendeu a escrever lendo uma quantidade enorme de textos. Mas ele só "sabe" o que estava nesses
textos, **até a data em que foi treinado**. Ele **nunca leu os seus documentos**. Quando perguntado
sobre algo que não conhece, ele pode dizer que não sabe — ou **inventar uma resposta com toda a
confiança**. Esse comportamento é chamado de **alucinação**.

**🧩 Analogia.** Imagine um especialista brilhante que passou os últimos anos isolado, sem internet.
Pergunte a ele sobre um relatório publicado ontem: ou ele admite que não leu, ou dá um palpite
convincente — e você não tem como saber qual dos dois.

Vamos ver isso acontecer. Carregamos o modelo **logo agora** por dois motivos: para mostrar o problema
antes da solução, e porque o download demora — enquanto isso, você lê.

**▶️ Escolher o modelo pelo tamanho da GPU.** Usaremos o **Qwen3** (da Alibaba, gratuito e de código
aberto). A versão de 4 bilhões de parâmetros ocupa cerca de 8 GB — cabe na T4 (15 GB). Se a GPU for
menor, ou se não houver GPU, usamos a versão de 1,7 bilhão (cerca de 4 GB).
""")

code(r'''
vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9 if torch.cuda.is_available() else 0

if vram_gb >= 12:
    MODELO_LLM = "Qwen/Qwen3-4B-Instruct-2507"   # melhor qualidade em português que cabe na T4
else:
    MODELO_LLM = "Qwen/Qwen3-1.7B"               # menor: cabe em GPUs menores e roda (devagar) na CPU

print("Modelo de linguagem escolhido:", MODELO_LLM)
''')

md("""
**🧠 Tokens.** O modelo não lê letras nem palavras inteiras: ele lê **pedaços de palavras**, chamados
**tokens**. Quem faz esse corte é o **tokenizador**. Veja como uma frase é cortada:
""")

code(r'''
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(MODELO_LLM)

frase = "Geração aumentada por recuperação"
ids = tokenizer(frase).input_ids
print(f"'{frase}' virou {len(ids)} tokens:")
print([tokenizer.decode([i]) for i in ids])
''')

md("""
**▶️ Carregar o modelo na GPU.** Esta é a célula mais demorada da aula (download de ~8 GB na primeira
vez). Usamos **meia precisão** (`float16`): cada número do modelo ocupa 2 bytes em vez de 4 — é o
formato que a GPU T4 processa bem.
""")

code(r'''
from transformers import AutoModelForCausalLM

inicio = time.perf_counter()
llm = AutoModelForCausalLM.from_pretrained(
    MODELO_LLM,
    dtype=torch.float16 if DISPOSITIVO == "cuda" else torch.float32,  # meia precisão na GPU
    device_map=DISPOSITIVO,  # coloca o modelo na GPU (ou na CPU, se não houver GPU)
)
TEMPOS["carregar o LLM (s)"] = round(time.perf_counter() - inicio)
print(f"Modelo carregado em {TEMPOS['carregar o LLM (s)']} s, no dispositivo: {llm.device}")
memoria_gpu("Depois de carregar o modelo de linguagem")
''')

md("""
**💡 O que isso significa.** **O modelo está sendo executado na GPU do Colab, e é isso que torna possível
rodar a inferência dentro do próprio notebook.** Os ~8 GB ocupados são os **parâmetros** do modelo:
4 bilhões de números × 2 bytes cada. Modelos maiores não caberiam nesta GPU sem técnicas de compressão.

> **Curiosidade:** para rodar modelos maiores em GPUs pequenas existe a **quantização**, que guarda cada
> número com ainda menos bytes, com alguma perda de qualidade.
""")

md("""
**▶️ Uma função para conversar com o modelo.** A conversa é uma lista de **mensagens**, cada uma com um
**papel** (`system` = instruções; `user` = quem pergunta) e um **conteúdo**. A função:

1. transforma as mensagens no formato de texto que o modelo foi treinado para ler (o *template de chat*);
2. pede ao modelo que escreva a resposta **token por token**, mostrando cada pedaço assim que sai (*streaming*);
3. usa sempre a escolha mais provável (`do_sample=False`), para a resposta não mudar a cada execução.

(`enable_thinking=False` pede uma resposta direta, sem um longo "raciocínio em voz alta" antes.)
""")

code(r'''
from transformers import TextStreamer


def gerar(mensagens, max_tokens=512):
    """Envia as mensagens ao modelo e mostra a resposta sendo escrita, pedaço por pedaço."""
    entradas = tokenizer.apply_chat_template(
        mensagens, add_generation_prompt=True, enable_thinking=False,
        return_tensors="pt", return_dict=True,
    ).to(llm.device)
    streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
    saida = llm.generate(**entradas, max_new_tokens=max_tokens, do_sample=False,
                         temperature=None, top_p=None, top_k=None, streamer=streamer)
    novos = saida[0][entradas["input_ids"].shape[1]:]  # só os tokens que o modelo escreveu
    return tokenizer.decode(novos, skip_special_tokens=True)
''')

md("""
**▶️ Aquecimento: uma pergunta de conhecimento geral.** Isso o modelo aprendeu no treinamento:
""")

code(r'''
_ = gerar([{"role": "user", "content": "Em duas frases: o que é fotossíntese?"}])
''')

md("""
**▶️ Agora, uma pergunta sobre um documento que ele nunca leu.** O artigo de exemplo desta aula foi
publicado no fim de 2025 (Medeiros & Oliveira, SEMISH 2025) e compara modelos para RAG em português.
""")

code(r'''
PERGUNTA_SOBRE_O_ARTIGO = (
    "No artigo de Medeiros e Oliveira (SEMISH 2025) que compara modelos de embeddings e LLMs "
    "para RAG em português, quais modelos tiveram o melhor desempenho?"
)
resposta_sem_rag = gerar([{"role": "user", "content": PERGUNTA_SOBRE_O_ARTIGO}])
''')

md("""
**💡 O que isso significa.** O modelo pode ter dito que não conhece o artigo — ou pode ter citado
modelos que *parecem* plausíveis. Guarde essa resposta: na §12 vamos compará-la com a resposta do RAG,
que vai **ler o artigo** antes de responder e **mostrar a página**.

Esse é o problema que o RAG resolve: **dar ao modelo o material certo, na hora da pergunta, e exigir
que ele responda a partir dele.** Para isso, primeiro precisamos preparar o material. Vamos à §3.
""")

# ═════════════════════════════════════════════════════════════════════════════
# §3 Documentos
# ═════════════════════════════════════════════════════════════════════════════
md("""
## 3. Documentos: do arquivo ao texto com endereço

**🧠 Conceito.** Um PDF não guarda "texto corrido": ele guarda **desenhos de letras em posições da
página**. Para usar o conteúdo, um programa precisa **extrair** o texto, página por página. Guardamos
cada página junto com o seu **endereço** — o nome do arquivo e o número da página. Essas informações
*sobre* o texto se chamam **metadados**, e são elas que vão permitir **citar a fonte** no final.

**🧩 Analogia.** É como tirar uma cópia de cada página de um livro e anotar no canto: *"livro X,
página 12"*. Mais tarde, quando você usar aquela cópia, sabe exatamente de onde ela veio.

**▶️ Envie os seus documentos** (PDF, TXT ou MD). Ao rodar a célula aparece o botão *Escolher arquivos*.
Se preferir usar o **artigo de exemplo**, clique em **Cancelar upload**.
""")

code(r'''
PASTA = Path("meus_documentos")
PASTA.mkdir(exist_ok=True)

try:
    from google.colab import files  # só existe dentro do Colab
    for nome, conteudo in files.upload().items():
        (PASTA / nome).write_bytes(conteudo)
except ImportError:
    print(f"Fora do Colab: copie seus arquivos para a pasta {PASTA.resolve()}")
except Exception:
    print("Nenhum arquivo enviado — vamos usar o artigo de exemplo.")
''')

md("""
**▶️ Artigo de exemplo.** Se você não enviou nada, baixamos da biblioteca digital da SBC o artigo
*"Comparação de Modelos de Embeddings e LLMs para Geração Aumentada por Recuperação em Português"*
(Medeiros & Oliveira, SEMISH 2025 — licença CC BY-NC 4.0). Se o download falhar, usamos o artigo que
criou o termo RAG (Lewis et al., 2020, em inglês).
""")

code(r'''
import urllib.request

EXEMPLOS = {  # nome do arquivo → endereço oficial (o primeiro que funcionar é usado)
    "exemplo_medeiros2025_embeddings_rag.pdf": "https://sol.sbc.org.br/index.php/semish/article/download/36829/36615/",
    "exemplo_lewis2020_rag.pdf": "https://arxiv.org/pdf/2005.11401",
}
FORMATOS = {".pdf", ".txt", ".md"}
if not any(p.suffix.lower() in FORMATOS for p in PASTA.iterdir()):
    for nome, url in EXEMPLOS.items():
        try:
            pedido = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            (PASTA / nome).write_bytes(urllib.request.urlopen(pedido, timeout=60).read())
            print("Baixamos o documento de exemplo:", nome)
            break
        except Exception as erro:
            print(f"Não consegui baixar {nome} ({erro}). Tentando o próximo…")
''')

md("""
**▶️ Quais arquivos temos?**
""")

code(r'''
arquivos = sorted(p for p in PASTA.iterdir() if p.suffix.lower() in FORMATOS)
assert arquivos, "Nenhum documento encontrado: envie um arquivo na célula de upload."
for p in arquivos:
    print(f"📄 {p.name}  ({p.stat().st_size / 1024:.0f} KB)")
''')

md("""
**▶️ Abrir um PDF e ler uma página.** Antes de qualquer transformação, vale sempre **olhar o texto que
foi extraído** — se ele vier embaralhado, todo o resto do RAG sofre.
""")

code(r'''
from pypdf import PdfReader

primeiro_pdf = next((p for p in arquivos if p.suffix.lower() == ".pdf"), None)
if primeiro_pdf:
    leitor = PdfReader(primeiro_pdf)
    print(f"{primeiro_pdf.name} tem {len(leitor.pages)} páginas.\n")
    print("Texto extraído da página 1 (primeiros 600 caracteres):\n")
    print(leitor.pages[0].extract_text()[:600])
''')

md("""
**▶️ Uma função para ler qualquer documento.** Ela devolve uma **lista de páginas**; cada página é um
pequeno registro com três campos: `arquivo`, `pagina` e `texto`. Arquivos TXT e MD contam como uma
página só.
""")

code(r'''
def ler_documento(caminho):
    """Devolve as páginas do documento, cada uma com o texto e o endereço (arquivo, página)."""
    if caminho.suffix.lower() == ".pdf":
        textos = [pagina.extract_text() or "" for pagina in PdfReader(caminho).pages]
    else:  # .txt e .md: o arquivo inteiro conta como página 1
        textos = [caminho.read_text(encoding="utf-8", errors="ignore")]
    return [{"arquivo": caminho.name, "pagina": n, "texto": t} for n, t in enumerate(textos, start=1)]
''')

md("""
**▶️ Ler todos os arquivos.** Páginas quase sem texto (menos de 30 caracteres) são deixadas de lado —
geralmente são imagens escaneadas.
""")

code(r'''
todas = [pagina for caminho in arquivos for pagina in ler_documento(caminho)]
paginas = [p for p in todas if len(p["texto"].strip()) >= 30]

resumo = pd.DataFrame(paginas)
resumo["caracteres"] = resumo["texto"].str.len()
display(resumo.groupby("arquivo").agg(paginas=("pagina", "count"), caracteres=("caracteres", "sum")))
if len(todas) > len(paginas):
    print(f"⚠️ {len(todas) - len(paginas)} página(s) sem texto — provavelmente imagem escaneada.")
''')

md("""
**👀 Um registro por dentro.** É assim que cada página ficou guardada:
""")

code(r'''
exemplo = paginas[min(1, len(paginas) - 1)]
print("arquivo:", exemplo["arquivo"])
print("página: ", exemplo["pagina"])
print("texto:  ", exemplo["texto"][:300], "…")
''')

md("""
**💡 O que isso significa.** Agora temos o texto do documento **com endereço**. Se o texto extraído
parecer estranho (palavras coladas, colunas misturadas), é aqui que o problema nasce — e nenhuma etapa
seguinte consegue consertar.

> **Curiosidade:** PDFs escaneados (fotos de páginas) não têm texto para extrair. Eles precisam de
> **OCR**, uma técnica que "lê" a imagem — fica fora desta aula.

Uma página inteira ainda é grande demais para ser a unidade de busca. Na §4 vamos cortá-la em pedaços.
""")

# ═════════════════════════════════════════════════════════════════════════════
# §4 Chunking
# ═════════════════════════════════════════════════════════════════════════════
md("""
## 4. Chunking: cortar o texto em pedaços

**🧠 Conceito.** Não entregamos o documento inteiro ao modelo. Em vez disso, cortamos o texto em
pedaços menores, chamados **chunks**, por três motivos:

1. **Busca mais precisa:** um pedaço pequeno fala de um assunto só, então é mais fácil saber se ele
   combina com a pergunta.
2. **Limite do modelo:** o modelo só consegue ler uma quantidade limitada de texto de cada vez.
3. **Citação:** dá para apontar exatamente o trecho que sustenta cada afirmação.

Para não partir uma ideia ao meio, cada chunk **repete o final do anterior**. Essa repetição se chama
**sobreposição** (em inglês, *overlap*).

**🧩 Analogia.** Pense em fichas de estudo. Cada ficha resume um trecho do livro. Se uma frase importante
cai bem na divisa entre duas fichas, você a copia nas duas — assim ela aparece inteira em pelo menos uma.

**▶️ Configurar o cortador.** Usamos o `RecursiveCharacterTextSplitter`, que tenta cortar primeiro entre
parágrafos, depois entre linhas, depois entre frases — e só em último caso no meio de uma palavra.
""")

code(r'''
TAMANHO_CHUNK = 700  # @param {type:"slider", min:200, max:2000, step:100}
SOBREPOSICAO = 150  # @param {type:"slider", min:0, max:400, step:50}

from langchain_text_splitters import RecursiveCharacterTextSplitter

divisor = RecursiveCharacterTextSplitter(
    chunk_size=TAMANHO_CHUNK,      # tamanho máximo de cada pedaço, em caracteres
    chunk_overlap=SOBREPOSICAO,    # quantos caracteres se repetem entre pedaços vizinhos
    separators=["\n\n", "\n", ". ", " ", ""],  # onde preferir cortar: parágrafo → linha → frase → palavra
)
''')

md("""
**▶️ Cortar uma página** — a que tem mais texto — e ver os primeiros pedaços:
""")

code(r'''
pagina_exemplo = max(paginas, key=lambda p: len(p["texto"]))
pedacos = divisor.split_text(pagina_exemplo["texto"])
print(f"{pagina_exemplo['arquivo']}, página {pagina_exemplo['pagina']}: "
      f"{len(pagina_exemplo['texto'])} caracteres → {len(pedacos)} chunks")
for i, pedaco in enumerate(pedacos[:3], start=1):
    print(f"\n── chunk {i} ({len(pedaco)} caracteres) ──\n{pedaco}")
''')

md("""
**▶️ Enxergar a sobreposição.** Esta função procura o maior trecho que **termina** um chunk e
**começa** o seguinte:
""")

code(r'''
def sobreposicao(a, b):
    """Maior trecho que aparece no fim do chunk a e no começo do chunk b."""
    for n in range(min(len(a), len(b)), 0, -1):
        if a.endswith(b[:n]):
            return b[:n]
    return ""
''')

md("""
**👀 O trecho repetido aparece destacado** no fim do chunk 1 e no começo do chunk 2:
""")

code(r'''
repetido = sobreposicao(pedacos[0], pedacos[1]) if len(pedacos) > 1 else ""
if repetido:
    marca = f"<mark style='background:#FBF1E0;outline:1px dashed #E09A2C'>{html.escape(repetido)}</mark>"
    fim_1 = html.escape(pedacos[0][: -len(repetido)][-200:]) + marca
    inicio_2 = marca + html.escape(pedacos[1][len(repetido):][:200])
    display(HTML(f"<p><b>Fim do chunk 1:</b> …{fim_1}</p><p><b>Começo do chunk 2:</b> {inicio_2}…</p>"))
    print(f"{len(repetido)} caracteres aparecem nos dois chunks: essa é a sobreposição.")
else:
    print("Sem sobreposição visível aqui (SOBREPOSICAO = 0 ou a página virou um chunk só).")
''')

md("""
**▶️ Cortar todas as páginas.** Cada chunk ganha um **id**, um endereço único no formato
`arquivo:p3:c1` (arquivo, página 3, chunk 1 daquela página), e herda o arquivo e a página de origem.
""")

code(r'''
chunks = []
for pagina in paginas:
    for i, texto in enumerate(divisor.split_text(pagina["texto"]), start=1):
        chunks.append({
            "id": f"{pagina['arquivo']}:p{pagina['pagina']}:c{i}",
            "arquivo": pagina["arquivo"], "pagina": pagina["pagina"], "texto": texto,
        })
print(f"{len(paginas)} páginas → {len(chunks)} chunks")
print("Exemplo de id:", chunks[0]["id"])
''')

md("""
**👀 Quantos chunks têm cada tamanho?**
""")

code(r'''
tamanhos = pd.Series([len(c["texto"]) for c in chunks])
print(f"Tamanho: média {tamanhos.mean():.0f} · menor {tamanhos.min()} · maior {tamanhos.max()} caracteres")
tamanhos.plot.hist(bins=30, title="Quantos chunks têm cada tamanho", figsize=(7, 2.5), color="#1F8F7C");
''')

md("""
**💡 O que isso significa.** A maioria dos chunks fica perto do tamanho máximo que escolhemos; os
menores são finais de página. Não existe tamanho perfeito — é um equilíbrio:

| | Chunk pequeno (~300) | Chunk grande (~2000) |
|---|---|---|
| Busca | mais precisa | mais "genérica" |
| Contexto para o modelo | pode faltar informação | traz mais informação, e mais ruído |
| Citação | aponta um trecho curto | aponta um trecho longo |

Experimente: mude `TAMANHO_CHUNK` lá em cima, rode as células desta seção de novo e compare.

> **Curiosidade:** em aplicações reais também se corta por **títulos e seções** do documento, ou onde
> o **assunto muda**.

Temos os pedaços. Mas como o computador vai saber qual pedaço **combina** com uma pergunta? Na §5 vamos
transformar texto em números.
""")

# ═════════════════════════════════════════════════════════════════════════════
# §5 Embeddings
# ═════════════════════════════════════════════════════════════════════════════
md("""
## 5. Embeddings: transformar significado em números

**🧠 Conceito.** Imagine que transformamos cada trecho de texto em uma **coordenada num espaço
matemático**. Textos parecidos ficam **próximos** uns dos outros, mesmo que usem palavras diferentes —
ou línguas diferentes. Essa representação numérica é chamada de **embedding**. Cada embedding é um
**vetor**: uma lista de centenas de números.

**🧩 Analogia.** Num mapa, "Brasília" e "Goiânia" ficam perto porque suas coordenadas (latitude,
longitude) são parecidas. Um modelo de embedding faz o mesmo com **significados**: dá a cada texto
coordenadas — só que com 768 números em vez de 2. "Gato dormindo" e "felino descansando" ganham
coordenadas vizinhas.

A proximidade é medida pela **similaridade de cosseno**: perto de **1** = mesmo sentido; perto de
**0** = sem relação.

**▶️ Carregar o modelo de embedding** (`granite-embedding-311m-multilingual-r2`, da IBM: gratuito,
multilíngue e bom em português). Ele também vai para a GPU:
""")

code(r'''
from sentence_transformers import SentenceTransformer

MODELO_EMBEDDING = "ibm-granite/granite-embedding-311m-multilingual-r2"
inicio = time.perf_counter()
embedder = SentenceTransformer(MODELO_EMBEDDING, device=DISPOSITIVO)
embedder.max_seq_length = 512  # limite de tokens por texto; nossos chunks cabem com folga
print(f"Modelo de embedding carregado em {time.perf_counter() - inicio:.0f} s")
memoria_gpu("Depois de carregar o modelo de embedding")
''')

md("""
**▶️ O embedding de uma frase.** Veja o formato e os primeiros números:
""")

code(r'''
vetor = embedder.encode("O gato está dormindo no sofá.", normalize_embeddings=True)
print("Formato do vetor:", vetor.shape, "→ uma lista de", len(vetor), "números")
print("Os 8 primeiros:", np.round(vetor[:8], 3))
''')

md("""
**▶️ Comparar quatro frases.** Duas dizem a mesma coisa com palavras diferentes, uma está em inglês e
uma fala de outro assunto. A tabela mostra a similaridade de cada par (quanto mais verde, mais perto):
""")

code(r'''
frases = [
    "O gato está dormindo no sofá.",
    "Um felino descansa no sofá da sala.",
    "The cat is sleeping on the couch.",
    "O Banco Central aumentou a taxa de juros.",
]
vetores_frases = embedder.encode(frases, normalize_embeddings=True)
similaridade = vetores_frases @ vetores_frases.T  # compara todas as frases com todas
rotulos = [f[:25] + "…" for f in frases]
pd.DataFrame(similaridade, index=rotulos, columns=rotulos).round(2).style.background_gradient(cmap="Greens")
''')

md("""
**▶️ A conta por trás.** Como os vetores foram **normalizados** (todos com o mesmo comprimento), a
similaridade de cosseno é só multiplicar os números par a par e somar — o chamado **produto escalar**:
""")

code(r'''
gato, felino, juros = vetores_frases[0], vetores_frases[1], vetores_frases[3]
print("'gato dormindo' × 'felino descansa':", round(float(np.dot(gato, felino)), 3))
print("'gato dormindo' × 'taxa de juros':  ", round(float(np.dot(gato, juros)), 3))
''')

md("""
**💡 O que isso significa.** "Gato dormindo" e "felino descansa" ficaram próximos **sem ter nenhuma
palavra importante em comum**, e a frase em inglês também ficou perto. Já "taxa de juros" ficou longe.
É isso que vai permitir **buscar por significado**, e não por palavra exata.

**▶️ Agora, o embedding de todos os chunks.** É aqui que a GPU faz diferença: centenas de textos
processados em lotes, ao mesmo tempo.
""")

code(r'''
inicio = time.perf_counter()
vetores_chunks = embedder.encode(
    [c["texto"] for c in chunks], normalize_embeddings=True, batch_size=32, show_progress_bar=True,
)
TEMPOS["embeddings dos chunks (s)"] = round(time.perf_counter() - inicio, 1)
print(f"{len(chunks)} chunks → matriz de vetores com formato {vetores_chunks.shape}")
print(f"Levou {TEMPOS['embeddings dos chunks (s)']} s na {'GPU' if DISPOSITIVO == 'cuda' else 'CPU'}")
''')

md("""
**💡 O que isso significa.** Cada linha dessa matriz é o "endereço no mapa de significados" de um
chunk. Um detalhe importante: **a pergunta vai ter que passar pelo mesmo modelo**. Vetores de modelos
diferentes são como coordenadas em mapas diferentes — não dá para compará-los.

> **Curiosidade:** existem modelos de embedding maiores (por exemplo, `BAAI/bge-m3`), que costumam buscar
> um pouco melhor, ao custo de mais memória e mais tempo. Trocar é mudar uma linha — e recalcular tudo.

Temos centenas de vetores. Precisamos de um lugar organizado para guardá-los e buscar neles. Vamos à §6.
""")

# ═════════════════════════════════════════════════════════════════════════════
# §6 Banco vetorial
# ═════════════════════════════════════════════════════════════════════════════
md("""
## 6. Banco vetorial: guardar os chunks para buscar depois

**🧠 Conceito.** Um **banco vetorial** guarda cada chunk junto com o seu vetor e responde muito rápido à
pergunta *"quais vetores estão mais perto deste?"*. Cada registro guarda quatro coisas:

| Campo | Exemplo | Para que serve |
|---|---|---|
| `id` | `artigo.pdf:p3:c1` | identificar o chunk |
| texto | "Os resultados mostram que…" | ser lido pelo modelo de linguagem |
| vetor | `[0.021, -0.043, …]` (768 números) | ser comparado com a pergunta |
| metadados | `{"arquivo": "artigo.pdf", "pagina": 3}` | citar a fonte |

Um grupo de registros se chama **coleção**. Usamos o **Chroma**, um banco vetorial gratuito que roda
aqui mesmo, na memória do Colab.

**🧩 Analogia.** Uma biblioteca comum organiza os livros em ordem alfabética. Um banco vetorial é uma
biblioteca organizada **por assunto**: livros sobre temas parecidos ficam na mesma prateleira, e o
bibliotecário sabe ir direto à prateleira certa.

**▶️ Criar o banco** (em memória: ele some quando a sessão do Colab termina — nada fica gravado):
""")

code(r'''
import chromadb

cliente = chromadb.EphemeralClient()
print("Banco vetorial pronto, na memória do Colab.")
''')

md("""
**▶️ Criar a coleção.** Dizemos que a proximidade deve ser medida pela similaridade de cosseno — a mesma
da §5 — e que **nós** vamos fornecer os vetores (já calculados).
""")

code(r'''
NOME_COLECAO = "aula_rag"
if NOME_COLECAO in [c.name for c in cliente.list_collections()]:
    cliente.delete_collection(NOME_COLECAO)  # ao rodar de novo, começamos do zero

colecao = cliente.create_collection(
    name=NOME_COLECAO,
    configuration={"hnsw": {"space": "cosine"}},  # medir proximidade pela similaridade de cosseno
    embedding_function=None,  # os vetores vêm da §5, não de um modelo escondido no banco
)
''')

md("""
**▶️ Guardar os chunks.** Enviamos, para cada chunk, o id, o texto, o vetor e os metadados (em lotes de
1000, para funcionar também com documentos grandes):
""")

code(r'''
LOTE = 1000
for i in range(0, len(chunks), LOTE):
    lote = chunks[i:i + LOTE]
    colecao.add(
        ids=[c["id"] for c in lote],
        documents=[c["texto"] for c in lote],
        embeddings=vetores_chunks[i:i + LOTE].tolist(),
        metadatas=[{"arquivo": c["arquivo"], "pagina": c["pagina"]} for c in lote],
    )
print("Registros no banco:", colecao.count())
''')

md("""
**👀 Um registro por dentro.** Os quatro campos da tabela lá de cima, de verdade:
""")

code(r'''
registro = colecao.get(ids=[chunks[0]["id"]], include=["documents", "metadatas", "embeddings"])
print("id:        ", registro["ids"][0])
print("metadados: ", registro["metadatas"][0])
print("texto:     ", registro["documents"][0][:150], "…")
print("vetor:     ", np.round(registro["embeddings"][0][:6], 3), f"… ({len(registro['embeddings'][0])} números)")
''')

md("""
**💡 O que isso significa.** O banco **não entende texto**: ele compara vetores. O texto e os metadados
vão junto só para, depois da busca, sabermos **o que** foi encontrado e **de onde** veio.

> **Curiosidade:** com milhões de vetores, comparar a pergunta com todos seria lento. Por isso bancos
> vetoriais usam índices que acham os vizinhos mais próximos **sem olhar um por um**.

O material está preparado. Agora vem a parte que acontece **a cada pergunta**: a busca (§7).
""")

# ═════════════════════════════════════════════════════════════════════════════
# §7 Retrieval
# ═════════════════════════════════════════════════════════════════════════════
md("""
## 7. Retrieval: encontrar os trechos que respondem à pergunta

**🧠 Conceito.** A pergunta também vira um vetor — **com o mesmo modelo** dos chunks. O banco devolve
os **k** chunks mais próximos dela (os **top-k**). Isso é uma **busca semântica** (busca por significado)
e, no RAG, essa etapa se chama **retrieval** (recuperação) — é o "R" de RAG.

**🧩 Analogia.** Você chega ao bibliotecário e diz: *"me traga os 4 textos que mais têm a ver com esta
pergunta"*. Ele não procura a palavra exata na capa; ele entende o **assunto** e vai à prateleira certa.

| Busca por palavra-chave | Busca semântica |
|---|---|
| procura as **mesmas palavras** | procura o **mesmo sentido** |
| "carro" não encontra "automóvel" | "carro" encontra "automóvel" |
| ótima para nomes, siglas e códigos exatos | ótima para perguntas em linguagem natural |

**▶️ Escreva a pergunta.** A sugestão abaixo é sobre o artigo de exemplo. **Se você enviou outro
documento, troque por uma pergunta sobre ele.**
""")

code(r'''
PERGUNTA = "Quais modelos de embedding e de linguagem tiveram o melhor desempenho no estudo?"  # @param {type:"string"}
print("Pergunta:", PERGUNTA)
''')

md("""
**▶️ A pergunta vira um vetor** — do mesmo tamanho dos vetores dos chunks:
""")

code(r'''
vetor_pergunta = embedder.encode(PERGUNTA, normalize_embeddings=True)
print("Formato do vetor da pergunta:", vetor_pergunta.shape)
''')

md("""
**▶️ Pedir ao banco os `K` chunks mais próximos.** O banco devolve a **distância** de cada um; como usamos
cosseno, **similaridade = 1 − distância**.
""")

code(r'''
K = 4  # @param {type:"slider", min:1, max:10, step:1}

resultado = colecao.query(
    query_embeddings=[vetor_pergunta.tolist()], n_results=K,
    include=["documents", "metadatas", "distances"],
)
''')

md("""
**👀 O que o banco encontrou:**
""")

code(r'''
pd.DataFrame({
    "arquivo": [m["arquivo"] for m in resultado["metadatas"][0]],
    "página": [m["pagina"] for m in resultado["metadatas"][0]],
    "similaridade": [round(1 - d, 3) for d in resultado["distances"][0]],
    "início do trecho": [t[:120] + "…" for t in resultado["documents"][0]],
}, index=range(1, len(resultado["ids"][0]) + 1))
''')

md("""
**👀 O trecho mais próximo, inteiro:**
""")

code(r'''
print(resultado["documents"][0][0])
''')

md("""
**▶️ Guardar a busca numa função.** Você acabou de ver os três passos (pergunta → vetor → k vizinhos).
Vamos juntá-los em `buscar()`, para usar daqui em diante:
""")

code(r'''
def buscar(pergunta, k=K):
    """Retrieval: pergunta → vetor → os k chunks mais próximos, com endereço e similaridade."""
    vetor = embedder.encode(pergunta, normalize_embeddings=True)
    r = colecao.query(query_embeddings=[vetor.tolist()], n_results=k,
                      include=["documents", "metadatas", "distances"])
    return [{"texto": t, **m, "similaridade": round(1 - d, 3)}
            for t, m, d in zip(r["documents"][0], r["metadatas"][0], r["distances"][0])]
''')

md("""
**▶️ E se a pergunta não tiver nada a ver com o documento?** Compare as similaridades:
""")

code(r'''
for pergunta in [PERGUNTA, "Qual é a receita de bolo de cenoura?"]:
    notas = [t["similaridade"] for t in buscar(pergunta)]
    print(f"{pergunta[:60]:<62} similaridades: {notas}")
''')

md("""
**💡 O que isso significa.** A pergunta sobre o documento tem similaridades maiores. Mas repare: o banco
**sempre devolve k trechos**, mesmo quando nenhum é bom. Ele não sabe dizer "não achei". Por isso, na
§9, o prompt vai autorizar o modelo a responder **"não encontrei"**.

Sobre o `K`:

| K pequeno (1–2) | K grande (8–10) |
|---|---|
| contexto enxuto e focado | mais chance de trazer o trecho certo |
| risco de faltar informação | mais texto irrelevante para o modelo ler |

Temos os trechos certos. Agora precisamos entregá-los ao modelo de um jeito organizado (§8).
""")

# ═════════════════════════════════════════════════════════════════════════════
# §8 Contexto
# ═════════════════════════════════════════════════════════════════════════════
md("""
## 8. Contexto: organizar os trechos que o modelo vai ler

**🧠 Conceito.** O **contexto** é o conjunto de trechos recuperados, organizado para o modelo ler. Cada
trecho ganha um **número** — `[1]`, `[2]`, … — e o seu **endereço** (arquivo, página). O número é o que
vai permitir ao modelo **citar** a fonte de cada afirmação.

**🧩 Analogia.** Na prova com consulta, é a folha onde você colou os recortes do material, numerados e
com a página anotada ao lado de cada um.

**▶️ Uma função para montar o contexto:**
""")

code(r'''
def montar_contexto(trechos):
    """Junta os trechos numerados [1], [2]… com o endereço de cada um."""
    return "\n\n".join(
        f"[{n}] ({t['arquivo']}, p. {t['pagina']})\n{t['texto']}"
        for n, t in enumerate(trechos, start=1)
    )
''')

md("""
**👀 O contexto da nossa pergunta:**
""")

code(r'''
trechos = buscar(PERGUNTA)
contexto = montar_contexto(trechos)
print(contexto[:1500], "…" if len(contexto) > 1500 else "")
print(f"\nO contexto tem {len(contexto)} caracteres, ou {len(tokenizer(contexto).input_ids)} tokens.")
''')

md("""
**💡 O que isso significa.** Este é **todo o conhecimento** que o modelo vai receber sobre o seu documento
— só estes trechos, não o documento inteiro. Se a resposta não estiver aqui, o modelo não tem como
sabê-la. Por isso a qualidade da busca (§7) importa tanto.

Falta dizer ao modelo **o que fazer** com esses trechos. Isso é o prompt (§9).
""")

# ═════════════════════════════════════════════════════════════════════════════
# §9 Prompt
# ═════════════════════════════════════════════════════════════════════════════
md("""
## 9. Prompt: as instruções, os trechos e a pergunta

**🧠 Conceito.** O **prompt** é tudo o que o modelo lê antes de responder. No RAG, ele tem três partes:

1. **Regras** (a mensagem de *sistema*): como o modelo deve se comportar.
2. **Contexto:** os trechos numerados da §8.
3. **Pergunta.**

A regra mais importante é: *responda **somente** com base nos trechos*. Isso se chama **grounding**
(ancoragem): a resposta fica **ancorada** no material recuperado, e não na "memória" do modelo.

**🧩 Analogia.** São as instruções no topo da prova: *"Use apenas o material de consulta. Indique a
página de cada resposta. Se a resposta não estiver no material, escreva: não encontrei."*

**▶️ As regras:**
""")

code(r'''
REGRAS = """Você é um assistente que responde perguntas usando SOMENTE os trechos numerados fornecidos.
Regras:
1. Responda em português, de forma clara e objetiva.
2. Depois de cada afirmação, indique o número do trecho que a sustenta, por exemplo [1] ou [2][3].
3. Se os trechos não trouxerem a resposta, diga exatamente: "Não encontrei essa informação nos documentos enviados."
4. Não use conhecimento que não esteja nos trechos."""
''')

md("""
**▶️ Montar as mensagens.** As regras vão como mensagem de sistema; os trechos e a pergunta, como
mensagem do usuário:
""")

code(r'''
def montar_mensagens(pergunta, contexto):
    """O prompt do RAG: regras (sistema) + trechos e pergunta (usuário)."""
    return [
        {"role": "system", "content": REGRAS},
        {"role": "user", "content": f"Trechos:\n\n{contexto}\n\nPergunta: {pergunta}"},
    ]


mensagens = montar_mensagens(PERGUNTA, contexto)
''')

md("""
**👀 O prompt real.** É **exatamente** este texto que o modelo vai ler — com as marcações especiais
(`<|im_start|>`, `<|im_end|>`) que separam as mensagens no formato em que ele foi treinado:
""")

code(r'''
prompt_real = tokenizer.apply_chat_template(
    mensagens, tokenize=False, add_generation_prompt=True, enable_thinking=False,
)
print(prompt_real)
''')

md("""
**▶️ De que tamanho ficou o prompt?**
""")

code(r'''
print("O prompt tem", len(tokenizer(prompt_real).input_ids), "tokens.")
''')

md("""
**💡 O que isso significa.** Não há mágica: o RAG é, no fim, **um texto bem montado**. Cada regra evita
um problema:

| Regra | Problema que ela evita |
|---|---|
| Só os trechos (1 e 4) | o modelo completar com "memória" ou inventar |
| Citar `[n]` (2) | resposta sem fonte, impossível de conferir |
| Frase exata de recusa (3) | o modelo "chutar" quando o documento não responde |

Agora sim: vamos pedir ao modelo que responda (§10).
""")

# ═════════════════════════════════════════════════════════════════════════════
# §10 Geração
# ═════════════════════════════════════════════════════════════════════════════
md("""
## 10. Geração: o modelo escreve a resposta, na GPU

**🧠 Conceito.** O modelo escreve **um token por vez**. A cada passo, ele calcula qual pedaço de palavra
é o mais provável de vir a seguir — considerando o prompt inteiro e o que já escreveu — e repete até
terminar. Isso é a **geração**. O *streaming* mostra os tokens aparecendo conforme são escritos.

**🧩 Analogia.** É o "completar automático" do teclado do celular — só que muito mais capaz, e lendo as
regras e os trechos antes de começar.

**▶️ Gerar a resposta com RAG** (e medir a velocidade):
""")

code(r'''
inicio = time.perf_counter()
resposta = gerar(mensagens)
segundos = time.perf_counter() - inicio
TEMPOS["resposta com RAG (s)"] = round(segundos, 1)
TEMPOS["tokens por segundo"] = round(len(tokenizer(resposta).input_ids) / segundos, 1)
print(f"\n⏱ {segundos:.1f} s · cerca de {TEMPOS['tokens por segundo']} tokens por segundo")
memoria_gpu("Depois da geração")
''')

md("""
**💡 O que isso significa.** Tudo aconteceu **dentro do Colab**: nenhum texto saiu para um serviço
externo. A velocidade depende da GPU que o Colab te entregou — numa T4, dezenas de tokens por segundo;
na CPU, muito menos. A memória subiu um pouco: durante a geração o modelo guarda cálculos
intermediários sobre o prompt (que ficam maiores quanto mais longo o prompt).

A resposta traz números entre colchetes. Vamos conferir de onde eles vêm (§11).
""")

# ═════════════════════════════════════════════════════════════════════════════
# §11 Fontes
# ═════════════════════════════════════════════════════════════════════════════
md("""
## 11. Fontes: da resposta de volta à página

**🧠 Conceito.** Cada `[n]` da resposta é uma **citação**: aponta para o trecho número *n* do contexto
— e, portanto, para um arquivo e uma página. Conferir as citações é o que torna a resposta
**verificável**. Mas atenção: o modelo pode errar — citar um número que não existe, ou não citar nada.

**🧩 Analogia.** É a nota de rodapé de um trabalho escolar: o leitor desconfiado pode ir até a página
e conferir.

**▶️ Encontrar as citações.** A expressão `\\[(\\d+)\\]` procura "um número entre colchetes" no texto
(é uma *expressão regular*, um padrão de busca em texto):
""")

code(r'''
import re


def fontes_citadas(resposta, trechos):
    """Acha os [n] da resposta e separa os válidos (existem no contexto) dos inválidos."""
    numeros = sorted({int(n) for n in re.findall(r"\[(\d+)\]", resposta)})
    validos = [n for n in numeros if 1 <= n <= len(trechos)]
    invalidos = [n for n in numeros if n not in validos]
    return validos, invalidos
''')

md("""
**👀 As fontes da resposta**, com arquivo e página:
""")

code(r'''
validos, invalidos = fontes_citadas(resposta, trechos)
display(pd.DataFrame([
    {"citação": f"[{n}]", "arquivo": trechos[n - 1]["arquivo"], "página": trechos[n - 1]["pagina"],
     "trecho": trechos[n - 1]["texto"][:120] + "…"}
    for n in validos
]))
if invalidos:
    print("⚠️ Citações que não correspondem a nenhum trecho enviado:", invalidos)
if not validos:
    print("⚠️ A resposta não citou nenhum trecho: confira com cuidado (ou foi uma recusa).")
''')

md("""
**▶️ Recuperado não é o mesmo que citado:**
""")

code(r'''
todos = list(range(1, len(trechos) + 1))
print("Trechos recuperados (§7):", todos)
print("Trechos citados:         ", validos)
print("Recuperados, mas não usados:", [n for n in todos if n not in validos])
''')

md("""
**💡 O que isso significa.** Nem todo trecho encontrado pela busca é útil — o modelo usou só alguns.
E citar não é garantia de acerto: o grounding **reduz** muito os erros, mas **não os elimina**. O modelo
ainda pode interpretar mal um trecho. Por isso mostramos a página: para você conferir.
""")

# ═════════════════════════════════════════════════════════════════════════════
# §12 Com × sem RAG
# ═════════════════════════════════════════════════════════════════════════════
md("""
## 12. Com RAG × sem RAG: a mesma pergunta, dois resultados

**🧠 Conceito.** Para ver o efeito do RAG, fazemos a **mesma pergunta** ao **mesmo modelo** — uma vez
sozinho, outra vez com os trechos e as regras.

**▶️ A pergunta, sem RAG:**
""")

code(r'''
sem_rag = gerar([{"role": "user", "content": PERGUNTA}], max_tokens=300)
''')

md("""
**👀 Lado a lado:**
""")

code(r'''
display(HTML(
    "<table><tr><th style='width:50%'>🤖 Modelo sozinho</th><th>📚 Modelo + RAG</th></tr>"
    f"<tr><td style='vertical-align:top;white-space:pre-wrap'>{html.escape(sem_rag)}</td>"
    f"<td style='vertical-align:top;white-space:pre-wrap'>{html.escape(resposta)}</td></tr></table>"
))
''')

md("""
**▶️ E quando o documento não responde?** Uma pergunta que o modelo **sabe** responder de memória, mas
que **não está** no documento:
""")

code(r'''
FORA = "Qual é a capital da Austrália?"
resposta_fora = gerar(montar_mensagens(FORA, montar_contexto(buscar(FORA))))
''')

md("""
**💡 O que isso significa.**

- Sem RAG, o modelo responde de memória: pode acertar, errar ou inventar — e **não mostra fonte**.
- Com RAG, a resposta vem **do documento** e **aponta a página**.
- Na pergunta sobre a Austrália, o comportamento certo é **recusar** ("Não encontrei essa informação…"),
  mesmo o modelo sabendo a resposta: a regra é responder **só com o material**. Se ele respondeu
  "Camberra" mesmo assim, você acabou de ver um limite real do grounding (§14).

Recusar, aqui, **não é defeito**: é o sistema sendo honesto sobre o que o documento diz.
""")

# ═════════════════════════════════════════════════════════════════════════════
# §13 Pipeline completo
# ═════════════════════════════════════════════════════════════════════════════
md("""
## 13. O RAG completo em uma função

Agora que você construiu e viu cada peça, dá para juntar tudo. Repare que a função abaixo **não tem
nada novo** — só chama o que você já fez:

```
pergunta ─► buscar() ─► montar_contexto() ─► montar_mensagens() ─► gerar() ─► fontes_citadas()
              §7              §8                   §9                §10            §11
```
""")

code(r'''
def perguntar(pergunta, k=K):
    """O RAG inteiro, com as peças construídas em cada seção."""
    trechos = buscar(pergunta, k)                                       # §7 retrieval
    mensagens = montar_mensagens(pergunta, montar_contexto(trechos))    # §8 contexto + §9 prompt
    resposta = gerar(mensagens)                                         # §10 geração, na GPU
    validos, _ = fontes_citadas(resposta, trechos)                      # §11 fontes
    print("\n📚 Fontes:" if validos else "\n📚 Nenhuma fonte citada.")
    for n in validos:
        print(f"   [{n}] {trechos[n - 1]['arquivo']}, p. {trechos[n - 1]['pagina']}")
    return resposta
''')

md("""
**▶️ Faça as suas perguntas.** Troque o texto e rode quantas vezes quiser. Experimente também uma
pergunta que o documento **não** responde.
""")

code(r'''
MINHA_PERGUNTA = "Quais bases de dados em português foram usadas na avaliação?"  # @param {type:"string"}
_ = perguntar(MINHA_PERGUNTA)
''')

# ═════════════════════════════════════════════════════════════════════════════
# §14 Limites, próximos passos e glossário
# ═════════════════════════════════════════════════════════════════════════════
md("""
## 14. Limites, próximos passos e glossário

### Onde um RAG pode errar

| Sintoma | Causa provável | O que olhar |
|---|---|---|
| Resposta sem sentido ou "não encontrei" para algo que está no documento | texto mal extraído (PDF escaneado, colunas misturadas) | o texto da §3 |
| A busca traz trechos que não respondem | chunk pequeno demais (sem contexto) ou grande demais (misturando assuntos) | `TAMANHO_CHUNK` na §4 |
| Falta informação na resposta | `K` pequeno demais | `K` na §7 |
| Resposta confusa com muitos trechos | `K` grande demais | `K` na §7 |
| Afirmação que não está no trecho citado | o modelo interpretou mal (o grounding reduz, não elimina) | a tabela de fontes da §11 |
| Respostas fracas em geral | modelo pequeno (ex.: sem GPU, usamos o de 1,7 bilhão) | o modelo escolhido na §2 |
| Pergunta vaga traz trechos aleatórios | a pergunta não tem "assunto" suficiente | reescrever a pergunta |

### Curiosidades para depois da aula

> **Curiosidade:** em aplicações reais existem estratégias mais sofisticadas — por exemplo, **reordenar**
> os trechos encontrados com um segundo modelo (*reranking*) ou **combinar** busca por significado com
> busca por palavra-chave (*busca híbrida*).
>
> **Curiosidade:** frameworks como **LangChain** e **LlamaIndex** fazem as etapas desta aula em poucas
> linhas. Agora você sabe o que eles fazem por baixo.
>
> **Curiosidade:** para saber se um RAG está bom, monta-se um conjunto de perguntas com as respostas
> esperadas e **mede-se** a qualidade a cada mudança.
""")

md("""
### 📖 Glossário

| Termo | Em uma linha |
|---|---|
| **RAG** | Geração Aumentada por Recuperação: buscar trechos relevantes e entregá-los ao modelo antes de ele responder. |
| **LLM** | Modelo de linguagem grande: programa que aprendeu a escrever lendo muitos textos. |
| **Alucinação** | Quando o modelo inventa uma informação com aparência de verdade. |
| **Token** | Pedaço de palavra: a unidade que o modelo lê e escreve. |
| **GPU / VRAM** | Processador que faz muitas contas ao mesmo tempo / a memória dele, onde o modelo precisa caber. |
| **Documento** | O arquivo com o conteúdo (PDF, TXT, MD). |
| **Metadados** | Informações sobre o texto, como arquivo e página; permitem citar a fonte. |
| **Chunk** | Pedaço do texto: a unidade de busca. |
| **Sobreposição** | Trecho repetido entre chunks vizinhos para não partir ideias ao meio. |
| **Embedding / vetor** | Lista de números que representa o significado de um texto. |
| **Similaridade de cosseno** | Nota de proximidade entre dois vetores: perto de 1 = mesmo sentido. |
| **Banco vetorial / coleção** | Onde os chunks e seus vetores ficam guardados para busca / um grupo desses registros. |
| **Busca semântica** | Busca por significado, e não por palavra exata. |
| **Retrieval / top-k** | A etapa de busca do RAG / os k trechos mais próximos da pergunta. |
| **Contexto** | Os trechos recuperados, numerados, que o modelo recebe. |
| **Prompt** | Tudo o que o modelo lê: regras + contexto + pergunta. |
| **Grounding** | Ancorar a resposta nos trechos, proibindo o uso da "memória" do modelo. |
| **Geração / streaming** | O modelo escrevendo token por token / mostrar os tokens conforme saem. |
| **Citação** | O `[n]` que liga uma afirmação ao trecho, ao arquivo e à página. |
| **Recusa** | Responder "não encontrei" quando o documento não traz a resposta. |
""")

md(f"""
### 🎯 Recapitulando

```
documento → chunks → embeddings → banco vetorial → pergunta → retrieval → contexto → prompt → LLM → resposta com fonte
```

Você construiu cada uma dessas etapas, viu o resultado de cada uma e rodou tudo na GPU do Colab. 🎉

**Referências e material**
- Lewis et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.* [arXiv:2005.11401](https://arxiv.org/abs/2005.11401)
- Medeiros & Oliveira (2025). *Comparação de Modelos de Embeddings e LLMs para Geração Aumentada por Recuperação em Português.* SEMISH 2025. [SOL/SBC](https://sol.sbc.org.br/index.php/semish/article/view/36829)
- Repositório da aula (código, slides e documentação): [{URL_REPO}]({URL_REPO})

---
*Material do Webinário CIIA — Aula prática de RAG.*
""")

md("""
---
### 🛠️ Para quem mantém este material: diagnóstico da execução

Esta célula não faz parte da aula. Ela resume o ambiente e os tempos desta execução — cole a saída na
issue de validação do repositório.
""")

code(r'''
import platform, sentence_transformers, transformers

pd.Series({
    "data": time.strftime("%Y-%m-%d %H:%M"), "python": platform.python_version(),
    "GPU": torch.cuda.get_device_name(0) if DISPOSITIVO == "cuda" else "nenhuma (CPU)",
    "torch": torch.__version__, "transformers": transformers.__version__,
    "sentence-transformers": sentence_transformers.__version__, "chromadb": chromadb.__version__,
    "LLM": MODELO_LLM, "embedding": MODELO_EMBEDDING, "páginas": len(paginas), "chunks": len(chunks),
    **TEMPOS,
    "pico de VRAM (GB)": round(torch.cuda.max_memory_allocated() / 1e9, 1) if DISPOSITIVO == "cuda" else 0,
})
''')


# ═════════════════════════════════════════════════════════════════════════════
# Montagem do .ipynb
# ═════════════════════════════════════════════════════════════════════════════
def celula(tipo, fonte):
    base = {"cell_type": tipo, "metadata": {}, "source": fonte.splitlines(keepends=True)}
    if tipo == "code":
        base.update(execution_count=None, outputs=[])
    return base


notebook = {
    "cells": [celula(t, f) for t, f in celulas],
    "metadata": {
        "accelerator": "GPU",
        "colab": {"gpuType": "T4", "provenance": [], "toc_visible": True},
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}
for i, c in enumerate(notebook["cells"]):
    c["id"] = f"c{i:03d}"

DESTINO.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

linhas = [len([l for l in f.splitlines() if l.strip()]) for t, f in celulas if t == "code"]
print(f"{DESTINO} gerado com {len(celulas)} células ({len(linhas)} de código; "
      f"linhas por célula de código: mediana {statistics.median(linhas):g}, máximo {max(linhas)})")
