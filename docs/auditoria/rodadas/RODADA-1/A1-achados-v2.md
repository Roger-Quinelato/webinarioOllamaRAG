# Eixo A1 — resposta às devoluções e à lacuna (RODADA-1)

**Data:** 2026-09-16 · Trata apenas os itens devolvidos pelo CTO ([`devolucoes/A1-02.md`](devolucoes/A1-02.md),
[`devolucoes/A1-07.md`](devolucoes/A1-07.md)) e a LACUNA A1 do [`cto-parecer.md`](cto-parecer.md).
Os achados A1-00, A1-01, A1-03, A1-04, A1-05 e A1-06 foram confirmados e seguem como estão.

---

### A1-07 — retirado

- **resposta-a-devolucao:** retirado
- **o que interpretei errado:** medi a sobreposição com uma chave de 40 caracteres num texto sintético
  repetitivo, e `str.find` casou uma ocorrência anterior da mesma chave; os "142" eram artefato da
  medição. Repetindo com texto não repetitivo, o valor é constante em 149, um caractere abaixo do
  configurado, por causa do `espaco + 1` de `rag.py:144` que evita começar o chunk no meio de uma
  palavra — comportamento documentado na região. Não há perda de contexto nem palavra cortada.

### A1-02 — corrigido

- **resposta-a-devolucao:** corrigido

### A1-02 (revisado) — Citação exclusivamente a índices inexistentes é indistinguível de "não citou"

- **severidade:** baixa
- **categoria:** correcao
- **onde:** `rag.py:337-344` (`indices_citados`), `rag.py:359-365` (`fontes_da_resposta`)
- **criterio:** 6.5
- **o-que-observei:** quando a resposta cita **exclusivamente** índices fora de `1..n`,
  `indices_citados` devolve lista vazia e o fallback documentado em `rag.py:359-365` lista todos os
  trechos recuperados. Quando há ao menos uma citação válida, o índice inválido é ignorado e só as
  fontes citadas aparecem — esse caso já está correto.
- **como-reproduzir:** `docs/auditoria/rodadas/RODADA-1/cto-sonda.py`, bloco `CTO/A1-02`.
- **saida-obtida:**
  ```
  indices_citados=[2] fontes=[2] <- 'Segundo [2] e [9].'
  indices_citados=[] fontes=[1, 2, 3, 4] <- 'Segundo [9].'
  ```
- **por-que-o-comentário-documentado-não-cobre:** `rag.py:359-365` justifica o fallback pelo caso "o
  modelo não citou nenhum", para "nunca ficar sem fontes". Citar `[9]` com k=4 não é o mesmo evento:
  é o modelo alucinando a numeração, e nesse caso listar tudo dá mais confiança do que a resposta
  merece. A decisão registrada continua válida para o caso que ela nomeia; o que falta é distinguir os
  dois.
- **ocorrência real:** **nenhuma encontrada.** Varri `resultados/com_sem_contexto.json` (3 respostas,
  `qwen2.5:1.5b`) e as citações presentes em `docs/evidencias/E6/*.txt`: todos os índices citados estão
  dentro de `1..4`. Sem ocorrência real, mantenho severidade baixa e confiança média, como pede o
  critério de aceite.
- **confianca:** média
- **relacionado:** A1-08 (a varredura pedida nesta devolução encontrou um problema maior, no sentido
  oposto)

### A1-08 — Com o modelo padrão atual, o fallback dispara sempre e "fontes citadas" vira o top-k inteiro

- **severidade:** alta
- **categoria:** risco-ao-vivo
- **onde:** `rag.py:365`, `config.py:17` (`MODELO_CHAT = "qwen2.5:1.5b"`),
  `resultados/com_sem_contexto.json`
- **criterio:** 6.5
- **o-que-observei:** nas duas respostas respondíveis salvas com o modelo padrão atual, o
  `qwen2.5:1.5b` **não emitiu nenhuma citação `[n]`**, apesar da instrução explícita em
  `INSTRUCOES_SISTEMA` (`rag.py:281`). O fallback entrou nas duas, e `fontes_citadas` no JSON é
  exatamente a lista dos 4 trechos recuperados. A terceira resposta é a recusa, e nela a lista fica
  vazia, correta.
- **como-reproduzir:**
  ```bash
  .venv/Scripts/python -c "import json;d=json.load(open('resultados/com_sem_contexto.json',encoding='utf-8'));[print(r['modelo'],len(r['fontes_citadas']),repr(r['com_contexto'][:60])) for r in d]"
  ```
- **saida-obtida:**
  ```
  qwen2.5:1.5b 4 'Segundo o artigo Lost in the Middle, os modelos usam melhor…'
  qwen2.5:1.5b 4 'No Self-RAG, os tokens de reflexão (reflection tokens) são…'
  qwen2.5:1.5b 0 'Não encontrei essa informação nos documentos.'
  ```
- **por-que-importa:** os tickets #1, #3 e #4 existiram para separar "trecho enviado ao prompt" de
  "fonte que a resposta usou". Com o modelo que o ticket #19 tornou padrão, essa separação não aparece
  em nenhuma resposta positiva: o app mostra "Fontes (citadas 4 de 4)" e marca "✅ citado" em tudo. A
  demonstração do critério 6.5 na aula perde o efeito, e pior, sugere ao espectador que o modelo citou
  quando ele não citou. O caso de recusa continua distinguindo corretamente.
- **o que isto não é:** não é defeito de `fontes_da_resposta`, que está fazendo o que foi especificado.
  É a interação entre a regra e a capacidade do modelo leve — decisão do ticket #19, ainda parcial
  (critério 9.3 está ⏸️).
- **confianca:** alta
- **relacionado:** A1-02; eixos A4 (o que a tela mostra) e A5 (o que a documentação afirma sobre fontes
  citadas)

### A1-09 — `_erro_ollama` manda "abra o Ollama" mesmo quando o servidor respondeu (resposta à LACUNA A1)

- **severidade:** média
- **categoria:** correcao
- **onde:** `rag.py:33-43`, `rag.py:43` (`_ERROS_CONEXAO` inclui `ollama.ResponseError`)
- **criterio:** 6.7
- **o-que-observei:** qualquer `ResponseError` que não seja 404 com modelo conhecido cai na mensagem
  genérica de servidor fora do ar. Um 500 — o retorno típico quando o Ollama está de pé mas falha em
  carregar o modelo por falta de memória — instrui o usuário a abrir um aplicativo que já está aberto.
- **como-reproduzir:** `cto-sonda.py`, bloco `CTO/LACUNA _erro_ollama`.
- **saida-obtida:**
  ```
  status 500 -> Não consegui falar com o Ollama em http://localhost:11434. Abra o aplicativo Ollama
  (ou rode `ollama serve`) e tente de novo. Detalhe: internal server error (status code: 500)
  status 404 -> O modelo 'qwen2.5:1.5b' não está baixado. Rode no terminal: ollama pull qwen2.5:1.5b
  ```
- **por-que-importa:** a máquina de demo tem 7,9 GB de RAM e as medições de E9 registram entre 0,22 e
  0,68 GB livres com os dois modelos carregados. Falha por memória é o erro mais provável ao vivo, e é
  exatamente o que recebe a instrução errada. O critério 6.7 pede "mensagem de erro clara": a mensagem
  é clara, mas aponta para a causa errada.
- **confianca:** alta

---

## Não verificado (continua valendo)

Mantidos da primeira rodada: `shapley_chunks`/`explicar_similaridade` ao vivo, `indexar()` de ponta a
ponta, comportamento de `responder()` com o gerador abandonado no meio, e a causa raiz de A1-00. O item
"determinismo com `seed=42`" saiu desta lista: o CTO o verificou (duas chamadas idênticas devolveram o
mesmo texto) e não gerou achado.
