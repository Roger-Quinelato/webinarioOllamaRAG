# PRD: Migração OpenAI RAG para o webinário

## Objetivo

Entregar um chatbot Streamlit didático que responde ao corpus selecionado usando
OpenAI, mostra fontes verificáveis e recusa perguntas sem suporte recuperado.
O produto precisa ser demonstrável no ensaio de 21/09 sem Ollama instalado.

## Usuário e experiência principal

O facilitador seleciona a base oficial ou envia até três PDFs. Faz uma pergunta,
acompanha a resposta em streaming e abre as fontes para ver arquivo, página, ano
e trecho recuperado. A interface explica se a resposta foi recusada, parcial ou
interrompida, sem fingir que uma fonte foi citada quando ela só foi recuperada.

## Escopo P0

- Corpus oficial indexado com `text-embedding-3-small` no Chroma persistente.
- Respostas com `gpt-5.6-luna`, streaming e uma única repetição antes do primeiro
  token.
- Grounding estrito, citações rastreáveis e recusa sem contexto suficiente.
- Upload de até três PDFs de 20 MB, ano opcional e índice exclusivo da sessão.
- Histórico de duas turnos na geração; retrieval usa apenas a pergunta atual.
- Cinco perguntas de ensaio cobrindo recuperação, citação, recusa, filtro e upload.

## Fora do escopo P0

- LangChain, FAISS, SentenceTransformers, Ollama, OCR/Tesseract e bounding boxes.
- Pesquisa simultânea nas bases oficial e de upload.
- Upload persistente, avaliação SHAP/RAGAS e revisão visual de UX.

## Critérios de aceite

- Sem `OPENAI_API_KEY`, a aplicação explica como configurar a chave e não inicia a
  consulta.
- Cada resposta grounded apresenta apenas fontes realmente referenciadas; fontes
  recuperadas sem citação recebem esse rótulo.
- Perguntas sem evidência recebem a recusa definida, sem conhecimento externo.
- O upload não aparece em outra sessão e não altera a coleção oficial.
- Falha antes do primeiro token repete uma vez; falha posterior preserva e marca a
  resposta parcial.
- A matriz das cinco perguntas passa no ensaio e possui evidência versionada.

## Métricas observáveis

- Taxa de respostas recusadas corretamente na pergunta fora da base.
- Taxa de respostas com ao menos uma citação válida nas perguntas grounded.
- Tempo de indexação do corpus e tempo até o primeiro token, registrados por ensaio.
- Contagem de falhas da API, tentativas e respostas parciais.
