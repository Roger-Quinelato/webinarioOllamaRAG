# Estratégia test-first: OpenAI RAG

## Seams

- **Provider de embeddings**: contrato público de `bge-m3` contra cliente Ollama
  simulado na fronteira externa.
- **Providers de geração**: contratos públicos de geração/streaming contra os
  clientes OpenAI, NVIDIA e Gemini, simulados apenas nas respectivas fronteiras
  externas.
- **Fachada RAG**: busca, grounding, fontes e retry observados por resposta e
  metadados; não teste funções privadas.
- **Streamlit**: AppTest observa estado, upload, fontes e erros.

## Ciclos red-green

1. Ollama ou `bge-m3` ausente: teste falha; implemente só mensagem acionável.
2. Chave de provider remoto ausente: teste falha; implemente só mensagem
   acionável para OpenAI, NVIDIA ou Gemini.
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
- Geração e streaming usam OpenAI, NVIDIA e Gemini, nessa ordem definida pela
  ADR-003; cada provider tem teste de contrato na sua fronteira externa.
- Falha antes do primeiro token avança pela ordem OpenAI, NVIDIA e Gemini; não
  aciona geração local automaticamente.
- **Corpus Oficial** e **Índice de Sessão** não se misturam numa consulta.
- Filtros/metadados de arquivo, página e ano chegam à fonte apresentada.
- Geração recebe duas turnos de histórico; retrieval não muda.
- AppTest cobre streaming, limpeza, credencial, recusa e fontes.
- Matriz de ensaio cobre recuperação, citação, recusa e filtro. O caso de
  upload só entra quando `UPLOADS_STREAMLIT_HABILITADOS=True`.

## Qualidade

Cada teste afirma comportamento observável, usa valores esperados independentes e
simula apenas as fronteiras Ollama, OpenAI, NVIDIA e Gemini. Nenhum depende de
detalhe privado.
