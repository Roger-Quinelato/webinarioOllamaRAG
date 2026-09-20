# MIG-05 — fallback remoto de geração

**Data:** 2026-09-20

## Validação automatizada

Comando executado no ambiente `.venv`:

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_*.py' -v
```

Resultado: **72 testes, sucesso**.

Cobertura adicionada:

- HTTP 429 OpenAI antes do primeiro token chama NVIDIA.
- `retry-after` curto repete provider; valor longo avança à NVIDIA.
- Falha NVIDIA antes de token chama Gemini.
- Falha após token não troca provider e preserva **Resposta Parcial**.
- Todos os providers indisponíveis retornam erro seguro.
- Retrieval e embeddings executam uma vez quando roteador falha.
- Streamlit inicia com provider disponível, inclusive sem OpenAI.

## Validação real pendente

Não há evidência real neste commit: não foram usadas nem registradas credenciais
OpenAI, NVIDIA ou Gemini. Antes do gate CTO, executar a matriz de cinco
perguntas com cada provider isolado e os cenários OpenAI 429, NVIDIA fallback e
Gemini fallback. Registrar provider, modelo, tentativa, tempo até primeiro
token, Base Ativa e fontes, sem chave ou prompt integral.
