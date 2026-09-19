# Contexto RAG didático

Linguagem do chatbot. Separa corpus controlado, participante, chunks recuperados
e afirmações atribuídas pela resposta.

## Bases

**Corpus Oficial**: conjunto fixo de oito artigos da demonstração.  Evitar: base
padrão, base global.

**Índice de Sessão**: base temporária, exclusiva dos PDFs enviados na sessão
Streamlit.  Evitar: corpus de upload, base do usuário.

**Base Ativa**: única base consultável por pergunta: Corpus Oficial ou Índice de
Sessão.  Evitar: base combinada.

## Recuperação e resposta

**Chunk Recuperado**: trecho com metadados retornado pela busca vetorial antes da
geração.  Evitar: fonte citada, evidência confirmada.

**Fonte Citada**: Chunk Recuperado referenciado pela resposta com identificador de
citação válido.  Evitar: fonte, resultado.

**Recusa**: resposta padronizada que informa contexto insuficiente na Base Ativa.
  Evitar: fallback, resposta vazia.

**Resposta Parcial**: texto emitido antes de falha da geração após primeiro token.
  Evitar: resposta completa.

## Integração

**Provider**: limite externo que fornece embeddings e geração de texto ao sistema
RAG.  Evitar: modelo, cliente global.
