# Estratégia test-first: OpenAI RAG

## Seams acordados

- **Provider**: contrato público de embeddings e streaming contra um cliente OpenAI
  simulado na fronteira externa.
- **Fachada RAG**: busca, grounding, fontes e retry observados pela resposta e seus
  metadados, sem testar funções privadas.
- **Aplicação Streamlit**: interação observada por AppTest para estado, upload,
  fontes e erros.

## Ciclos red-green

1. Escrever um teste que falha para chave ausente; implementar apenas a mensagem
   acionável.
2. Escrever um teste que falha para coleção com modelo incompatível; implementar a
   recusa de uso e a reindexação explícita.
3. Escrever um teste que falha para fonte recuperada sem marcador; classificá-la
   como fallback, não como citação.
4. Escrever um teste que falha para pergunta sem evidência; devolver a Recusa sem
   gerar conteúdo externo.
5. Escrever um teste que falha para erro antes e depois do primeiro token;
   implementar retry único e Resposta Parcial.
6. Escrever um teste que falha para upload visível em outra sessão; isolar o Índice
   de Sessão e limpar seus recursos.

## Casos obrigatórios

- Embeddings e geração usam os modelos configurados, sem Ollama.
- Corpus Oficial e Índice de Sessão não se misturam numa consulta.
- Filtros e metadados de arquivo, página e ano chegam à fonte apresentada.
- Histórico contém duas turnos na geração, mas não altera o retrieval.
- AppTest cobre streaming, limpeza, erro de credencial, recusa e fontes.
- A matriz de ensaio cobre recuperação, citação, recusa, filtro e upload.

## Critério de qualidade

Cada teste afirma um comportamento observável, usa valores esperados independentes
e simula apenas a fronteira OpenAI. Nenhum teste depende de detalhes privados da
implementação.
