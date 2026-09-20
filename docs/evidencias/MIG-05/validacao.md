# Evidência MIG-05

**Issue:** #63

## Comandos executados

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_app -v
.\.venv\Scripts\python.exe -m unittest discover tests -v
```

## Resultado

- AppTests: 3 passaram. Cobrem chave OpenAI ausente, inicialização e seleção de Índice de Sessão sem upload.
- Suíte completa: 50 testes passaram.
- `Corpus Oficial` inicia como Base Ativa. `Índice de Sessão` só é usado após seleção explícita.
- Upload válido não seleciona a base silenciosamente. Limpeza remove histórico, sessão e coleção efêmera; troca a chave do widget de upload.
- `Fontes Citadas` lista somente chunks citados. Chunks sem citação aparecem em `Chunks Recuperados`; Recusa não promove chunks.
- Falhas conhecidas de OpenAI, Ollama, Chroma e incompatibilidade do Corpus Oficial mostram orientação segura, sem traceback ou segredo.
- Streaming preserva `Resposta Parcial`, produzida pela fachada antes da interface exibir o resultado.
