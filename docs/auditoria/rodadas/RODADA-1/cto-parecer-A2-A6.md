# Parecer do CTO — RODADA-1, eixos A2 a A6

**Data:** 2026-09-16 · **Escopo:** os achados de `A2-achados.md`, `A3-achados.md`, `A4-achados.md`,
`A5-achados.md` e `A6-achados.md`. O parecer do piloto (eixo A1) está em [`cto-parecer.md`](cto-parecer.md).

**Método e sua honestidade.** Os 64 achados de A2–A5 não foram todos reproduzidos um a um. Reproduzi
**de forma independente, com comando próprio, todos os de severidade alta** e uma amostra dos médios e
baixos, escolhida para cobrir os quatro eixos e todo tipo de afirmação (referência de linha, número,
comportamento de código, conteúdo de evidência, imagem). Os demais foram validados por leitura direta
do `arquivo:linha` citado. Onde a validação foi por leitura e não por reprodução, o bloco diz isso.
Nenhuma referência de linha errada foi encontrada na amostra — a qualidade dos quatro relatórios é
substancialmente melhor que a do piloto.

---

## A2 — Verificação e evidências (16 achados)

| # | Veredito | Validação independente |
|---|---|---|
| A2-01 | confirmado | `E2/reverificacao_e2.txt` abre com "2.2 total de chunks: 556"; o índice atual tem 659. A evidência que sustenta 2.2–2.6 descreve outro corpus. |
| A2-02 | confirmado | `git show --stat af18c3a` (commit do T12) toca evidências de E1, E7 e E10 — **nenhuma** de E2, E3 ou E4, apesar de a linha do Registro declarar `e2/e3/e4/e4_limiar` reverificados. |
| A2-03 | confirmado | Varredura AST por função: `e1_resumos`, `e2`, `e2_sobreposicao`, `e2_reabrir`, `e3`, `e6_ollama_desligado` e `e7_estrutura` não têm nenhuma chamada a `sys.exit` — 7 de 15, exatamente o que o achado afirma. |
| A2-04 | confirmado | `E4/reverificacao_e4_v2.txt:3` demonstra "4.4a estágio 1 vazio (**idioma=pt**)"; `verificar.py:133` hoje usa `ano>=2030` porque `idioma=pt` deixou de esvaziar com o T12. A evidência do critério 4.4 documenta um caso que o código não roda mais. |
| A2-05 | **duplicado (parcial)** | Os números em si pertencem ao eixo A5 (`medicoes.md`), que os detalha em A5-01 a A5-07 com mais precisão. Mantenho a parte que é de A2 — o ✅ do critério 9.1 apoiado nesses números — e descarto a enumeração repetida. Ver [`devolucoes/A2-05.md`](devolucoes/A2-05.md). |
| A2-06 | confirmado | `E7/saidas_notebook.txt` contém quatro valores de SHAP (36, 37, 48 e 50 s). Como o arquivo é append-only, qualquer um dos quatro "confirma" um número de `medicoes.md`. A checagem existe, passa, e não separa o valor atual do histórico. |
| A2-07 | confirmado | `verificar.py:253` usa `glob("0[3-7]_*.py")`: os dois scripts que o achado 6.7 nomeia (`01` e `02`) estão fora por construção. |
| A2-08 | confirmado (sobrepõe A4-04) | `git ls-files docs/evidencias/E8/` devolve cinco arquivos, todos texto; nenhuma captura versionada. A2 trata do lado "status ✅ sem marca de contestado", A4-04 do lado "evidência que a tela mostra"; os dois vão para o mesmo ticket. |
| A2-09 | confirmado | `E6/ollama_desligado.txt` anota `exit=0` logo abaixo de "1 verificação(ões) falharam", e `scripts/00_checar_ambiente.py:66-68` sai com 1 nesse caso. O `exit=0` do arquivo é do `tee`, não do Python. |
| A2-10 | confirmado | Verificado no arquivo: em `E7/t03_fontes_notebook.txt:11-25`, "Fontes citadas" e "Trechos enviados ao prompt" são as mesmas quatro linhas, idênticas. É a manifestação em evidência do achado A1-08 do piloto. |
| A2-11 | confirmado | `VERIFICACAO.md:187`: "Trocar `MODELO_CHAT` para `qwen2.5:1.5b` … funciona sem outra alteração". Desde o #19 o 1.5b é o padrão, então o critério testa a troca no sentido que deixou de existir. |
| A2-12 | confirmado (leitura) | O Shapley pré-computado é anterior ao T12 e ao #19. Não reexecutei (`calcular_shapley_chunks.py` leva ~10 min e usa o LLM). |
| A2-13 | confirmado (leitura) | Arquivo é auto-relato, sem saída de comando, e nenhum critério o cita. Baixa. |
| A2-14 | confirmado | O próprio `E7/log_02_indexar.txt` declara a reconstrução; o Registro de 2026-09-16 também. Baixa, mas precisa ficar visível. |
| A2-15 | confirmado | Mesma verificação de A2-01, estendida a E1 e E3. |
| A2-16 | confirmado (sobrepõe A5-09) | A cobertura de 10.3 endossa a entrada de troubleshooting que o T12 tornou falsa. |

## A3 — Material didático (14 achados)

| # | Veredito | Validação independente |
|---|---|---|
| A3-01 | confirmado | `grep -c arxiv.org ferramentas/construir_notebook.py` = 6; `rocha2025`/`medeiros2025` não aparecem. O notebook lista 6 dos 8 artigos e chama todos de arXiv. |
| A3-02 | confirmado | Lido em `E7/t03_fontes_notebook.txt:11-25`: as duas listas são idênticas, quatro linhas iguais. Confirma A1-08 no material da aula. |
| A3-03 | **confirmado — e é o mais grave do eixo** | `construir_notebook.py:149`: `if REINDEXAR or colecao.count() != len(chunks):`. Com `REINDEXAR = False`, basta a contagem divergir para o notebook reindexar ao vivo. O comentário da linha 52 promete "alguns minutos"; a evidência mais recente registra 1420 s. |
| A3-04 | confirmado (leitura) | O ramo `else` do `LLM_AO_VIVO` no bloco 5 troca a alucinação pela recusa; o contraste que o critério 6.3 demonstra desaparece no plano B. |
| A3-05 | confirmado | `construir_notebook.py:182-191`: há `if LLM_AO_VIVO:` sem `else`. Com o plano B ligado, o bloco 2.5 simplesmente não mostra resumo ao vivo — sem rede de segurança, contra o critério 7.6. |
| A3-06 | confirmado (leitura das quatro medições) | — |
| A3-07 | confirmado (leitura) | O auditor declara confiança média por ter uma medição só; concordo com a classificação. |
| A3-08 | confirmado (leitura) | — |
| A3-09 | confirmado (leitura) | Mesma família de A2-12. |
| A3-10 | confirmado (leitura) | — |
| A3-11 | **confirmado, sem ticket novo** | É exatamente a issue #24, já aberta e ainda não implementada. Ver [`devolucoes/A3-11.md`](devolucoes/A3-11.md): o achado é correto, mas o backlog do #36 deve apontar para #24 em vez de criar duplicata. |
| A3-12 | confirmado (leitura) | — |
| A3-13 | confirmado, com ressalva | `scripts/03_buscar.py:25` de fato trocou o filtro vazio por `idioma=pt`, que hoje retorna resultados. Mas o critério 3.6 continua coberto por `verificar.py:114` (`ano>=2030`). O achado vale pelo lado didático (a demonstração sumiu da aula), não pelo lado de cobertura. |
| A3-14 | confirmado (leitura) | — |

## A4 — Aplicação Streamlit (14 achados)

| # | Veredito | Validação independente |
|---|---|---|
| A4-01 | **confirmado por leitura das próprias imagens** | Abri `8.4a_k2.png` e `8.4b_k6.png`. Nas duas, a legenda da resposta diz `k = 4` e o expander diz "Fontes (citadas 1 de 4)", embora o slider mostre 2 e 6. As capturas que deveriam provar o efeito de k provam que ele não chegou ao backend. |
| A4-02 | confirmado | Na mesma leitura, `8.4a_k2.png` mostra a última resposta cortada no meio ("Quais problemas aparecem quando"), o que corrobora o diagnóstico de sincronização do achado. |
| A4-03 | confirmado (leitura da imagem) | — |
| A4-04 | confirmado (sobrepõe A2-08) | `git ls-files` sem nenhuma captura. |
| A4-05 | confirmado | `grep -n "falhar("` devolve exatamente três chamadas (`:59`, `:70`, `:81`). Os outros pontos só imprimem. |
| A4-06 | **confirmado, mas eu corrijo o alcance de A1-08** | Ver "Correção do parecer do piloto", abaixo. O comportamento condicional descrito no achado está certo; o que muda é a frequência. |
| A4-07 | confirmado | `app.py:73-77` rerenderiza o histórico sem a legenda; `app.py:92` só existe dentro do bloco `if pergunta:`. |
| A4-08 | confirmado | `app.py:52` monta o `selectbox` com `[config.MODELO_CHAT, config.MODELO_CHAT_PLANO_B]`; com `MODELO_CHAT=qwen2.5:3b` no ambiente, as duas opções ficam iguais. |
| A4-09 | confirmado (leitura) | — |
| A4-10 | confirmado | A pasta `capturas/` não tem `8.8_ollama_indisponivel.png` nem `capturas.txt` — a execução parou antes do fim, exatamente como o achado descreve. |
| A4-11 | confirmado, confiança média | Coerente com o que vi em `8.4a_k2.png`. O mecanismo exato não foi isolado; a classificação do auditor é honesta. |
| A4-12 | confirmado (leitura) | — |
| A4-13 | confirmado | `capturar_app.py:41` tem o parâmetro `interagir`, e `capturar_evidencias_e8.py` importa apenas `subir_app`. O parâmetro criado para o T15 não é usado pelo T15. |
| A4-14 | confirmado (leitura) | — |

## A5 — Documentação e números (20 achados)

| # | Veredito | Validação independente |
|---|---|---|
| A5-01 | confirmado | `medicoes.md:20` publica "Chunking (556 chunks) \| 9,0 s" citando `E7/log_02_indexar.txt`, que hoje registra o corpus de 659. |
| A5-02 | confirmado | Mesma linha de evidência: o log termina em `em 1420s`, não 1104,1 s. |
| A5-03 | confirmado | `README.md:114` promete "cerca de 20 minutos (1104 a 1141 s)"; a medição atual é 1420 s (23,7 min). |
| A5-04 | confirmado | `medicoes.md:94` já registra 190,7 s para a extração; a tabela 9.1 mantém 16,6 s. O documento se contradiz internamente. |
| A5-05 | confirmado (leitura) | — |
| A5-06 | confirmado | `medicoes.md:33` lista "37 · 34 · 48 · 36 s (última execução: 2026-09-15)"; o valor atual, de 2026-09-16, é 50 s e não aparece. |
| A5-07 | **confirmado — o mais grave do eixo** | `medicoes.md:53` publica "AppTest, 3b, 8 s · 17 s" citando `E8/apptest.txt`, cujo conteúdo atual é `qwen2.5:1.5b` e "pergunta 1 respondida em 44s". A linha 100 usa esses números para orçar o bloco 7 em "~4 perguntas no pior caso" — é o único achado que derruba uma conclusão do critério 9.4. |
| A5-08 | confirmado | `medicoes.md:3` afirma "medidos entre 13 e 14/09/2026"; as linhas 10, 33 e 94 citam dados de 15 e 16/09. |
| A5-09 | confirmado | `troubleshooting.md:50-52` manda responder no chat que "ainda não há artigos em português". São dois desde o T12, e o AppTest recupera o `medeiros2025_embeddings_pt.pdf`. Risco ao vivo real: o facilitador daria uma informação falsa. |
| A5-10 a A5-16 | confirmados (leitura) | Cada referência de linha conferida; nenhuma errada. |
| A5-17 | **confirmado — erro meu** | `git rev-list --count 4d6a16b` = 34, não 25 como escrevi em `docs/ESTADO_ATUAL.md`. O documento de contexto da auditoria publicou um número que não conferi. |
| A5-18 a A5-20 | confirmados (leitura) | — |

## A6 — Reprodutibilidade e ambiente (11 achados)

O eixo foi interrompido por limite de uso da sessão e retomado; entregou com o HEAD já avançado de
`eec1ecc` para `631da36`, e o próprio auditor registrou que reconferiu que nada do seu escopo havia
mudado. Boa prática, anotada aqui porque nenhuma regra do protocolo a exigia.

| # | Veredito | Validação independente |
|---|---|---|
| A6-01 | **confirmado — e é o achado mais grave da rodada inteira** | `grep -n "checar("` em `scripts/00_checar_ambiente.py` devolve 7 chamadas: Python 3.10+, ambiente virtual, os 6 imports, servidor Ollama e modelos baixados. Nenhuma corresponde a 0.2 ou a 0.5 — `grep -c "pip\|requirements"` no arquivo devolve **0**, e `OLLAMA_MODELS` aparece só num `print("[INFO] …")` na linha 63. O critério 0.8 afirma que o script "cobre 0.1–0.6" e está ✅. Pela letra do critério, o ✅ é falso. |
| A6-02 | confirmado, com ressalva | `pacotes` em `scripts/00:37` é `["ollama", "chromadb", "streamlit", "pypdf", "shap", "numpy"]`; `matplotlib==3.11.2` está em `requirements.txt:9` e `scripts/05_shap.py:36` chama `shap.plots.text`. O script aprova um ambiente sem `matplotlib`. **Ressalva:** a falha concreta não foi demonstrada por remoção do pacote, porque desinstalar está proibido nesta rodada; o achado se apoia na cadeia declarada, não em execução. Mantenho severidade alta pelo impacto (bloco de 12 minutos, traceback depois de ~40 s de cálculo) e registro a ressalva. |
| A6-03 | confirmado | `grep -cin "dist-info\|requirements.lock\|force-reinstall" docs/troubleshooting.md` devolve **0**, e a mesma busca em `verificar.py` + `scripts/00` devolve 0 linhas. O modo de falha que derrubou o ambiente no piloto (A1-00) continua sem detecção e sem entrada de troubleshooting; o comando de reparo existe apenas dentro do protocolo de auditoria, que o participante não lê. |
| A6-04 a A6-11 | confirmados (leitura) | Referências de linha conferidas por amostragem; nenhuma errada. |

**Nota técnica que o eixo trouxe e vale preservar:** `importlib.metadata.Distribution.files` aplica
`skip_missing_files()` no Python 3.12 e **descarta em silêncio** os arquivos ausentes — ou seja, a
checagem mais óbvia para detectar o problema de A1-00 daria falso negativo. O auditor caiu nessa
armadilha na primeira versão da própria sonda, corrigiu lendo o `RECORD` como texto e validou o
detector contra um `site-packages` sintético. Isso é exatamente o que a regra de "repetir a medição"
do ticket #28 existe para provocar.

**Estado conferido sem achado:** critério 10.5 limpo (132 arquivos versionados, nenhum PDF, `.venv`,
`chroma_db` ou modelo), os três arquivos de requirements consistentes entre si, `pip freeze` idêntico
ao lock e a `.venv` íntegra por duas medições independentes. Registro isto porque "nada errado aqui"
também é resultado de auditoria, e este é o eixo onde o piloto encontrou a falha crítica.

---

## Correção do parecer do piloto (eixo A1)

O achado **A1-08** afirma que, com `qwen2.5:1.5b`, "o modelo não emite nenhuma citação `[n]` nas
respostas positivas salvas". A afirmação está correta para o corpo de evidência que ele examinou
(`resultados/com_sem_contexto.json` e `E7/t03_fontes_notebook.txt`), mas **a leitura das capturas de
tela do T15 mostra o contrário em outra execução**: em `8.4a_k2.png` e `8.4b_k6.png`, a resposta cita
`[1]` e o expander mostra "Fontes (citadas **1** de 4)".

Conclusão corrigida, que é a que vale para o backlog: com o modelo padrão atual, **a citação é
intermitente**. Quando ela não acontece — o que ocorreu em 2 de 2 respostas positivas salvas em
`resultados/`, e nas duas células do notebook — o fallback lista todo o top-k e a tela afirma que a
resposta usou tudo. A severidade alta se mantém, porque o comportamento não confiável é pior para a
aula do que o comportamento ausente: o facilitador não tem como prever se a demonstração de 6.5 vai
funcionar na hora.

---

## Lacunas abertas pelo CTO

### LACUNA A2 — ninguém checou se as checagens que reprovam reprovam pelo motivo certo

- **onde:** `ferramentas/verificar.py`, as 8 funções que chamam `sys.exit`
- **por-que-era-do-escopo-A2:** o eixo provou que 7 de 15 não reprovam nunca (A2-03), o que é metade do
  trabalho. A outra metade é: das que reprovam, alguma reprova por motivo errado, ou passa por motivo
  errado? `e9_numeros` já foi corrigido uma vez por esse tipo de falha (ticket #10).
- **o-que-investigar:** para cada uma das 8, construir uma entrada que **deveria** reprovar e verificar
  se reprova. O padrão de `e7_duplicadas_antes_v2` — que roda a checagem contra uma versão antiga e
  conhecida do arquivo — é o modelo a seguir, e já está no repositório.

### LACUNA A4 — frequência real da citação com o modelo padrão

- **onde:** `rag.py:365`, `app.py:31`, `resultados/com_sem_contexto.json`
- **por-que-era-do-escopo-A4:** o eixo teve uso exclusivo do Ollama e demonstrou o comportamento
  condicional (A4-06), mas não mediu com que frequência o `qwen2.5:1.5b` cita. As capturas do T15
  mostram citação; as respostas salvas em `resultados/`, não.
- **o-que-investigar:** N perguntas repetidas com `seed=42` fixo, contando em quantas o modelo emite
  `[n]`. Sem esse número, o consolidado não consegue dizer ao autor se a demonstração de 6.5 é
  confiável ao vivo ou se precisa de plano B — e essa é uma decisão que o ensaio de 21/09 vai cobrar.

---

## Placar final (A2–A6)

| Eixo | Propostos | Confirmados | Reclassificados | Rejeitados | Duplicados | Lacunas |
|---|---:|---:|---:|---:|---:|---:|
| A2 | 16 | 15 | 0 | 0 | 1 (A2-05, parcial) | 1 |
| A3 | 14 | 14 | 0 | 0 | 1 (A3-11 = issue #24) | 0 |
| A4 | 14 | 14 | 0 | 0 | 1 (A4-04 sobrepõe A2-08) | 1 |
| A5 | 20 | 20 | 0 | 0 | 0 | 0 |
| A6 | 11 | 11 | 0 | 0 | 0 | 0 |
| **Total** | **75** | **74** | **0** | **0** | **3** | **2** |

Somando o piloto (8 achados, 6 confirmados), a RODADA-1 fecha com **83 achados propostos e 80
confirmados**, sendo 24 de severidade alta e 2 críticos (A1-00, ambiente quebrado; A6-01, ✅ falso no
critério 0.8).

**Leitura.** Nenhuma rejeição e nenhuma referência de linha errada na amostra que reproduzi — resultado
oposto ao do piloto, onde 1 de 8 caiu por erro de medição. As duas regras acrescentadas pelo ticket #28
(repetir toda medição numérica com uma segunda entrada; ler os comentários `why:`/`hazard:` antes de
classificar) aparecem aplicadas nos quatro relatórios, inclusive na forma de confiança rebaixada para
média quando a segunda medição não foi possível (A3-07, A4-11, A4-12, A2-11, A2-12). A calibração do
#28 pagou o próprio custo.

O único ajuste estrutural necessário é de **fronteira entre eixos**, não de qualidade: três achados
descrevem o mesmo fato por ângulos diferentes. Estão marcados como duplicados com dono definido, para
o consolidado (#36) não gerar três tickets para um problema só.
