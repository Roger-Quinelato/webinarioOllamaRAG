# Roteiro do facilitador — Encontro 2

**Condução:** Roger Quinelato · **Suporte:** João Victor Rikio Enomoto · **Duração:** ~1h54.

Consulte [troubleshooting.md](troubleshooting.md) antes da live.

## Antes da live

1. Inicie Ollama e instale somente `bge-m3`.
2. Configure pelo menos uma chave: `OPENAI_API_KEY`, `NVIDIA_API_KEY` ou
   `GEMINI_API_KEY`. Nunca mostre valores.
3. Rode `python scripts/00_checar_ambiente.py`.
4. Publique o Corpus Oficial antes da live com
   `python scripts/02_indexar_hibrido.py`.
5. Inicie `streamlit run app.py`. Durante o treino, upload permanece desativado.

Se Ollama falhar, interrompa retrieval. Se um provider remoto falhar antes do
primeiro token, o router tenta o próximo. Depois do primeiro token, preserve
**Resposta Parcial**. HTTP 429 bloqueia o ensaio real até validação.

## Bloco 1 — Arquitetura híbrida

- **Fala:** Ollama fornece embeddings `bge-m3`; Chroma recupera evidências;
  providers remotos geram texto.
- **Demo:** diagrama do notebook e fronteiras dos providers.
- **Checkpoint:** cada pergunta usa uma única **Base Ativa**.

## Bloco 2 — Corpus Oficial e indexação

- Mostre metadados, chunks e a coleção publicada.
- Explique provider, modelo, dimensão `1024`, esquema `bge-m3-v1` e status
  `ready`.
- Não reindexe ao vivo.

## Bloco 3 — Retrieval

- Use os filtros do Streamlit para demonstrar retrieval no Corpus Oficial.
- Explique distância, `k` e filtros.
- Use **Chunk Recuperado** para evidência retornada pela busca. Não chame isso de
  **Fonte Citada**.

## Bloco 4 — Geração e fallback

- Use uma pergunta no Streamlit para demonstrar streaming.
- Mostre ordem OpenAI, NVIDIA e Gemini.
- Explique: troca só ocorre antes do primeiro token; depois, resultado vira
  **Resposta Parcial** se stream falhar.

## Bloco 5 — Fontes e Recusa

- Resposta com marcador válido mostra **Fontes Citadas**.
- Marcador ausente mantém **Chunks Recuperados**.
- Pergunta fora do Corpus Oficial produz **Recusa**, sem fonte.

## Bloco 6 — Streamlit

- Faça duas perguntas e mostre histórico limitado a dois turnos anteriores.
- Mostre filtros, **Limpar conversa**, provider concluinte e classe de fontes.
- `UPLOADS_STREAMLIT_HABILITADOS=False` sinaliza upload para implementação
  futura. Índice de Sessão não é removido do código.

## Encerramento

- Não há fallback automático para geração local.
- Rollback de geração local exige troca explícita para `legacy-pre-openai`.
- Não marque ensaio como aprovado sem chamada real concluída e evidência
  versionada.
