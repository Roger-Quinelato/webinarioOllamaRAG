# PRD: Migração OpenAI RAG para webinário

## Objetivo

Entregar chatbot Streamlit didático que recupera contexto com `bge-m3` local,
gera respostas com providers remotos, mostra fontes verificáveis e recusa perguntas sem
suporte recuperado. Deve funcionar no ensaio de 21/09 com Ollama e ao menos um
provider remoto de geração configurados.

## Usuário e fluxo

Facilitador seleciona base oficial ou envia até três PDFs; pergunta; acompanha
streaming; abre fontes com arquivo, página, ano e trecho recuperado. UI distingue
**Recusa**, **Resposta Parcial** e interrupção. Não chama recuperação de citação.

## Escopo P0

- Corpus oficial e índice de sessão: `bge-m3` via Ollama, em espaços vetoriais
  compatíveis e coleções Chroma separadas.
- Geração: OpenAI, NVIDIA e Gemini com streaming. Ordem padrão OpenAI, NVIDIA,
  Gemini; troca somente antes do primeiro token.
- Grounding estrito, citações rastreáveis, recusa sem contexto suficiente.
- Até três PDFs de 20 MB; ano opcional; índice exclusivo da sessão.
- Geração usa duas últimas turnos; retrieval usa apenas pergunta atual.
- Ensaio: cinco perguntas para recuperação, citação, recusa, filtro e upload.

## Fora do escopo P0

LangChain, FAISS, SentenceTransformers, geração local no caminho principal,
fallback automático para geração local, OCR/Tesseract, bounding boxes, consulta
simultânea entre bases, upload persistente, SHAP/RAGAS e revisão visual de UX.

## Critérios de aceite

- Sem credencial de provider remoto: explique como configurar OpenAI, NVIDIA ou
  Gemini; não inicie consulta.
- Sem Ollama ou `bge-m3`: explique configuração; não indexe nem consulte.
- Coleção com provedor, modelo, dimensão ou esquema incompatível: recuse o uso e
  oriente reindexação explícita.
- Resposta grounded: mostre só fontes realmente referenciadas. Chunk recuperado
  sem citação deve receber rótulo de Chunk Recuperado.
- Sem evidência: produza recusa definida, sem conhecimento externo.
- Upload não aparece em outra sessão nem altera coleção oficial.
- Falha antes do primeiro token: roteie para o próximo provider; `retry-after`
  curto permite uma repetição. Falha posterior: preserve e marque resposta parcial.
- Matriz de cinco perguntas passa ensaio e possui evidência versionada.
- MIG-04 permanece bloqueada até o gate aprovar a reindexação híbrida e a
  fachada RAG adaptada.

## Métricas

- Recusas corretas na pergunta fora da base.
- Respostas grounded com ao menos uma citação válida.
- Tempo de indexação e tempo até primeiro token, registrados por ensaio.
- Falhas API, tentativas e respostas parciais.
