# PRD: Migração OpenAI RAG para webinário

## Objetivo

Entregar chatbot Streamlit didático que responde ao corpus selecionado com
OpenAI, mostra fontes verificáveis e recusa perguntas sem suporte recuperado.
Deve funcionar no ensaio de 21/09 sem Ollama instalado.

## Usuário e fluxo

Facilitador seleciona base oficial ou envia até três PDFs; pergunta; acompanha
streaming; abre fontes com arquivo, página, ano e trecho recuperado. UI distingue
**Recusa**, **Resposta Parcial** e interrupção. Não chama recuperação de citação.

## Escopo P0

- Corpus oficial: `text-embedding-3-small`, Chroma persistente.
- Geração: `gpt-5.6-luna`, streaming, uma repetição antes do primeiro token.
- Grounding estrito, citações rastreáveis, recusa sem contexto suficiente.
- Até três PDFs de 20 MB; ano opcional; índice exclusivo da sessão.
- Geração usa duas últimas turnos; retrieval usa apenas pergunta atual.
- Ensaio: cinco perguntas para recuperação, citação, recusa, filtro e upload.

## Fora do escopo P0

LangChain, FAISS, SentenceTransformers, Ollama, OCR/Tesseract, bounding boxes,
consulta simultânea entre bases, upload persistente, SHAP/RAGAS e revisão visual
de UX.

## Critérios de aceite

- Sem `OPENAI_API_KEY`: explique configuração; não inicie consulta.
- Resposta grounded: mostre só fontes realmente referenciadas. Chunk recuperado
  sem citação deve receber rótulo de Chunk Recuperado.
- Sem evidência: produza recusa definida, sem conhecimento externo.
- Upload não aparece em outra sessão nem altera coleção oficial.
- Falha antes do primeiro token: uma repetição. Falha posterior: preserve e marque
  resposta parcial.
- Matriz de cinco perguntas passa ensaio e possui evidência versionada.

## Métricas

- Recusas corretas na pergunta fora da base.
- Respostas grounded com ao menos uma citação válida.
- Tempo de indexação e tempo até primeiro token, registrados por ensaio.
- Falhas API, tentativas e respostas parciais.
