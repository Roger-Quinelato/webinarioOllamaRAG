# Evidência MIG-05

**Issue:** #63
**Objetivo:** Adaptar Streamlit para estado, fontes e falhas OpenAI.

## Subtasks concluídas
- [x] Guardar histórico de duas turnos para geração e pergunta atual para retrieval. (Implementado em `app.py` fatiando `st.session_state.mensagens[-5:-1]`)
- [x] Exibir Base Ativa, fontes citadas, fallback recuperado, recusa e resposta parcial. (Implementado via lógica em `mostrar_fontes`)
- [x] Criar controles para upload, ano opcional e limpeza de sessão. (Implementado via `st.sidebar`)
- [x] Tratar chave ausente, erro de provider e upload inválido sem traceback. (Tratamentos baseados nas exceções de `openai_provider.py`)

## Validação
- Executado o `test_app.py` garantindo que:
  - O aplicativo não quebra e exibe aviso `st.warning` quando não há chave OpenAI.
  - O aplicativo sobe corretamente quando a chave e o índice existem.

**Comando:**
```bash
.\.venv\Scripts\python.exe -m unittest discover tests/
```
**Resultado:** `OK` para todos os testes (43 executados).
