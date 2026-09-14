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

## Indexação e busca

### A indexação demora quase 20 minutos
- **Causa:** gerar os 556 embeddings do `bge-m3` em CPU levou 1141 s na 1ª execução e 1111 s na 2ª.
- **Resposta:** "É esperado sem GPU. Rode `scripts/02_indexar.py` uma vez; ele grava a coleção em `chroma_db/` e o notebook só a reabre (`REINDEXAR = False`)."

### O filtro `idioma = pt` não traz nada
- **Causa:** ainda não há artigos em português no corpus. O resultado vazio é o comportamento esperado e não gera erro (E3 critério 3.6).
- **Resposta:** "Ainda não há artigos em português. Esse filtro volta vazio de propósito."

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
