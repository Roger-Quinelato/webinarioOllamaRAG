# Troubleshooting

## Ollama não responde

Ollama fornece somente embeddings. Inicie o serviço e confirme `bge-m3`:

```powershell
ollama pull bge-m3
python scripts/00_checar_ambiente.py
```

Não tente resolver falha de embedding instalando modelo de chat local. A UI e o
router remoto dependem desta fronteira apenas para embeddings.

## Nenhuma chave de geração disponível

Defina ao menos uma de `OPENAI_API_KEY`, `NVIDIA_API_KEY` ou `GEMINI_API_KEY`
no ambiente ou em `st.secrets`. A aplicação mostra orientação segura e não
inicia consulta. Nunca registre o valor.

## OpenAI, NVIDIA ou Gemini retorna erro

Confira credencial, quota e conectividade. Antes do primeiro token, HTTP 429,
timeout, rede e indisponibilidade acionam o próximo provider na ordem OpenAI,
NVIDIA, Gemini. Depois do primeiro token, a UI preserva **Resposta Parcial**.
Não há fallback automático para geração local. O fallback válido usa somente
providers remotos.

`OPENAI_TIMEOUT`, `NVIDIA_TIMEOUT` e `GEMINI_TIMEOUT` usam segundos e podem vir
do ambiente ou de `st.secrets`. Sem `OPENAI_TIMEOUT` e `GEMINI_TIMEOUT` vale o
padrão do SDK; sem `NVIDIA_TIMEOUT` vale 30 s, para não esperar falhas de 90 s.
O SDK Gemini recebe internamente o valor convertido para milissegundos.

Cada provider descreve apenas o que aconteceu ("limite de requisições", "sem
saldo", "não foi possível conectar"). Quem decide o próximo passo é o roteador:
só ele avança para o próximo provider ou devolve "Nenhum provider de geração
está disponível". Um `retry-after` de até 2 s, vindo de cabeçalho ou dos
detalhes do erro (`RetryInfo.retryDelay` no Gemini), permite uma repetição no
mesmo provider; sem esse atraso, o roteador avança direto.

A OpenAI sem saldo (`credit_balance_exhausted` ou `insufficient_quota`) aparece
como "sem saldo ou cota". Recarregue a conta ou remova `OPENAI_API_KEY` para não
gastar a primeira tentativa de cada pergunta.

### Diagnóstico pelo log

O logger `rag.geracao` registra, em nível INFO, provider, modelo, Base Ativa,
quantidade de chunks, tentativa, tempo até o primeiro token, Recusa e Resposta
Parcial. Para o provider NVIDIA registra também quantos eventos o stream trouxe
e se algum indicou `finish_reason`, o que separa encerramento sem conclusão de
timeout. O log nunca contém chave, prompt, chunk nem texto da resposta. Ele sai
no stderr do processo, então rode o Streamlit num terminal visível durante a
demonstração.

Se a NVIDIA falhar com frequência, confira `NVIDIA_MODEL`: prefira um modelo de
instrução, como o padrão `meta/llama-3.1-8b-instruct`, a um modelo de
*reasoning*, que demora a emitir o primeiro token.

O Gemini roda com chamada automática de funções desligada, pois o pipeline não
usa ferramentas; isso evita o aviso de AFC do SDK em cada chamada.

## Rollback para geração local (tag `legacy-pre-openai`)

O rollback não é imediato. O caminho legado espera a coleção Chroma `artigos_rag`
(`config.NOME_COLECAO`), que pode não existir no `chroma_db/` da máquina: a
migração usa coleções `artigos_rag_hibrido_*` e `artigos_rag_openai*`, e
`chroma_db/` não é versionado. Sem `artigos_rag`, `rag.abrir_colecao` cria uma
coleção vazia e os scripts `03`–`07` e o notebook devolvem zero resultados sem
erro.

Antes de depender do rollback:

1. Liste as coleções da máquina que fará a demonstração:

   ```powershell
   python -c "import chromadb; print([c.name for c in chromadb.PersistentClient('chroma_db').list_collections()])"
   ```

2. Se `artigos_rag` não estiver na lista, reindexe com `python scripts/02_indexar.py`
   depois de `git checkout legacy-pre-openai`. Essa etapa leva cerca de 19 a 24
   minutos e exige os modelos de chat locais (`qwen2.5:1.5b`, `qwen2.5:3b`).
3. Não apague coleções existentes: nenhuma coleção nova ou antiga deve ser
   removida durante a migração.

Não se sabe se a ausência de `artigos_rag` decorre da migração ou de recriação
do diretório local; o histórico de `chroma_db/` não é versionado, então nenhuma
causa é atribuída.

## Corpus Oficial incompatível

Coleção precisa declarar `Ollama`, `bge-m3`, dimensão `1024`, esquema
`bge-m3-v1` e status `ready`. Rode `python scripts/02_indexar_hibrido.py` para
reindexar explicitamente.

## Upload de PDFs

Upload está desativado no Streamlit para o treino. A flag
`UPLOADS_STREAMLIT_HABILITADOS=False` preserva esse estado. Índice de Sessão e
limites de três PDFs de 20 MB ficam para implementação futura; OCR continua fora
do P0.

## Recusa, fontes e resposta parcial

**Recusa** indica contexto insuficiente. **Fonte Citada** aparece somente quando
a resposta usa marcador válido. Chunk sem marcador aparece como **Chunk
Recuperado**. Falha após primeiro token preserva **Resposta Parcial**.
