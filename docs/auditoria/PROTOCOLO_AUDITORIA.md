# Protocolo de auditoria multiagente com validação CTO

Define **como** o repositório é auditado: quem audita o quê, em que formato o achado é entregue, como
o agente CTO valida, e como um achado rejeitado volta para o auditor com erro, localização e correção
recomendada. Os prompts prontos para colar estão em [`PROMPT_AUDITORIA.md`](PROMPT_AUDITORIA.md).

Contexto de partida obrigatório: [`../ESTADO_ATUAL.md`](../ESTADO_ATUAL.md), [`../VERIFICACAO.md`](../VERIFICACAO.md), `CLAUDE.md`.

---

## 1. Princípios

1. **Achado sem evidência não existe.** Todo achado carrega arquivo, linha e a saída do comando que o
   demonstra. "Parece errado" é hipótese, não achado.
2. **Auditor não corrige.** As rodadas de auditoria são **só leitura**: nenhum auditor edita arquivo,
   roda `git`, muda status em `VERIFICACAO.md` ou abre ticket. Quem decide o que vira correção é o CTO;
   quem corrige é um agente de implementação, depois, ticket a ticket.
3. **O CTO valida contra o código, não contra o relatório.** Ele reabre o arquivo citado e confere;
   um achado que ele não conseguiu reproduzir volta rejeitado, não vira "provavelmente verdade".
4. **Rejeição é acionável.** O CTO nunca devolve "está errado": devolve o erro, onde está, por que a
   análise falhou e qual é a melhor forma de refazer/corrigir, com critério de aceite.
5. **Nenhum critério é afrouxado.** Se um critério de `VERIFICACAO.md` não passa, o resultado é achado,
   nunca reescrita do critério.
6. **Falso negativo é falha de auditoria.** O CTO também procura o que o auditor deixou passar dentro
   do escopo dele, e isso volta como pendência da mesma forma.

## 2. Papéis

| Papel | Quantidade | Permissões | Entrega |
|---|---|---|---|
| **Orquestrador** | 1 (sessão principal) | tudo | Dispara auditores, encaminha rejeições, consolida |
| **Auditor** | 6 (eixos A1–A6) | leitura + execução de comandos de verificação; **sem escrita, sem git write** | `docs/auditoria/rodadas/RODADA-N/A<k>-achados.md` |
| **CTO** | 1 | leitura + execução; **sem escrita fora de `docs/auditoria/`** | `docs/auditoria/rodadas/RODADA-N/cto-parecer.md` + devoluções |
| **Implementador** | 1 por ticket, fora da auditoria | escrita | Commit por ticket, seguindo o fluxo do `CLAUDE.md` |

Um auditor nunca valida o próprio achado. O CTO nunca escreve achado novo em nome de um auditor: ele
devolve ao eixo dono do escopo.

## 3. Os seis eixos

| Eixo | Nome | Escopo | Pergunta central |
|---|---|---|---|
| **A1** | Pipeline RAG | `rag.py`, `config.py` | O pipeline faz o que diz fazer, inclusive nos casos de borda (fallback por limiar, recusa, citação parcial, filtro vazio, entrada vazia no embedding)? |
| **A2** | Verificação e evidências | `docs/VERIFICACAO.md`, `docs/evidencias/**`, `ferramentas/verificar.py` | Cada ✅ tem evidência que realmente demonstra o critério? Alguma checagem passa sem checar nada? |
| **A3** | Material didático | `webinario_rag.ipynb`, `ferramentas/construir_notebook.py`, `scripts/**`, `docs/roteiro_facilitador.md` | O material roda de ponta a ponta na máquina de quem assiste, na ordem e no tempo do cronograma, com rede de segurança nas etapas lentas? |
| **A4** | Aplicação Streamlit | `app.py`, `ferramentas/testar_app.py`, `capturar_app.py`, `capturar_evidencias_e8.py`, `docs/evidencias/E8/**` | Os critérios 8.1–8.8 se sustentam no app real, com evidência do que a tela mostra? |
| **A5** | Documentação e números | `README.md`, `CLAUDE.md`, `docs/medicoes.md`, `docs/troubleshooting.md`, `docs/ESTADO_ATUAL.md`, plano v1.1 | Todo número e toda afirmação batem com o código e com a última medição desta máquina? |
| **A6** | Reprodutibilidade | `requirements*.txt/lock`, `.gitignore`, `scripts/00`, `rodar_scripts.sh`, estado do git | Um participante partindo de zero chega ao app funcionando sem conhecimento prévio nem arquivo que não está no repo? |

Fronteiras: um achado pertence ao eixo **dono do arquivo citado**. Achado que cruza eixos vai para o
eixo do arquivo que precisa mudar, com referência cruzada no campo `relacionado`.

## 4. Formato do achado

Cada auditor entrega um arquivo markdown com um bloco por achado, nesta estrutura exata:

```markdown
### A3-04 — Notebook regenerado perde as saídas pré-computadas

- **severidade:** alta
- **categoria:** correcao | evidencia | documentacao | reprodutibilidade | didatico | risco-ao-vivo
- **onde:** `ferramentas/construir_notebook.py:312`, `webinario_rag.ipynb` (célula 27)
- **criterio:** 7.2, 7.6
- **decisao-documentada:** <obrigatório quando a região tem `why:`/`hazard:` — cite a linha do
  comentário e diga por que a decisão registrada ali não cobre o caso; omita quando não houver>
- **o-que-observei:** <fato, sem interpretação>
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python ferramentas/verificar.py e7_saidas
  ```
- **saida-obtida:** <trecho literal, no máximo 15 linhas>
- **por-que-importa:** <impacto concreto na aula ou em quem replica>
- **confianca:** alta | média | baixa
- **relacionado:** A5-02
```

Regras de preenchimento:

- `onde` sempre com linha. Se for o notebook, identificar a célula **e** o trecho de
  `construir_notebook.py` que a gera (o `.ipynb` não se edita à mão).
- **Todo número reportado vem de duas medições**, com entradas de forma e tamanho diferentes. Uma
  medição só é hipótese. O piloto (#27) rejeitou um achado inteiro por isso.
- **`decisao-documentada` é obrigatório quando a região tem `why:`/`hazard:`.** Achado que contradiz
  uma decisão registrada sem sequer citá-la é rejeitado por falta de contexto, não julgado no mérito.
- Script de sonda usado para chegar ao achado é versionado na pasta da rodada, com a saída salva.
- `como-reproduzir` precisa ser um comando que o CTO consiga rodar. Se o achado for textual, o comando
  é o `grep` que o localiza.
- `confianca: baixa` é permitido e preferível a omitir — o CTO decide o que fazer com isso.
- Sem propor correção. A recomendação de implementação é do CTO.

**Severidade**

| Nível | Significado |
|---|---|
| **crítica** | Quebra a aula ao vivo, ou um ✅ é falso (critério não se sustenta) |
| **alta** | Quem replica em casa trava, ou número publicado está errado |
| **média** | Divergência real sem impacto imediato na execução (doc defasada, evidência fraca) |
| **baixa** | Ruído, inconsistência cosmética, oportunidade de clareza |

## 5. Formato do parecer do CTO

Um bloco por achado recebido, mais uma seção de lacunas:

```markdown
### A3-04 — CONFIRMADO
- **veredito:** confirmado | rejeitado | reclassificado | duplicado
- **como-validei:** <comando que rodei e o que vi, independente do auditor>
- **severidade-final:** alta (auditor: alta)
- **acao:** ticket | correcao-imediata | aceitar-como-conhecido | descartar
```

Quando o veredito é **rejeitado** ou **reclassificado**, o bloco de devolução é obrigatório e vai
neste formato, que é literalmente o que volta para o auditor:

```markdown
### DEVOLUÇÃO A3-04 → auditor A3

1. **Erro:** <o que exatamente está errado no achado — fato incorreto, linha errada,
   comportamento mal interpretado, severidade fora da escala, achado duplicado>
2. **Onde:** `arquivo:linha` — <o que o código realmente faz ali, citado>
3. **Evidência contrária:** <comando + saída que refuta ou corrige o achado>
4. **Como refazer:** <o caminho correto de análise: qual função seguir, qual caso de
   borda testar, qual comando rodar, qual arquivo de evidência ler antes>
5. **Critério de aceite:** <o que o achado revisado precisa conter para ser aceito>
```

Quando o CTO encontra algo que o auditor **deveria** ter achado:

```markdown
### LACUNA A1 — fallback não coberto para filtro + limiar simultâneos
- **onde:** `rag.py:242-265`
- **por-que-era-do-escopo-A1:** <justificativa>
- **o-que-investigar:** <instrução concreta>
```

## 6. O ciclo

```
Rodada N
  │
  ├─ Orquestrador prepara o pacote de contexto (ESTADO_ATUAL + VERIFICACAO + CLAUDE.md + escopo do eixo)
  │
  ├─ A1 … A6 auditam em paralelo, só leitura ──────────┐
  │                                                     │
  ├─ CTO lê os 6 relatórios e valida cada achado        │
  │     ├─ confirmado ───────────────► backlog          │
  │     ├─ reclassificado ──► DEVOLUÇÃO ──┐             │
  │     ├─ rejeitado ───────► DEVOLUÇÃO ──┤             │
  │     └─ lacuna ──────────► LACUNA ─────┤             │
  │                                        ▼            │
  └─ Auditor do eixo refaz SÓ os itens devolvidos ──────┘
        (nova rodada parcial; máximo 3 rodadas por eixo)
```

**Critérios de saída da rodada.** A rodada fecha quando, para cada eixo:

- todo achado tem veredito do CTO, e
- toda devolução foi respondida (achado corrigido, ou retirado pelo auditor com justificativa), e
- nenhuma lacuna aberta permanece sem investigação.

**Limite de 3 rodadas por eixo.** Se um item não converge em 3 idas e voltas, o CTO decide unilateralmente
e registra a decisão com o motivo — o material tem data de entrega (21/09) e auditoria não pode virar
loop infinito.

## 7. Saída da auditoria

Ao fim, o CTO produz `docs/auditoria/rodadas/RODADA-N/consolidado.md` com:

1. **Bloqueadores da aula** — críticos e altos, em ordem de risco para 21/09.
2. **Backlog de tickets** — um item por ticket futuro, no formato do `docs/agents/issue-tracker.md`
   (título, corpo, critério de `VERIFICACAO.md` afetado, label sugerida).
3. **Critérios contestados** — quais ✅ de `VERIFICACAO.md` ficaram sob suspeita e o que os reabilita.
4. **Aceites conscientes** — o que foi visto, não será corrigido, e por quê.
5. **Placar da auditoria** — por eixo: achados propostos, confirmados, rejeitados, lacunas. É o
   controle de qualidade dos próprios auditores.

A auditoria **não muda nenhum status** em `VERIFICACAO.md`. Ela produz achados e tickets; a mudança de
status só acontece depois, quando a correção foi implementada e reverificada com evidência nova — como
já foi feito na auditoria de 2026-09-14 (`docs/evidencias/E10/revisao_codigo.md`).

## 8. Organização dos arquivos

```
docs/auditoria/
├── PROTOCOLO_AUDITORIA.md      (este documento)
├── PROMPT_AUDITORIA.md         (prompts prontos)
└── rodadas/
    └── RODADA-1/
        ├── A1-achados.md … A6-achados.md
        ├── cto-parecer.md
        ├── devolucoes/A3-04.md …
        └── consolidado.md
```

## 9. Salvaguardas

- **Ambiente conferido antes da rodada.** `pip check` e `scripts/00_checar_ambiente.py` precisam sair
  com 0 antes de qualquer eixo começar. No piloto (#27) a `.venv` estava com os diretórios de código de
  ~31 distribuições apagados e os `dist-info` intactos: `pip list` dava tudo como instalado e
  `import chromadb` falhava. Reparo: `pip install --force-reinstall --no-deps -r requirements.lock`,
  excluindo `pip`, `setuptools` e `wheel` — incluí-los faz o pip travar no meio da própria
  reinstalação. Salve a evidência em `docs/evidencias/E0/`.
- **Só leitura na auditoria.** Se um auditor precisar rodar algo que escreve (`02_indexar.py` recria a
  coleção; `executar_notebook.py` sobrescreve saídas), ele **não roda**: registra como "não verificável
  sem efeito colateral" e passa ao CTO, que decide.
- **Nada de reindexar durante a auditoria** — destrói a base usada pelas outras verificações e invalida
  qualquer medição em curso.
- **Worktrees fora do escopo.** `.claude/worktrees/**` contém cópias antigas; auditar só a raiz.
- **Ollama é recurso único.** Dois auditores chamando o LLM ao mesmo tempo, em 7,9 GB de RAM, degradam
  a medição e falseiam tempos. Comandos que usam o Ollama rodam **um de cada vez**, coordenados pelo
  orquestrador.
- **Alucinação de linha é achado rejeitado.** Citar `arquivo:linha` que não contém o que o achado diz é
  motivo automático de devolução, com severidade registrada no placar do eixo.
