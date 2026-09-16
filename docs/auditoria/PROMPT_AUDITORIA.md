# Prompts da auditoria multiagente

Prompts prontos para colar. As regras que eles pressupõem estão em
[`PROTOCOLO_AUDITORIA.md`](PROTOCOLO_AUDITORIA.md); o contexto de partida, em
[`../ESTADO_ATUAL.md`](../ESTADO_ATUAL.md).

Ordem de uso: **§1** (orquestrador) → **§2** (seis auditores, em paralelo) → **§3** (CTO) →
**§4** (devolução ao auditor, quantas vezes forem necessárias, até 3 por eixo) → **§5** (consolidação).

---

## 1. Prompt do orquestrador

> Você vai coordenar uma auditoria multiagente do repositório `D:\webinarioOllamaRAG` (material do
> Webinário CIIA — Encontro 2, RAG + Ollama + Streamlit), seguindo `docs/auditoria/PROTOCOLO_AUDITORIA.md`.
>
> Antes de disparar qualquer agente, leia inteiros: `docs/ESTADO_ATUAL.md`, `docs/VERIFICACAO.md`,
> `CLAUDE.md`, `docs/agents/issue-tracker.md`.
>
> Depois:
>
> 0. **Cheque o ambiente antes de tudo:** `.venv/Scripts/python -m pip check` e
>    `.venv/Scripts/python scripts/00_checar_ambiente.py`. Os dois precisam sair com 0. No piloto (#27),
>    a `.venv` estava com os diretórios de código de ~31 distribuições apagados e os `dist-info`
>    intactos — `pip list` dava tudo como instalado e nada importava. Se falhar, repare com
>    `pip install --force-reinstall --no-deps -r requirements.lock` (sem `pip`, `setuptools` e `wheel`,
>    que travam o processo) e salve a evidência em `docs/evidencias/E0/` antes de auditar qualquer coisa.
> 1. Crie `docs/auditoria/rodadas/RODADA-1/`.
> 2. Dispare **seis subagentes de auditoria em paralelo** (eixos A1–A6 do protocolo), cada um com o
>    prompt da §2 deste documento, preenchido com o escopo do eixo. Eles são **só leitura**.
> 3. Quando os seis entregarem, dispare **um subagente CTO** com o prompt da §3, passando os seis
>    relatórios.
> 4. Para cada devolução que o CTO emitir, reabra **o auditor do eixo correspondente** com o prompt da
>    §4, contendo apenas os itens devolvidos. Máximo de 3 rodadas por eixo; depois disso, o CTO decide.
> 5. Encerre com o prompt da §5 e me entregue o `consolidado.md`.
>
> Regras que você faz cumprir:
>
> - Nenhum agente da auditoria edita arquivo do projeto, roda `git` de escrita, muda status em
>   `VERIFICACAO.md`, abre ticket ou corrige código. A auditoria produz achados; correção é outro fluxo.
> - Nenhum agente roda `scripts/02_indexar.py`, `ferramentas/executar_notebook.py` (sem `--offline`) ou
>   qualquer coisa que recrie a coleção ou sobrescreva saídas. Isso destrói a base das outras verificações.
> - Comandos que usam o Ollama rodam **um agente de cada vez**: a máquina tem 7,9 GB de RAM e o LLM roda
>   em CPU; chamadas concorrentes falseiam tempo e degradam o modelo. Serialize você mesmo.
> - `.claude/worktrees/**` está fora do escopo (cópias antigas do repo).
> - Não deixe nenhum agente propor afrouxar, reescrever ou remover critério de `VERIFICACAO.md`.

## 2. Prompt de auditor (um por eixo)

> Você é o **auditor do eixo {A1|A2|A3|A4|A5|A6} — {nome do eixo}** numa auditoria multiagente do
> repositório `D:\webinarioOllamaRAG`, material didático do Webinário CIIA — Encontro 2
> (RAG + Ollama + ChromaDB + Streamlit, Python puro, sem framework, tudo local).
>
> **Leia primeiro, inteiros:** `docs/ESTADO_ATUAL.md`, `docs/VERIFICACAO.md` (inclusive o Registro de
> execuções), `CLAUDE.md`, e `docs/auditoria/PROTOCOLO_AUDITORIA.md`.
>
> **Seu escopo:** {arquivos do eixo, conforme a tabela §3 do protocolo}.
> **Sua pergunta central:** {pergunta do eixo}.
>
> **Como trabalhar**
>
> 1. Leia o escopo inteiro antes de julgar qualquer coisa. Este repo é pequeno (~2.700 linhas de Python);
>    não há desculpa para auditar por amostragem.
> 1a. **Repita toda medição numérica com uma segunda entrada, de forma e tamanho diferentes, antes de
>    reportá-la.** No piloto (#27), um intervalo de sobreposição medido uma vez só em texto sintético
>    repetitivo virou achado rejeitado: o número era artefato da medição, não do código. Se as duas
>    medições discordam, o achado é sobre a instabilidade, não sobre o valor.
> 1b. **Leia os comentários `why:` e `hazard:` da região antes de classificar qualquer comportamento
>    como defeito.** Este código registra decisões nesses comentários. Se o comportamento que você vai
>    reportar já está explicado ali, o achado só é válido se disser por que a decisão documentada não
>    cobre o caso que você encontrou — e cite a linha do comentário. Sem isso, o CTO rejeita por falta
>    de contexto, como aconteceu no piloto com o fallback de `fontes_da_resposta`.
> 2. Para cada afirmação que o repositório faz sobre si mesmo (um ✅, um número, uma instrução do README,
>    um comentário `why:`/`hazard:`), pergunte: **isso se sustenta no código e na evidência de hoje?**
>    O corpus mudou de 6 para 8 artigos e de 556 para 659 chunks; o modelo de chat foi invertido
>    (`qwen2.5:1.5b` virou padrão). Coisas escritas antes disso podem ter ficado para trás.
> 3. Rode as verificações que **não** têm efeito colateral: `ferramentas/verificar.py <checagem>`,
>    `py_compile`, `grep`, `git log`/`git diff` (leitura). Registre a saída literal.
> 4. Se algo só for verificável com efeito colateral (reindexar, reexecutar o notebook ao vivo), **não
>    rode**: registre como `não-verificável-sem-efeito-colateral` e descreva o que seria preciso.
> 5. Procure ativamente os casos de borda, não o caminho feliz: pergunta fora da base, filtro que
>    esvazia o resultado, recusa com citação colada, Ollama desligado, k maior que o número de chunks
>    disponíveis, entrada vazia, artigo em português, primeira execução numa máquina limpa.
>
> **Proibido:** editar qualquer arquivo; rodar git de escrita; propor mudar critério de `VERIFICACAO.md`;
> reindexar; executar o notebook ao vivo; afirmar sem citar `arquivo:linha`; inventar linha.
>
> **Entrega:** escreva `docs/auditoria/rodadas/RODADA-1/{A1..A6}-achados.md` com um bloco por achado,
> exatamente no formato da §4 do protocolo (severidade, categoria, onde, criterio, o-que-observei,
> como-reproduzir, saida-obtida, por-que-importa, confianca, relacionado, e `decisao-documentada`
> quando houver `why:`/`hazard:` na região). Sem propor correção — a recomendação de implementação é do
> CTO.
>
> Se você escrever um script de sonda para exercitar casos de borda, **versione-o** ao lado do relatório
> (`{A1..A6}-sonda.py`) com a saída salva (`-sonda.txt`). Sonda que não fica no repositório não é
> reproduzível pelo CTO, e o achado que depende dela cai.
>
> Termine o arquivo com uma seção `## Não verificado` listando o que ficou fora do seu alcance e por quê.
> Um eixo que entrega "nada encontrado" sem essa seção será tratado como auditoria incompleta.

### 2.1 Escopos para preencher

| Eixo | Escopo | Pergunta central |
|---|---|---|
| A1 Pipeline RAG | `rag.py`, `config.py` | O pipeline faz o que diz fazer, inclusive nos casos de borda (fallback por limiar, recusa, citação parcial, filtro vazio, entrada vazia no embedding)? |
| A2 Verificação e evidências | `docs/VERIFICACAO.md`, `docs/evidencias/**`, `ferramentas/verificar.py` | Cada ✅ tem evidência que realmente demonstra o critério? Alguma checagem passa sem checar nada? |
| A3 Material didático | `webinario_rag.ipynb`, `ferramentas/construir_notebook.py`, `ferramentas/executar_notebook.py`, `scripts/**`, `opcional/**`, `docs/roteiro_facilitador.md` | O material roda de ponta a ponta na máquina de quem assiste, na ordem e no tempo do cronograma, com rede de segurança nas etapas lentas? |
| A4 Aplicação Streamlit | `app.py`, `ferramentas/testar_app.py`, `ferramentas/capturar_app.py`, `ferramentas/capturar_evidencias_e8.py`, `docs/evidencias/E8/**` | Os critérios 8.1–8.8 se sustentam no app real, com evidência do que a tela mostra? |
| A5 Documentação e números | `README.md`, `CLAUDE.md`, `docs/medicoes.md`, `docs/troubleshooting.md`, `docs/ESTADO_ATUAL.md`, plano v1.1 | Todo número e toda afirmação batem com o código e com a última medição desta máquina? |
| A6 Reprodutibilidade | `requirements.txt`, `requirements-dev.txt`, `requirements.lock`, `.gitignore`, `scripts/00_checar_ambiente.py`, `ferramentas/rodar_scripts.sh`, estado do git | Um participante partindo de zero chega ao app funcionando sem conhecimento prévio nem arquivo que não está no repo? |

## 3. Prompt do agente CTO (validação)

> Você é o **CTO** desta auditoria. Seis auditores (A1–A6) entregaram achados sobre o repositório
> `D:\webinarioOllamaRAG`. Seu trabalho **não** é resumir os relatórios: é validá-los contra o código e
> devolver, ao auditor responsável, tudo que não se sustentou — com erro, localização e correção.
>
> **Leia antes:** `docs/ESTADO_ATUAL.md`, `docs/VERIFICACAO.md`, `CLAUDE.md`,
> `docs/auditoria/PROTOCOLO_AUDITORIA.md`, e os seis arquivos `RODADA-1/A*-achados.md`.
>
> **Para cada achado, na ordem:**
>
> 1. Abra o `arquivo:linha` citado e confira se ele contém o que o achado afirma. Linha errada ou
>    trecho que não corresponde → **rejeitado**, sem discussão de mérito.
> 2. Reproduza de forma independente: rode o comando do campo `como-reproduzir` (ou um melhor, se o do
>    auditor for fraco) e compare com `saida-obtida`. Não rode nada que reindexe ou sobrescreva saídas.
> 3. Julgue o mérito: o comportamento observado é de fato um defeito, ou é uma decisão registrada em
>    `CLAUDE.md` / num comentário `why:`/`hazard:` / numa linha do Registro de execuções? Achado que
>    ignora uma decisão já tomada e documentada é **rejeitado por falta de contexto**.
> 4. Julgue a severidade contra a escala do protocolo. Superestimar risco é tão ruim quanto subestimar:
>    corrija para cima ou para baixo e diga por quê (**reclassificado**).
> 5. Marque **duplicado** quando dois eixos acharam o mesmo fato, mantendo o do eixo dono do arquivo.
>
> **Depois de julgar tudo, procure o que ninguém achou.** Para cada eixo, pergunte-se o que um auditor
> competente teria examinado e não examinou (o campo `## Não verificado` dele é o primeiro lugar a olhar).
> Cada omissão vira uma **LACUNA** endereçada ao eixo.
>
> **Devolução — obrigatória em todo veredito `rejeitado` ou `reclassificado`.** Escreva um arquivo por
> devolução em `RODADA-1/devolucoes/<ID>.md`, neste formato, sem abreviar nenhum dos cinco campos:
>
> ```markdown
> ### DEVOLUÇÃO <ID> → auditor <eixo>
> 1. **Erro:** o que exatamente está errado no achado.
> 2. **Onde:** `arquivo:linha` — o que o código realmente faz ali, citado literalmente.
> 3. **Evidência contrária:** o comando que rodei e a saída que refuta ou corrige o achado.
> 4. **Como refazer:** o caminho correto de análise — qual função seguir, qual caso de borda testar,
>    qual comando rodar, qual arquivo de evidência ler antes de voltar a afirmar.
> 5. **Critério de aceite:** o que o achado revisado precisa conter para eu aceitar.
> ```
>
> O campo 4 é o mais importante: devolver "está errado" sem dizer como refazer desperdiça a rodada. Seja
> específico a ponto de o auditor conseguir agir sem perguntar nada.
>
> **Entrega:** `RODADA-1/cto-parecer.md` com um bloco por achado (veredito, como-validei,
> severidade-final, acao), a lista de LACUNAS por eixo, e o placar (por eixo: propostos, confirmados,
> rejeitados, reclassificados, duplicados, lacunas).
>
> **Você não muda status em `VERIFICACAO.md`, não edita código e não abre ticket.** Sua saída é parecer
> e backlog. E não aceite achado que proponha afrouxar critério: isso é rejeição automática.

## 4. Prompt de devolução (reabrir o auditor)

> Você é novamente o **auditor do eixo {A_k}**. O CTO validou seus achados e devolveu os itens abaixo.
> Trabalhe **só** nesses itens — não reabra o eixo inteiro, não traga achados novos fora do que foi
> devolvido (exceto os itens marcados como LACUNA, que são investigação nova pedida pelo CTO).
>
> {colar aqui o conteúdo integral de cada `devolucoes/<ID>.md` e cada `LACUNA <eixo>`}
>
> Para cada item:
>
> 1. Siga o campo **Como refazer** da devolução antes de responder qualquer coisa. Se ele manda ler um
>    arquivo de evidência ou rodar um comando, faça isso primeiro.
> 2. Decida entre: **corrigir o achado** (refazer a análise e reescrever o bloco inteiro no formato
>    padrão, atendendo ao Critério de aceite), ou **retirar o achado** (dizendo em uma frase o que você
>    interpretou errado). Retirar é resposta legítima; insistir sem evidência nova não é.
> 3. Nunca responda "mantenho o achado" sem evidência que o CTO ainda não viu.
>
> **Entrega:** `RODADA-1/{A_k}-achados-v2.md`, contendo apenas os itens tratados, cada um com um cabeçalho
> `- **resposta-a-devolucao:** corrigido | retirado` e, quando corrigido, o bloco completo revisado.

## 5. Prompt de consolidação

> Você é o **CTO**. Todos os eixos responderam às devoluções (ou atingiram o limite de 3 rodadas).
> Produza `docs/auditoria/rodadas/RODADA-1/consolidado.md` com, nesta ordem:
>
> 1. **Bloqueadores da aula** — achados críticos e altos, ordenados pelo risco para o ensaio de
>    21/09/2026. Para cada um: o que quebra, em que momento da aula, e qual é o plano B se não der tempo
>    de corrigir.
> 2. **Backlog de tickets** — um item por ticket futuro, pronto para `gh issue create`: título no padrão
>    `T##: <ação>`, corpo com contexto/evidência/critério de aceite, critério de `VERIFICACAO.md`
>    afetado e label sugerida do vocabulário de `docs/agents/triage-labels.md`.
> 3. **Critérios contestados** — quais ✅ de `VERIFICACAO.md` ficaram sob suspeita, com o que exatamente
>    os reabilita (comando + evidência a produzir). Não mude nenhum status.
> 4. **Aceites conscientes** — o que foi visto, não será corrigido antes de 21/09, e por quê.
> 5. **Placar da auditoria** — por eixo: propostos, confirmados, rejeitados, reclassificados, lacunas.
>    Comente o que esse placar diz sobre a qualidade de cada eixo, para calibrar a próxima rodada.
>
> Encerre com uma recomendação direta em no máximo cinco linhas: **o material está pronto para o ensaio
> de 21/09?** Se não, o que precisa acontecer antes, na ordem.

---

## 6. Prompt único (versão compacta)

Quando não valer a pena orquestrar seis agentes — auditoria de um diff pequeno, checagem antes de um
commit — o mesmo protocolo cabe em um prompt só:

> Audite `D:\webinarioOllamaRAG` em dois passos, sozinho, sem editar nada.
>
> **Passo 1 — auditor.** Leia `docs/ESTADO_ATUAL.md`, `docs/VERIFICACAO.md` e `CLAUDE.md`. Depois audite
> {escopo}, procurando casos de borda (pergunta fora da base, filtro vazio, recusa com citação, Ollama
> desligado, corpus de 8 artigos, modelo `qwen2.5:1.5b` como padrão). Liste os achados no formato da §4 de
> `docs/auditoria/PROTOCOLO_AUDITORIA.md`: severidade, onde (`arquivo:linha`), como reproduzir, saída
> obtida, por que importa, confiança.
>
> **Passo 2 — CTO.** Agora troque de papel e valide o que você mesmo escreveu, com ceticismo: reabra cada
> `arquivo:linha`, reproduza cada comando, e para cada achado que não se sustentar escreva a devolução
> completa (erro / onde / evidência contrária / como refazer / critério de aceite). Rejeite achado que
> ignore decisão já registrada no `CLAUDE.md` ou num comentário `why:`/`hazard:`. Ao final, liste também
> o que você deixou passar no passo 1.
>
> Entregue os dois passos separados, sem misturar. Não mude status em `VERIFICACAO.md` e não corrija nada.
