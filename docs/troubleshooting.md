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

`NVIDIA_TIMEOUT` e `GEMINI_TIMEOUT` são opcionais e usam segundos. O SDK
Gemini recebe internamente o valor convertido para milissegundos.

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
