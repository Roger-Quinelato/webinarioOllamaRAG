# Consolidado da RODADA-1 — bloqueadores, backlog e veredito para 21/09

**Data:** 2026-09-16 · **Eixos:** A1 (piloto) + A2 a A6 · **Achados:** 84 propostos, 81 confirmados,
1 rejeitado, 1 reclassificado, 3 duplicados, 2 lacunas abertas e respondidas.

Nenhum status de `docs/VERIFICACAO.md` foi alterado por esta auditoria. Este documento diz o que
precisa acontecer para que os status voltem a ser verdadeiros.

---

## 1. Bloqueadores da aula

Ordenados pelo risco para o ensaio de **21/09/2026**, não pela severidade nominal.

### B1 — `REINDEXAR = False` não impede a reindexação (A3-03)

- **O que quebra:** `ferramentas/construir_notebook.py:149` é `if REINDEXAR or colecao.count() != len(chunks):`.
  Basta a contagem de chunks divergir — corpus alterado, coleção de outra execução, índice incompleto —
  para o notebook reindexar **ao vivo**.
- **Quando:** bloco 2 (Indexação), 18 minutos previstos. A última medição de indexação é **1420 s**,
  23,7 minutos: sozinha, estoura o bloco inteiro e come a folga dos cinco minutos.
- **Plano B se não der tempo de corrigir:** antes de começar, rodar `verificar.py e2` e confirmar 659
  vetores. Se a contagem divergir, **não abrir o notebook**: usar as saídas salvas e explicar a
  indexação pelo `resultados/`.

### B2 — A demonstração do critério 6.5 funciona em 25% das perguntas (A4-15, A1-08, A4-06, A3-02, A2-10)

- **O que quebra:** com `qwen2.5:1.5b`, padrão desde o #19, o modelo cita `[n]` em **2 de 8** perguntas
  medidas (`seed=42`, k=4). Nas outras 6, o fallback lista o top-k inteiro e a tela afirma
  "Fontes (citadas 4 de 4)", marcando "✅ citado" em tudo.
- **Quando:** blocos 5 (com/sem contexto), 6 (Ollama) e 7 (Streamlit) — os três demonstram fontes. O
  notebook já tem a evidência do problema salva: em `E7/t03_fontes_notebook.txt:11-25` as duas listas
  saem idênticas.
- **Por que é o pior dos bloqueadores:** é **intermitente**. Não dá para ensaiar: a mesma pergunta pode
  citar no ensaio de 21/09 e não citar em 28/09.
- **Plano B se não der tempo de corrigir:** escolher perguntas que já se sabe que citam (a sonda
  `lacuna-a4-sonda.py` identifica duas) ou trocar para o `qwen2.5:3b` no bloco de fontes, assumindo os
  40–80 s de troca de modelo.

### B3 — `scripts/00` aprova um ambiente onde o bloco de SHAP quebra (A6-02)

- **O que quebra:** a lista `pacotes` de `scripts/00_checar_ambiente.py:37` não inclui `matplotlib`,
  exigido por `shap.plots.text` (`scripts/05_shap.py:36`). O script imprime "Ambiente pronto." e sai 0.
- **Quando:** bloco 4 (SHAP), 12 minutos. O traceback aparece **depois** de ~40 s de cálculo, com a
  turma olhando. Mesmo buraco para `ipykernel`, que quebra antes, ao abrir o notebook.
- **Plano B:** rodar `python -c "import matplotlib, ipykernel"` na véspera. Trivial de corrigir: dois
  nomes na lista.

### B4 — O troubleshooting manda dar uma informação falsa no chat (A5-09, A2-16)

- **O que quebra:** `docs/troubleshooting.md:50-52` instrui o facilitador a responder que "ainda não há
  artigos em português no corpus" e que o filtro `idioma = pt` "volta vazio de propósito". São dois
  artigos em português desde o T12, e o app recupera o `medeiros2025_embeddings_pt.pdf`.
- **Quando:** qualquer momento em que alguém do chat perguntar sobre o filtro de idioma — o público é
  intermediário/avançado e o filtro está visível na barra lateral.
- **Plano B:** nenhum. É uma linha de documentação; corrigir custa um minuto.

### B5 — O orçamento do bloco 7 foi calculado com números do modelo errado (A5-07)

- **O que quebra:** `docs/medicoes.md:53` publica "AppTest, 3b, 8 s · 17 s" citando `E8/apptest.txt`,
  cujo conteúdo atual é `qwen2.5:1.5b` com 44 s por pergunta. A linha 100 conclui "~4 perguntas no pior
  caso" para o bloco 7.
- **Quando:** bloco 7 (Streamlit), 15 minutos. Com 44 s por pergunta e não 17 s, o número real de
  perguntas que cabem é menor, e o bloco pode estourar sem aviso.
- **Plano B:** limitar a 3 perguntas no Streamlit e avisar a turma que o resto vai por conta deles.

### B6 — O ambiente pode quebrar de novo, sem detecção e sem receita (A1-00, A6-03)

- **O que quebra:** o `.venv` foi encontrado com os arquivos de ~31 distribuições apagados e os
  `dist-info` intactos. `pip list` dava tudo como instalado; nada importava. Nenhuma checagem do
  repositório procura esse estado, e `troubleshooting.md` não menciona `dist-info`,
  `requirements.lock` nem `force-reinstall`.
- **Quando:** antes da aula, ou durante — a causa raiz não foi determinada.
- **Plano B:** deixar o comando de reparo à mão:
  `pip install --force-reinstall --no-deps -r requirements.lock` (sem `pip`, `setuptools` e `wheel`,
  que travam o processo).

## 2. Backlog de tickets

Prontos para `gh issue create`. Label sugerida do vocabulário de `docs/agents/triage-labels.md`.

| # | Título | Critério | Label | Origem |
|---|---|---|---|---|
| T31 | Corrigir a condição de reindexação do notebook e o comentário de tempo | 7.6, 9.4 | `ready-for-agent` | A3-03 (B1) |
| T32 | Decidir o tratamento das fontes citadas com o modelo padrão | 6.5, 8.7, 9.3 | `needs-info` | A4-15 (B2) |
| T33 | `scripts/00` deve checar todos os pacotes de `requirements.txt` | 0.5, 0.6, 0.8 | `ready-for-agent` | A6-02 (B3) |
| T34 | Reescrever o critério 0.8 ou cobrir 0.2 e 0.5 no script | 0.8 | `ready-for-agent` | A6-01 |
| T35 | Corrigir `troubleshooting.md` sobre artigos em português | 10.3 | `ready-for-agent` | A5-09 (B4) |
| T36 | Reconciliar todos os números de `medicoes.md` com a evidência atual | 9.1, 9.4 | `ready-for-agent` | A5-01 a A5-08, A2-05 |
| T37 | Detectar `dist-info` sem arquivos e documentar o reparo | 0.5, 10.3 | `ready-for-agent` | A1-00, A6-03 (B6) |
| T38 | Fazer as 7 checagens mudas reprovarem | 1.6, 2.x, 3.x, 6.7, 7.3 | `ready-for-agent` | A2-03 |
| T39 | Regerar as evidências de E1, E2, E3 e E4 no corpus de 8 artigos | 1.x, 2.x, 3.x, 4.4 | `ready-for-agent` | A2-01, A2-02, A2-04, A2-15 |
| T40 | Refazer as capturas de E8 com o slider chegando ao backend | 8.2, 8.4, 8.5, 8.6, 8.7, 8.8 | `ready-for-agent` | A4-01, A4-02, A4-03, A4-10, A4-11, A4-12 |
| T41 | Versionar as capturas de E8 | 8.2–8.8 | `ready-for-agent` | A4-04, A2-08 |
| T42 | Fazer `testar_app.py` reprovar em todos os pontos que verifica | 8.1, 8.2, 8.3, 8.7 | `ready-for-agent` | A4-05 |
| T43 | Incluir os 2 artigos em português no notebook | 1.7, 7.3 | `ready-for-agent` | A3-01 |
| T44 | Dar saída pré-computada ao bloco 2.5 e rever o plano B do bloco 5 | 6.3, 7.6 | `ready-for-agent` | A3-04, A3-05, A3-08 |
| T45 | Atualizar README, CLAUDE.md e plano v1.1 (modelo, corpus, branch, tempos) | 10.1, 10.4 | `ready-for-agent` | A5-03, A5-11 a A5-16, A5-19 |
| T46 | Corrigir HEAD e contagem de commits em `ESTADO_ATUAL.md` | — | `ready-for-agent` | A5-17, A5-18 |
| T47 | Recalcular o Shapley e a avaliação RAGAS no corpus atual | 5b.1, 7.6 | `ready-for-agent` | A2-12, A3-09 |
| T48 | Exercitar `e4` e `e4_limiar` contra entrada que deveria reprovar | 4.4 | `ready-for-agent` | LACUNA A2 |

A issue **#24** (proteger `scripts/01` e `02` com `cli_seguro()`) já existe e continua válida; A3-11
acrescentou a ela o ângulo do roteiro sem plano B para Ollama fora do ar no bloco 2.

## 3. Critérios contestados

Nenhum status foi alterado. Cada linha diz o que reabilita o ✅.

| Critério | Por quê | O que reabilita |
|---|---|---|
| 0.8 | ✅ falso: o script não cobre 0.2 nem 0.5 (A6-01) | T34 + nova execução de `scripts/00` com as checagens que faltam |
| 0.5, 0.6 | O script aprova ambiente sem `matplotlib`/`ipykernel` (A6-02) | T33 |
| 1.1, 1.2, 1.6, 2.1–2.6, 3.1–3.6 | Evidência descreve o corpus de 6 artigos (A2-01, A2-15) | T39: rodar as checagens no corpus atual e salvar a saída |
| 3.6, 4.4 | A evidência demonstra o caso `idioma=pt`, que o código não roda mais (A2-04) | T39 + T48 |
| 5b.1 | Shapley pré-computado é de outro corpus e de outro modelo (A2-12, A3-09) | T47 |
| 6.5 | Demonstração funciona em 25% das perguntas (A4-15) | T32 (decisão do autor) |
| 6.6 | Testa a troca de modelo no sentido que deixou de existir (A2-11) | Reescrever o critério junto com a decisão de 9.3 |
| 6.7 | `scripts/01` e `02` fora da cobertura (A2-07, A3-11) | issue #24 |
| 7.2, 7.6 | Bloco 2.5 sem saída pré-computada; plano B do bloco 5 apaga o contraste (A3-04, A3-05, A3-08) | T44 |
| 8.2, 8.4, 8.5, 8.6, 8.7, 8.8 | Capturas inválidas e não versionadas (A4-01, A4-02, A4-04) | T40 + T41 |
| 8.1, 8.3 | `testar_app.py` não reprova nesses pontos (A4-05) | T42 |
| 9.1 | Números divergem da evidência citada (A5-01 a A5-08, A2-05) | T36 |
| 9.4 | O orçamento do bloco 7 usa números do 3b (A5-07) | T36 + remedição do bloco 7 |
| 10.3 | Troubleshooting afirma o que o corpus tornou falso (A5-09, A2-16) | T35 |
| 10.4 | Plano v1.1 diz 8 artigos e lista 6 (A5-16) | T45 |

## 4. Aceites conscientes

- **10.1 em macOS e Linux** — sem máquina para testar. Segue ⏸️, como já estava (issue #17).
- **9.3, decisão final do modelo** — depende do ensaio de 21/09. A auditoria entrega o número que
  faltava (25% de citação com o 1.5b); a escolha é do autor (T32, issue #19).
- **Causa raiz de A1-00** — não determinada e provavelmente não determinável agora. O que dá para fazer
  é detectar e documentar o reparo (T37).
- **`e4` e `e4_limiar` nunca vistas reprovando** — exigiria montar um corpus de teste. Vai para T48 com
  prioridade baixa: as duas cobrem um caminho que já tem três evidências independentes.
- **Achados de severidade baixa** (17 no total) — não bloqueiam nada. Ficam no backlog sem prioridade.

## 5. Placar da auditoria

| Eixo | Propostos | Confirmados | Reclassificados | Rejeitados | Duplicados | Lacunas |
|---|---:|---:|---:|---:|---:|---:|
| A1 (piloto) | 8 | 6 | 1 | 1 | 0 | 1 |
| A2 | 17 | 16 | 0 | 0 | 1 | 1 |
| A3 | 14 | 14 | 0 | 0 | 1 | 0 |
| A4 | 15 | 15 | 0 | 0 | 1 | 1 |
| A5 | 20 | 20 | 0 | 0 | 0 | 0 |
| A6 | 11 | 11 | 0 | 0 | 0 | 0 |
| **Total** | **85** | **82** | **1** | **1** | **3** | **3** |

**O que o placar diz.** O piloto (A1) foi o pior eixo: 1 rejeição e 1 reclassificação em 8 achados, as
duas por não ter repetido a medição e por não ter lido o comentário adjacente. As duas regras que o
ticket #28 acrescentou por causa disso apareceram aplicadas nos cinco eixos seguintes, que fecharam com
**zero rejeições e nenhuma referência de linha errada na amostra reproduzida**. A calibração pagou o
próprio custo em uma rodada.

Os três duplicados foram todos de fronteira entre eixos, não de qualidade — sinal de que a divisão por
arquivo funciona, mas precisa de uma regra explícita para achados que atravessam eixos (o mesmo fato
visto do lado do código, da evidência e da documentação).

O eixo A5 foi o mais produtivo (20 achados, 7 altos) e o A6 o mais decisivo por achado (11 achados, 1
crítico e 2 altos, num escopo de 6 arquivos). O A4 foi o único que precisou do Ollama e o único que
produziu evidência visual — e foi lendo as próprias imagens que o CTO derrubou a evidência do critério
8.4.

---

## Recomendação

**O material não está pronto para o ensaio de 21/09.** Nesta ordem, antes do ensaio: (1) corrigir a
condição de reindexação do notebook, que pode consumir 23 minutos ao vivo; (2) decidir o que fazer com
as fontes citadas, que hoje funcionam em 25% das perguntas; (3) acrescentar `matplotlib` e `ipykernel`
à checagem de ambiente; (4) corrigir a linha do troubleshooting sobre artigos em português. Os quatro
são de baixa complexidade e alto impacto. O resto do backlog pode correr depois do ensaio, com exceção
dos números de `medicoes.md`, que sustentam o cronograma inteiro.
