# Troubleshooting

Cada entrada abaixo aconteceu de verdade durante a montagem e a verificação do material (etapas E0–E9 de [VERIFICACAO.md](VERIFICACAO.md)). As respostas estão escritas para o João copiar e colar no chat.

## Ollama

### "Não consegui falar com o Ollama em http://localhost:11434"
- **Quando aparece:** o aplicativo Ollama está fechado. Os scripts, o notebook e o app mostram essa mensagem em vez de um traceback (E6 critério 6.7, E8 critério 8.8).
- **Resposta:** "Abra o aplicativo Ollama (Windows/macOS) ou rode `ollama serve` no terminal (Linux) e tente de novo. Para conferir, rode `ollama list`."

### "O modelo 'X' não está baixado"
- **Resposta:** "Rode `ollama pull X`. Os modelos da aula são `bge-m3`, `qwen2.5:3b` e `qwen2.5:1.5b`."

### Mudei `OLLAMA_MODELS` e o Ollama não enxerga os modelos
- **Causa:** o servidor só lê a variável quando inicia.
- **Resposta:** "Feche o Ollama pelo ícone da bandeja (no Windows, confira no Gerenciador de Tarefas que não ficou nenhum processo `ollama`) e abra de novo. Depois rode `ollama list`."

### A primeira resposta demora muito
- **Causa:** o modelo está sendo carregado na RAM. Nesta máquina (8 GB, CPU), as cargas de modelo registradas no log do Ollama levaram de 40 a 80 s. Trocar entre o `qwen2.5:3b` e o `qwen2.5:1.5b` recarrega o modelo e custa o mesmo tempo de novo. Os números estão em [medicoes.md](medicoes.md).
- **Resposta:** "É o carregamento do modelo, só na primeira pergunta. Na aula, fazemos uma pergunta de aquecimento antes de começar. Evite alternar entre os dois modelos."

### Tudo fica lento e a memória livre cai para menos de 1 GB
- **Causa:** com 8 GB de RAM, o `bge-m3` e o `qwen2.5` carregados juntos, mais o navegador, deixaram entre 0,22 e 0,68 GB livres nas medições (E9, `docs/evidencias/E9/medicao_*.json`). Nessas condições, o 3b chegou a gerar só 3,0 tokens/s.
- **Resposta:** "Feche abas e programas pesados. Se continuar lento, troque para o `qwen2.5:1.5b` na barra lateral do app ou em `config.py`."

## Ambiente Python

### `pip install -r requirements.txt` demora muito
- **Causa:** o `chromadb` e o `shap` trazem muitas dependências (onnxruntime, numba, scikit-learn, pyarrow…). Nesta máquina, a primeira instalação passou de 50 minutos: o processo do pip começou às 23h58 e terminou antes da checagem das 01h01. Numa segunda instalação em `.venv` novo, com os pacotes já no cache do pip, foram 1311 s, cerca de 22 min (`docs/evidencias/E10/readme_do_zero.txt`). Quase todo esse tempo foi na fase "Installing collected packages", que é lenta no Windows.
- **Resposta:** "É normal demorar. Deixe rodando; não cancele no meio. Se cancelar, rode o mesmo comando de novo."

### `ModuleNotFoundError` ao abrir o notebook
- **Causa:** o kernel escolhido não é o do `.venv`.
- **Resposta:** "No VS Code, clique no seletor de kernel (canto superior direito) e escolha **Python (webinario-rag)**. Se ele não aparecer, rode `python -m ipykernel install --user --name webinario-rag --display-name \"Python (webinario-rag)\"` com o `.venv` ativo."

### Acentos aparecem como `Ã§`, `Ã£` no terminal do Windows
- **Causa:** o PowerShell 5 decodifica a saída do Python com a página de código do sistema (aconteceu com `Tee-Object` na etapa E2).
- **Resposta:** "Antes de rodar o script, execute `$env:PYTHONIOENCODING='utf-8'` e `chcp 65001` no mesmo terminal."

### `python -c "..."` com aspas quebra no PowerShell
- **Causa:** o PowerShell interpreta as aspas e as chaves de f-strings.
- **Resposta:** "Use os scripts da pasta `scripts/` em vez de `python -c`."

### O ambiente diz que o pacote está instalado, mas o import falha ou acusa integridade corrompida
- **Causa:** os diretórios de código de algumas bibliotecas sumiram do `.venv`, mas as pastas `.dist-info` continuaram intactas (incidente A1-00). Ferramentas como o `pip` acham que os pacotes ainda estão lá.
- **Resposta:** "Ocorreu uma corrupção no ambiente virtual (arquivos ausentes). Para reparar, rode o comando: `pip install --force-reinstall --no-deps -r requirements.lock`. Ele força a reinstalação de todos os pacotes listados, sem tocar no pip e ferramentas base."

## Indexação e busca

### A indexação demora mais de 20 minutos
- **Causa:** gerar os 659 embeddings do `bge-m3` em CPU levou **1420 s (23,7 min)** na medição mais recente desta máquina, com o corpus de 8 artigos. No corpus anterior, de 6 artigos e 556 embeddings, eram 1141 s e 1111 s (`docs/evidencias/E2/02_indexar_execucao1.txt`, `02_indexar_execucao2.txt`).
- **Resposta:** "É esperado sem GPU: cerca de 24 minutos nesta máquina. Rode `scripts/02_indexar.py` uma vez, **fora da aula**; ele grava a coleção em `chroma_db/` e o notebook a reabre em vez de reindexar."
- **Cuidado:** hoje o notebook só deixa de reindexar se `REINDEXAR = False` **e** a contagem da coleção conferir com o número de chunks; basta divergir para ele reindexar ao vivo. Correção em [#40](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/40).
- **De onde vêm os 1420 s:** do resumo da bateria `ferramentas/rodar_scripts.sh` de 2026-09-16 (`02_indexar.py → exit 0 em 1420s`), com a contagem confirmada por `verificar.py e2` (659/659). O arquivo `docs/evidencias/E7/log_02_indexar.txt` cita o valor, mas é uma **reconstrução** — a saída original foi sobrescrita por um `git checkout`, como a nota no fim do próprio arquivo registra.

### O filtro `idioma = pt` traz pouca coisa, ou eu esperava que viesse vazio
- **Causa:** o corpus tem **2 artigos em português** desde o T12/#12 (`rocha2025_ragsft.pdf`, SBBD 2025; `medeiros2025_embeddings_pt.pdf`, SEMISH 2025), que respondem por 103 dos 659 chunks indexados. `idioma = pt` recupera trechos de verdade — só de dois artigos, contra seis em inglês. Quem lembra da versão antiga do material (corpus só em inglês) espera resultado vazio e estranha.
- **Resposta:** "Traz sim: dois dos oito artigos estão em português. O filtro que volta vazio de propósito é um que não casa com nada, por exemplo `ano >= 2030` — é o caso que o critério 3.6 usa para mostrar que filtro sem correspondência devolve lista vazia sem erro."
- **Onde conferir:** `ferramentas/verificar.py e3` imprime os dois casos lado a lado — `3.6 filtro ano>=2030 (sem artigos): 0 resultados, sem erro` e `3.6b filtro idioma=pt (com artigos, T12/#12): 4 resultados, todos pt = True`. Os 4 são o `k` pedido na chamada, não o total disponível: com o filtro de idioma a coleção tem 103 chunks para escolher.

### A busca em dois estágios "perdeu" o artigo certo
- **Causa:** o 1º estágio escolhe os artigos pelos **resumos**. Se o resumo não menciona o assunto, o artigo fica de fora. Caso registrado na etapa E4: "Recuperar mais documentos sempre melhora a resposta do modelo?" encontra o *Lost in the Middle* na busca simples, mas não nos dois estágios.
- **Resposta:** "É uma limitação real da técnica, e um bom tema para discutir: resumo bom é pré-requisito."

## LLM e prompts

### O modelo respondeu em inglês ou disse "Não encontrei" sem motivo
- **Causa:** com todas as instruções dentro da mensagem do usuário, o `qwen2.5:3b` às vezes copiava frases dos trechos em inglês. Uma variação do prompt fez o modelo recusar uma pergunta que os trechos respondiam. A solução adotada em `rag.montar_mensagens()` foi colocar as instruções em uma mensagem **system** separada.
- **Resposta:** "Modelos pequenos são sensíveis ao formato do prompt. No nosso código, as instruções vão na mensagem de sistema."

### A resposta cita `[n]` literalmente ou cita o trecho errado
- **Causa:** limitação de um modelo de 3B parâmetros.
- **Resposta:** "Confira as fontes no expander. Esse é um dos motivos para avaliar com métricas de fidelidade (bloco 8)."

## Streamlit

### `ConnectionResetError: [WinError 10054]` no terminal do Streamlit
- **Causa:** ruído do asyncio no Windows quando o navegador recarrega ou fecha a aba. O app continua funcionando.
- **Resposta:** "Pode ignorar."

### Pressionar Enter no campo de pergunta não enviou
- **Causa:** no painel de navegador usado nos testes, o Enter não disparou o envio e só o botão de enviar funcionou.
- **Resposta:** "Clique na seta à direita do campo de pergunta."

### O app mostra "External URL" com o IP da máquina
- **Causa:** por padrão, o Streamlit escuta em todas as interfaces de rede.
- **Resposta:** "Para expor só na sua máquina, rode `streamlit run app.py --server.address localhost`."
