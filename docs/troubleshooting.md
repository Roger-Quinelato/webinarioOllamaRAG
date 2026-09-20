# Troubleshooting

## Ollama não responde

Ollama fornece somente embeddings. Inicie o serviço e confirme `bge-m3`:

```powershell
ollama pull bge-m3
python scripts/00_checar_ambiente.py
```

Não tente resolver falha de embedding instalando modelo de chat local.

## Chave OpenAI ausente

Defina `OPENAI_API_KEY` no ambiente ou em `st.secrets`. A aplicação mostra
orientação segura e não inicia consulta sem chave. Nunca registre o valor.

## OpenAI retorna 401, 429 ou falha de rede

Confira credencial, quota e conectividade. O provider expõe mensagem acionável;
não há fallback automático para geração local. HTTP 429 mantém ensaio bloqueado
até chamada real concluir.

## Corpus Oficial incompatível

Coleção precisa declarar `Ollama`, `bge-m3`, dimensão `1024`, esquema
`bge-m3-v1` e status `ready`. Rode `python scripts/02_indexar_hibrido.py` para
reindexar explicitamente.

## Upload vazio ou inválido

Índice de Sessão aceita até três PDFs de 20 MB. PDF sem texto extraível produz
aviso; OCR fica fora do P0. Upload válido não altera Corpus Oficial.

## Recusa, fontes e resposta parcial

**Recusa** indica contexto insuficiente. **Fonte Citada** aparece somente quando
a resposta usa marcador válido. Chunk sem marcador aparece como **Chunk
Recuperado**. Falha após primeiro token preserva **Resposta Parcial**.
