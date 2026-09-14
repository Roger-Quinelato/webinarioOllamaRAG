# Revisão de código em dois eixos — 2026-09-14

- **Pergunta do autor:** o plano de implementação foi feito corretamente?
- **Ponto fixo:** árvore vazia `4b825dc` → `HEAD` `26689e8`. O diff tem 93 arquivos, porque o projeto inteiro nasceu nos commits `7e29c38` e `26689e8`.
- **Spec:** `docs/VERIFICACAO.md` (E0–E10), as decisões de arquitetura do `CLAUDE.md` e o plano de aula v1.0 (`~/Downloads`) comparado com a v1.1 (`docs/`).
- **Padrões:** `CLAUDE.md`, `docs/VERIFICACAO.md`, `.tlc/harness/` e a baseline de smells de Fowler. Não há `CODING_STANDARDS.md` nem `CONTRIBUTING.md`.
- **Método:** dois sub-agentes em paralelo, só leitura. A sessão principal conferiu no código os achados marcados como "conferido".
- **Checagens estáticas:** `revisao_codigo_checagens.txt`.
  - `e7_duplicadas` e `e7_estrutura` saem com código 0.
  - `py_compile` dos 19 `.py` sai com código 0.
  - `git ls-files` não lista nenhum PDF, `chroma_db/`, `.venv/` ou `Ollama/models/`.
- **Status:** nenhum critério mudou nesta revisão. Os critérios contestados estão listados no fim, para reverificação.

## Standards

Não há violação dura confirmada; três falhas de padrão documentado são prováveis.

Conferido e conforme:
- `requirements*.txt` só usam `==`, e o lock é coerente.
- Não há LangChain nem LlamaIndex.
- O `.gitignore` segue o `CLAUDE.md`.
- Nomes de modelo só aparecem em `config.py`.
- As mensagens `system` e `user` estão separadas.
- As chaves `REINDEXAR`, `LLM_AO_VIVO` e `SHAP_AO_VIVO` estão na 1ª célula.

### (a) Padrões documentados

1. **Lógica do pipeline fora do `rag.py`** (CLAUDE.md, seção "Arquitetura"; critério 7.4). Provável violação; **conferido**.
   - `scripts/06_com_sem_contexto.py:35` copia a regra de omitir fontes de `rag.py:317-318`.
   - `ferramentas/construir_notebook.py:320` diverge: mostra as fontes sempre, mesmo quando a resposta é "Não encontrei…".
   - `ferramentas/medir.py:67` chama o Ollama direto, com o privado `rag._opcoes()` e sem tratar erro de conexão. É julgamento, porque a regra não cita `ferramentas/`.
2. **Checagem do 7.4 fraca** (`ferramentas/verificar.py`, função `e7_duplicadas`). **Conferido**.
   - Só compara nomes de funções.
   - Não varre `ferramentas/`.
   - Ignora `opcional/` na lista de chamadas.
   - Só imprime, sem falhar. Mesmo assim, o ✅ do 7.4 se apoia nela.
3. **Ollama desligado (6.7).** **Conferido**.
   - Só `app.py` e `scripts/07_ollama.py` capturam `OllamaIndisponivel`.
   - `scripts/03`–`06` e `opcional/*.py` não capturam nada e mostram traceback.
   - A checagem `e6_ollama_desligado` testa só `rag.py`.
4. **k fixo fora do `config.py`.**
   - `opcional/calcular_shapley_chunks.py:16` usa `default=4`.
   - Também há k fixo em `scripts/04_dois_estagios.py`, `ferramentas/medir.py` e `construir_notebook.py`.
   - Nos scripts 03 e 05, variar o k é didático, e está ok.
5. **Comentários `why:`/`hazard:`/`invariant:`.** É julgamento, porque a regra é do harness e vale para comentários novos.
   - `construir_notebook.py:52-54` narra o que o código faz.
   - O "alguns minutos" dessas linhas contradiz os ~19 min de reindexação.

### (b) Smells da baseline (sempre julgamento)

- **Repeated Switches e Data Clumps** (**conferido**): a escolha entre busca simples e dois estágios monta o dicionário `{caminho, artigos, resultados}` e se repete em `app.py:77-81` e `scripts/07_ollama.py:18-23`. Caberia uma função no `rag.py`.
- **Duplicated Code:**
  - `try/except _ERROS_CONEXAO` aparece 4× em `rag.py` (166, 296, 311, 337).
  - `tabela()` no gerador do notebook repete `rag.tabela_resultados`; a didática justifica.
- **Shotgun Surgery:** a lista de artigos está em `config.ARTIGOS_ARXIV` e de novo em `construir_notebook.py:101-108`.
- **Estado global oculto:** `opcional/avaliacao_estilo_ragas.py` lê `args.modelo` dentro das funções.
- **Números mágicos** (leve):
  - `rag.py`: `lote = 64`, `seed = 42` e `max_tokens=200`.
  - `app.py:46`: anos de 2020 a 2026.

## Spec

A maior parte dos ✅ tem evidência que confere.

Conferido e OK:
- 556 chunks, sobreposição de 139–146 caracteres e 6 resumos.
- k = 1, 4 e 8, filtros e busca cross-lingual.
- Estágio 2 restrito aos artigos do estágio 1.
- SHAP: diferença de aditividade de 0,002–0,007; soma dos Shapley correta.
- Saídas pré-computadas regeneradas depois da troca para system+user.
- Ordem do notebook igual à do cronograma.
- Plano v1.1: 1h54, sem Colab, datas 21/09 e 28/09, anexos preenchidos.

### (a) Ausente ou parcial

1. **4.4** (critério: "Se o estágio 1 não achar nada, a função cai para a busca simples ou avisa, sem quebrar", verificado com "pergunta fora da base"). **Conferido**.
   - Com a pergunta fora da base, o caminho seguiu "dois estágios", com distâncias de ~0,73, sem fallback e sem aviso (`E4/04_dois_estagios.txt:74-82`).
   - A verificação trocou esse caso por um filtro `idioma=pt`.
2. **8.2, 8.4, 8.5 e 8.7** (critério: "captura" de tela). Nenhuma captura foi salva; a evidência é texto do DOM mais AppTest (`E8/ui_navegador.txt`). No 8.5, filtro, k e modo mudaram juntos (`E8/apptest.txt:12-13`).
3. **Evidências com números defasados (5a.1, 7.2, 9.1).** **Conferido** em `medicoes.md`.
   - `E5/notebook_E5.txt:12` e `docs/medicoes.md:33` registram SHAP em 34–37 s.
   - O notebook versionado e `medicoes.md:97` registram 94 s.
   - O teste offline (03:37) é anterior à regeneração de `com_sem_contexto.json` e `resposta_bloco6.md`.
4. **1.6** (critério: "conferência manual de cada linha, registrada"). **Conferido**: a seção 1.6 de `E1/verificacao_E1.txt:13-14` está vazia. Os resumos aparecem depois, sob o título da 1.7, sem registro de conferência manual.
5. **Prompt system+user.** O `CLAUDE.md` diz "testado", mas não há arquivo com a falha do prompt único. **Conferido**: `E10/troubleshooting_cobertura.txt:15` admite que não há arquivo salvo.
6. **v1.0 → v1.1.** **Conferido**:
   - A v1.1 não menciona os "slides conceituais" da v1.0.
   - `docs/roteiro_facilitador.md:109` ainda diz "Explique as métricas pelo slide".

### (b) Escopo não pedido

- **Seletor de modelo e botão "Limpar conversa"** (`app.py:42`, `app.py:49`). O roteiro desaconselha trocar de modelo ao vivo.
- **Arquivos de ferramenta versionados:** `.tlc/harness/*` e `.claude/launch.json`.

### (c) Implementado, mas com implementação que parece errada

1. **Fallback morto em `rag.py:234-238`.** **Conferido**.
   - Quando o estágio 1 fica vazio, `buscar()` recebe o mesmo `where`.
   - Os chunks de página herdam os metadados do CSV, então o resultado também sai vazio. A própria evidência mostra "(nenhum resultado)".
   - Pergunta fora da base nunca esvazia o estágio 1, porque a busca vetorial sempre devolve os vizinhos mais próximos.
2. **6.4.** A resposta salva é "Não encontrei essa informação nos documentos. [1]" (`resultados/com_sem_contexto.json:37`), e não a frase exata. **Conferido**. O `responder()` ainda suprime as fontes, porque testa por substring.
3. **6.5** (critério: "cita as fontes (arquivo, página) usadas"). `responder()` lista os k trechos recuperados, não os citados (`rag.py:317-318`). **Conferido**.
4. **Bloco 5** (plausível). Na pergunta ao vivo sobre Self-RAG, sem contexto o modelo recusa em vez de inventar. O caso de invenção do 6.3 só aparece na tabela salva.
5. **6.7.** `E6/ollama_desligado.txt:2,16` registra `exit=0` depois de `ERRO`/`FALHOU`. **Conferido**. O código sai com 2 em `scripts/07_ollama.py:34`, então o código de saída capturado não é confiável. A mensagem clara, sem traceback, que é o critério, está presente.

## Critérios contestados (reverificar; status não alterado nesta revisão)

| Critério | Motivo |
|---|---|
| 1.6 | seção de conferência manual vazia |
| 4.4 | fallback nunca dispara com a pergunta fora da base; com filtro, devolve vazio |
| 6.5 | fontes listadas = recuperadas, não usadas |
| 6.7 | cobre `rag.py` e `app.py`; scripts 03–06 e `opcional/` sem tratamento; `exit=0` duvidoso |
| 7.4 | checagem só por nome de função, não falha e não varre `ferramentas/` |
| 8.2, 8.4, 8.5, 8.7 | sem captura de tela |
| 5a.1, 7.2, 9.1 | números da evidência defasados em relação ao notebook versionado |
