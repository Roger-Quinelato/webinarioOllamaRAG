# Roadmap — `gerar_notebook_publico.py`: chunking menor + notebook mais didático

> Documento gerado a partir de uma sessão de grilling (perguntas/respostas) em 2026-09-21/22.
> Todas as decisões abaixo já passaram por trade-off e foram confirmadas pelo autor — **não reabrir
> o debate**, só implementar. Se surgir uma dúvida de escopo durante a implementação que não está
> coberta aqui, é preferível perguntar a assumir.

## Contexto

- Arquivo-fonte: [`notebooks/gerar_notebook_publico.py`](../notebooks/gerar_notebook_publico.py) —
  gera `notebooks/rag_com_seus_documentos.ipynb` (material público do webinário CIIA, MIG-06).
  **Nunca editar o `.ipynb` diretamente**: sempre editar o `.py` e rodar
  `python notebooks/gerar_notebook_publico.py` para regenerar.
- Duas motivações originais do autor:
  1. `TAMANHO_CHUNK = 1000` estava "pegando quase a página inteira" — reduzir.
  2. Tornar chunks e overlap visíveis/ilustrativos para os participantes.
- Isso evoluiu, durante o grilling, para um escopo maior: tornar o notebook mais didático para um
  público que **já programa mas é novo em RAG/LLM** (não confundir com iniciante em Python).
- Restrição de tempo do webinário: **não há limite rígido** — "a pessoa pode estudar em casa
  depois", então extensão de conteúdo não é um problema, desde que cada peça nova seja concreta e
  conectada ao que já existe (nada de encher linguiça).

## Estado atual relevante (fatos, não decisões — conferir se ainda válidos antes de implementar)

- `TAMANHO_CHUNK = 1000` (slider 200–4000, step 100), `SOBREPOSICAO = 150` (slider 0–800, step 50)
  — seção 3, por volta da linha 286 do `.py`.
- Já existe `mostrar_sobreposicao()` (seção 3) que compara **dois** chunks vizinhos e destaca com
  `<mark>` o trecho repetido — mas para no primeiro par encontrado e pode não achar nada
  silenciosamente. Será **substituída**, não mantida em paralelo.
- Lista do bloco "🧪 Experimente" em seção 3: `(300, 500, 1000, 2000, 4000)`.
- Seções com bloco `🎓 Aprofundando` **depois** do código funcional (candidatas ao "passo 4" novo):
  2 (carregar), 4 (embeddings), 5 (banco vetorial), 6 (recuperação), 8 (prompt e cadeia RAG).
- Seções que **não** entram nessa rodada: 1 (upload, é logística), 3 (já reformulada nesta rodada),
  7 (não tem bloco 🎓 rico o bastante pra justificar), 9 e 10 (já intercalam teoria/código bem).
- A ordem atual dessas seções já é `explicação básica (md) → código funcional (exemplo real) →
  🎓 aprofundamento (md)` — ou seja, os "passos 1-2-3" do ciclo pedagógico já existem nessa ordem.
  **Não é necessário reordenar nada existente**; falta só adicionar o "passo 4" (ver Fase 4).

## Decisões consolidadas

### A. Chunking (tamanho/overlap)
- Novo padrão: `TAMANHO_CHUNK = 700`, `SOBREPOSICAO = 150` (~21%, mantém o overlap absoluto atual).
- Faixa do slider (`min`/`max`/`step`) **não muda** — o propósito é o participante explorar de
  extremo a extremo.
- Lista do "🧪 Experimente" recentralizada: `(300, 500, 700, 1200, 2500)`.
- Texto teórico das seções 3 e 11 (tabela-resumo de parâmetros) **não muda** — a faixa genérica
  "500–1000 caracteres, 10–20% overlap" já cobre 700/150.

### B. Nova visualização de chunks + overlap (substitui `mostrar_sobreposicao()`)
- Escolhe a **página com mais chunks** (critério robusto contra documento enviado pelo participante
  ter capa/primeira página curta).
- Mostra o **texto completo da página**, fatiado com uma cor de fundo por chunk, e as zonas de
  overlap destacadas de forma diferente (dupla cobertura).
- Limite de segurança: se a página passar de ~6000 caracteres, avisa e mostra só os primeiros N
  chunks/fronteiras em vez do texto inteiro.
- Liga por padrão (sempre roda), com parâmetro `⚙️` para desligar quem quiser.
- Tratar graciosamente o caso `SOBREPOSICAO = 0` (sem cor de overlap, só os blocos por chunk).

### C. Célula de abertura — "tour conceitual" (nova, antes da seção "0. Antes de começar")
- Público-alvo: já programa, novo em RAG/LLM (não sabe o que é embedding/retriever/chain).
- Explica **o notebook como um todo** (não uma seção específica), em 4 passos:
  1. **Explicação básica** — reaproveitar/expandir o diagrama ASCII + tabela de etapas que já
     existem na introdução (não duplicar).
  2. **Exemplo** — narrado em prosa (sem código): uma pergunta fictícia → busca de 3 trechos →
     resposta citando `[1][2]`.
  3. **Aprofundamento** — por que RAG existe (memória paramétrica vs. não-paramétrica, o problema
     que resolve); hoje esse conteúdo está disperso na seção 11 ("RAG × fine-tuning").
  4. **Código comentado** — pseudo-pipeline curto e ilustrativo, **não executa o pipeline real**
     (evita duplicar lógica/manutenção dobrada); deixar explícito que o de verdade começa na seção 1.
- Posição: antes da seção "0. Antes de começar" (o participante entende o que vai construir antes
  da parte operacional de escolher provedor/colar chave).
- Sem limite de tamanho rígido, mas manter enxuto ("uma tela, não uma aula").

### D. "Passo 4" novo em 5 seções técnicas (fecha o ciclo pedagógico)

Cada uma ganha uma célula de código **nova** (não reaproveita o código funcional já existente),
comentada, logo depois do bloco `🎓 Aprofundando` já existente, demonstrando concretamente o tópico
do aprofundamento daquela seção:

| Seção | Tópico do 🎓 | Demo do passo 4 |
|---|---|---|
| 2. Carregar | PDF é desenho, não texto; hifenização; OCR | Comparar o mesmo trecho **com e sem** `LIMPAR_TEXTO`, mostrando a hifenização quebrada sendo corrigida |
| 4. Embeddings | Prefixos `query:`/`passage:` do E5; esquecê-los derruba qualidade **sem erro visível** | Recalcular a similaridade **sem os prefixos** e comparar com o resultado original |
| 5. Banco vetorial | Busca exata O(n) vs. ANN/HNSW | Comparar tempo de busca por cosseno "na unha" (numpy) vs. Chroma, com nota honesta de que a diferença só aparece em escala |
| 6. Recuperação | MMR, calibração de limiar — **puxa o "estado da arte" da seção 10** | Prévia rápida de busca híbrida (BM25 + vetorial) na mesma pergunta de teste, comparando lado a lado com a busca simples |
| 8. Prompt e cadeia | Lost-in-the-middle; prompt injection | Simular um chunk malicioso ("ignore as instruções…") e mostrar a regra 4 do prompt reagindo (ou não) |

## Fora de escopo (adiado, decisão explícita — não fazer nesta rodada)

- Reordenar/reescrever o ciclo completo (explicação → exemplo → aprofundamento → código) dentro de
  **todas** as 11 seções. Só as 5 da tabela acima recebem o "passo 4" novo nesta rodada.
- Qualquer alteração nas seções 1, 3 (além do já decidido em B), 7, 9, 10, 11 além do que está listado
  aqui.

---

## Roadmap incremental

Ordem pensada por risco crescente: primeiro mudança numérica pura (reversível, sem risco), depois
mudanças de conteúdo autocontidas, por último as adições distribuídas em várias seções (mais
trabalho, mas cada uma é independente e pode ser feita/revisada isoladamente).

### Fase 1 — Ajustes numéricos de chunking
**Objetivo:** aplicar a decisão A sem tocar em nada estrutural.
**Mudanças:**
- `TAMANHO_CHUNK = 700`, `SOBREPOSICAO = 150` (valores-padrão do `@param`).
- Lista do "🧪 Experimente" → `(300, 500, 700, 1200, 2500)`.
**Arquivos:** só `gerar_notebook_publico.py`, seção 3.
**Critério de pronto:** notebook regenerado, célula de chunking mostra os novos padrões, célula de
comparação usa a nova lista.
**Risco:** nenhum — é troca de literal, sem lógica nova.

### Fase 2 — Nova visualização de página/chunks/overlap
**Objetivo:** aplicar a decisão B, substituindo `mostrar_sobreposicao()`.
**Mudanças:**
- Função que escolhe a página com mais chunks.
- Renderização HTML com cor por chunk + destaque de overlap (reaproveitar o padrão `display(HTML(...))`
  já usado em `mostrar_sobreposicao()`).
- Truncamento de segurança (~6000 caracteres) com aviso.
- Parâmetro `⚙️` para desligar (default ligado).
**Arquivos:** `gerar_notebook_publico.py`, seção 3 (substitui a célula "Veja a sobreposição em ação").
**Critério de pronto:** rodar com o documento de exemplo (Lewis et al. 2020) e confirmar que aparece
uma página com múltiplos chunks coloridos e overlap visível; testar também com `SOBREPOSICAO = 0`
para confirmar que não quebra.
**Risco:** baixo/médio — depende do documento de exemplo ter uma página com chunks suficientes;
testar com o PDF de exemplo padrão (`URL_EXEMPLO`) antes de considerar pronto.
**Depende de:** Fase 1 (usa o novo `TAMANHO_CHUNK` para gerar os chunks que serão visualizados).

### Fase 3 — Célula de abertura ("tour conceitual")
**Objetivo:** aplicar a decisão C.
**Mudanças:**
- Novo bloco markdown + código, inserido antes da seção "0. Antes de começar".
- Reaproveita o diagrama/tabela já existentes no topo do notebook como passo 1.
- Passos 2 e 3 em markdown (prosa).
- Passo 4: pseudo-código ilustrativo (pode ser um bloco de código **não executável de fato**, ou
  markdown com syntax highlighting — decidir na implementação; se for célula de código real, deixar
  claro no texto que é ilustrativo e não faz parte do pipeline).
**Arquivos:** `gerar_notebook_publico.py`, logo após a introdução geral e antes da seção 0.
**Critério de pronto:** célula nova legível em poucos parágrafos, sem duplicar o diagrama/tabela do
topo, com nota explícita "você vai construir isso de verdade a partir da seção 1".
**Risco:** nenhum — é conteúdo novo, autocontido, sem dependência de código de outras seções.
**Independente das Fases 1, 2 e 4** — pode ser feita em qualquer ordem relativa a elas.

### Fase 4 — "Passo 4" nas 5 seções técnicas
**Objetivo:** aplicar a decisão D, seção por seção. Pode ser feita como 5 sub-entregas
independentes (uma por seção) se for útil revisar aos poucos.
**Sub-fases sugeridas (qualquer ordem):**
- 4.1 — Seção 2 (comparação com/sem `LIMPAR_TEXTO`)
- 4.2 — Seção 4 (comparação com/sem prefixos E5)
- 4.3 — Seção 5 (tempo de busca numpy vs. Chroma)
- 4.4 — Seção 6 (prévia de busca híbrida vs. simples — atenção: usa `BM25Retriever`, que só é
  importado na seção 10 hoje; ou importa cedo aqui também, ou reaproveita depois — decidir na
  implementação para não duplicar import/lógica desnecessariamente)
- 4.5 — Seção 8 (chunk malicioso / prompt injection)
**Arquivos:** `gerar_notebook_publico.py`, uma célula nova de código (+ markdown curto de transição)
logo após o bloco `🎓 Aprofundando` de cada seção listada.
**Critério de pronto (por sub-fase):** célula roda sem erro com o documento de exemplo, demonstra
visivelmente o ponto do aprofundamento (ex.: mostra os dois textos lado a lado, mostra a nota de
similaridade mudando, mostra o tempo de execução, mostra a citação inválida sendo pega).
**Risco:** médio na 4.4 (antecipar `BM25Retriever` da seção 10 pode exigir mover um import ou aceitar
reimportar) — as demais são isoladas e de baixo risco.
**Depende de:** Fase 1 (chunks/overlap já no tamanho novo) para os exemplos ficarem consistentes com
o resto do notebook.

---

## Como validar cada fase

```bash
python notebooks/gerar_notebook_publico.py
```

Conferir que o script roda sem erro e imprime `... gerado com N células`. Idealmente, abrir o
notebook gerado (Jupyter local ou Colab) e rodar **de cima a baixo** pelo menos uma vez por fase — em
especial a Fase 2 e a Fase 4.4, que têm mais risco de dependência entre células.
