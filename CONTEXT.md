# Contexto RAG didático

Este contexto descreve a linguagem do chatbot do webinário. Ele separa o corpus
controlado do participante, os trechos recuperados e as afirmações efetivamente
atribuídas pela resposta.

## Bases

**Corpus Oficial**:
O conjunto fixo de oito artigos selecionados para a demonstração.
_Evitar_: base padrão, base global.

**Índice de Sessão**:
Base temporária criada exclusivamente a partir dos PDFs enviados durante uma
sessão Streamlit.
_Evitar_: corpus de upload, base do usuário.

**Base Ativa**:
A única base consultável por uma pergunta: Corpus Oficial ou Índice de Sessão.
_Evitar_: base combinada.

## Recuperação e resposta

**Chunk Recuperado**:
Trecho com metadados retornado pela busca vetorial antes da geração.
_Evitar_: fonte citada, evidência confirmada.

**Fonte Citada**:
Chunk Recuperado que a resposta referencia explicitamente pelo identificador de
citação válido.
_Evitar_: fonte, resultado.

**Recusa**:
Resposta padronizada que informa não haver contexto suficiente na Base Ativa.
_Evitar_: fallback, resposta vazia.

**Resposta Parcial**:
Texto já emitido quando a geração falha depois do primeiro token.
_Evitar_: resposta completa.

## Integração

**Provider**:
Limite externo que fornece embeddings e geração de texto ao sistema RAG.
_Evitar_: modelo, cliente global.
