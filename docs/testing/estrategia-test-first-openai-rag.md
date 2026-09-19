# Estratégia test-first: OpenAI RAG

## Seams

- **Provider**: contrato público de embeddings/streaming contra cliente OpenAI
  simulado na fronteira externa.
- **Fachada RAG**: busca, grounding, fontes e retry observados por resposta e
  metadados; não teste funções privadas.
- **Streamlit**: AppTest observa estado, upload, fontes e erros.

## Ciclos red-green

1. Chave ausente: teste falha; implemente só mensagem acionável.
2. Modelo incompatível: teste falha; implemente recusa de uso + reindexação
   explícita.
3. Fonte sem marcador: teste falha; classifique fallback, não citação.
4. Pergunta sem evidência: teste falha; devolva **Recusa**, sem conteúdo externo.
5. Erro antes/depois do primeiro token: teste falha; implemente retry único +
   **Resposta Parcial**.
6. Upload visível em outra sessão: teste falha; isole **Índice de Sessão** e
   limpe recursos.

## Casos obrigatórios

- Embeddings e geração usam modelos configurados, sem Ollama.
- **Corpus Oficial** e **Índice de Sessão** não se misturam numa consulta.
- Filtros/metadados de arquivo, página e ano chegam à fonte apresentada.
- Geração recebe duas turnos de histórico; retrieval não muda.
- AppTest cobre streaming, limpeza, credencial, recusa e fontes.
- Matriz de ensaio cobre recuperação, citação, recusa, filtro e upload.

## Qualidade

Cada teste afirma comportamento observável, usa valores esperados independentes e
simula apenas fronteira OpenAI. Nenhum depende de detalhe privado.
