# Estratégia test-first: OpenAI RAG

## Seams

- **Provider de embeddings**: contrato público de `bge-m3` contra cliente Ollama
  simulado na fronteira externa.
- **Provider de geração**: contrato público de geração/streaming contra cliente
  OpenAI simulado na fronteira externa.
- **Fachada RAG**: busca, grounding, fontes e retry observados por resposta e
  metadados; não teste funções privadas.
- **Streamlit**: AppTest observa estado, upload, fontes e erros.

## Ciclos red-green

1. Ollama ou `bge-m3` ausente: teste falha; implemente só mensagem acionável.
2. Chave OpenAI ausente: teste falha; implemente só mensagem acionável.
3. Provider, modelo, dimensão ou esquema incompatível: teste falha; implemente
   recusa de uso + reindexação explícita.
4. Fonte sem marcador: teste falha; classifique fallback, não citação.
5. Pergunta sem evidência: teste falha; devolva **Recusa**, sem conteúdo externo.
6. Erro antes/depois do primeiro token: teste falha; implemente retry único +
   **Resposta Parcial**.
7. Upload visível em outra sessão: teste falha; isole **Índice de Sessão** e
   limpe recursos.

## Casos obrigatórios

- Corpus Oficial e Índice de Sessão usam `bge-m3` via Ollama.
- Geração e streaming usam `gpt-5.6-luna` via OpenAI.
- Falha da geração OpenAI não aciona geração local automaticamente.
- **Corpus Oficial** e **Índice de Sessão** não se misturam numa consulta.
- Filtros/metadados de arquivo, página e ano chegam à fonte apresentada.
- Geração recebe duas turnos de histórico; retrieval não muda.
- AppTest cobre streaming, limpeza, credencial, recusa e fontes.
- Matriz de ensaio cobre recuperação, citação, recusa e filtro. O caso de
  upload só entra quando `UPLOADS_STREAMLIT_HABILITADOS=True`.

## Qualidade

Cada teste afirma comportamento observável, usa valores esperados independentes e
simula apenas as fronteiras Ollama e OpenAI. Nenhum depende de detalhe privado.
