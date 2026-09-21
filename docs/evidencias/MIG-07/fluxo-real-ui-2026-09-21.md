# MIG-07 — fluxo real pela interface Streamlit

> **Registro histórico (corpus anterior).** Medido em 2026-09-21 no corpus de 661 chunks, antes da troca para o corpus só em português. Para o ensaio, vale [`fluxo-real-ui-pt-br-2026-09-21.md`](fluxo-real-ui-pt-br-2026-09-21.md).


**Data da execução:** 2026-09-21, das 01:13 às 01:25
**Branch:** `fix/fin-03-ordem-providers` (PR #114)
**App:** `streamlit run app.py` via `.claude/launch.json`, porta 8501, navegador
embutido
**Ordem de geração:** `GENERATION_PROVIDERS_ORDER=nvidia,gemini,openai` (secrets)
**NVIDIA:** `meta/llama-3.2-11b-vision-instruct`
**Máquina:** CPU apenas (sem GPU NVIDIA); Ollama com `bge-m3`

Este registro guarda o que a interface mostrou e o log `rag.geracao` do
servidor. Não contém chave nem prompt integral.

## 1. Integridade do índice (Corpus Oficial)

Consulta local ao Chroma, sem chamada externa:

| Verificação | Resultado |
|---|---|
| Coleção | `artigos_rag_hibrido_a280e65e16ee`, `status=ready`, `bge-m3-v1`, dimensão 1024 |
| Chunks | 661, com 661 ids únicos e nenhum texto duplicado |
| Tamanho | mín. 160, mediana 995, máx. 999 caracteres |
| Vazios, com menos de 100 caracteres ou com página de bloqueio | 0 |
| Caractere de substituição (`�`) ou nulo | 0 |
| Metadados `arquivo`, `pagina`, `ano`, `idioma` e `tema` faltando | 0 |
| Menos de 50% de letras | 9. A amostra mostra tabelas dos artigos (Lewis, p. 8; Gao, p. 13), não lixo de extração. |
| Chunks por arquivo | Gao 137 · Asai 136 · Lewis 89 · Liu 82 · Karpukhin 73 · Rocha 54 · Medeiros 50 · Es 40 |

Veredito: o índice está íntegro. As 9 tabelas podem ser recuperadas, mas estão
dentro do esperado para PDF sem OCR.

## 2. Matriz de quatro perguntas pela UI

Configuração padrão da sidebar: `k=4` e ano mínimo 2020.

| # | Cenário | Pergunta | Resultado na UI | 1º token (log) |
|---|---|---|---|---:|
| 1 | recuperação | "Como o modelo RAG combina o retriever DPR com o gerador BART?" | Classe `citadas`, NVIDIA. Fonte [1] `lewis2020_rag.pdf` p. 2, distância 0,3481. | 10,0 s |
| 2 | citação | "Quais métricas o Ragas usa para avaliar fidelidade e relevância?" | Classe `citadas`, NVIDIA. Fonte [3] `es2023_ragas.pdf` p. 5, distância 0,4142. | 0,7 s |
| 3 | Recusa | "Qual é a receita de pão de queijo mineiro?" | "Não encontrei essa informação nos documentos." Classe `sem_resultados`, sem geração. | — |
| 4 | filtro | "O que é Dense Passage Retrieval (DPR)?", ano mínimo 2023 | Classe `recusa`, NVIDIA. Nenhum chunk de Karpukhin (2020) no contexto. O modelo recusou diante do contexto de 2023. | 0,7 s |

Após **Limpar conversa**, o histórico foi a 0 mensagens e os filtros da sidebar
continuaram como estavam.

Todas as respostas vieram da NVIDIA na primeira tentativa (`fallback=False`),
com streaming visível e `finish_reason` recebido.

## 3. Achados

1. **Primeira pergunta lenta: cerca de 70 s.** O `POST /api/embed` levou
   1 min 1 s no log do Ollama, que carregava o `bge-m3` a frio na CPU. Depois
   disso, o embedding é imediato. A página também leva uns 30 s para abrir na
   primeira vez (`providers()`). **Ação para o ensaio:** abrir o app e fazer uma
   pergunta de aquecimento antes de começar.
2. **Citação parcial na pergunta 2.** A resposta lista três métricas, mas só a
   primeira traz marcador `[3]`. A frase ligada a esse marcador fala do
   *baseline* com ChatGPT descrito no artigo, e não da métrica do Ragas. A UI
   não inventa fonte, mas o aterramento dessa resposta é fraco. Isso é
   coerente com as 3/9 respostas sem marcador da NVIDIA na
   [FIN-05](../FIN-05/README.md).
3. **Filtro com contexto fraco vira Recusa.** Com `ano >= 2023`, os chunks do
   survey ficam perto do limiar (0,46–0,51), e a NVIDIA recusou. Isso é
   correto, porque não usa conhecimento externo, mas não demonstra o filtro
   bem. **Sugestão para o roteiro:** usar um filtro que mantenha uma fonte
   forte, como `idioma = pt` com uma pergunta sobre embeddings em português,
   respondida por `medeiros2025_embeddings_pt.pdf`.
4. **O subtítulo da UI ainda diz "geração OpenAI, NVIDIA ou Gemini"**
   (`app.py:96`). A ordem não bate com o padrão da ADR-004. É cosmético.
5. **Três Recusas `chunks=0` sem origem identificada** (01:21:15, 01:21:20 e
   01:23:27). O app só consulta o RAG ao receber `chat_input`, então foram
   envios reais. Eles aparecem perto de quando o painel do navegador fechou e
   reabriu. Não foi possível atribuir a causa, e o comportamento não se
   repetiu nas perguntas seguintes.

## 4. Artefato de automação descartado

A primeira tentativa do filtro mudou o slider por injeção de valor no DOM. A UI
mostrou 2023, mas o Streamlit não recebeu o valor: a resposta citou Karpukhin
(2020). Com arraste real do mouse, o filtro foi aplicado. Essa execução não
indica bug do app.

## 5. Log `rag.geracao` (servidor)

```text
01:19:39 geracao provider=NVIDIA tentativa=1 ttft=10.016 fallback=False tentados=NVIDIA
01:19:39 resposta base_ativa=Corpus Oficial provider=NVIDIA chunks=4 status=completa recusa=False parcial=False
01:20:43 resposta base_ativa=Corpus Oficial chunks=0 status=Recusa recusa=True parcial=False
01:20:49 geracao provider=NVIDIA tentativa=1 ttft=0.703 fallback=False tentados=NVIDIA
01:20:49 resposta base_ativa=Corpus Oficial provider=NVIDIA chunks=4 status=completa recusa=False parcial=False
01:24:00 geracao provider=NVIDIA tentativa=1 ttft=0.688 fallback=False tentados=NVIDIA
01:24:00 resposta base_ativa=Corpus Oficial provider=NVIDIA chunks=4 status=completa recusa=True parcial=False
```

O log não trouxe chave, prompt nem texto de resposta (FIN-18).

## 6. Status do critério MIG-07

| Critério | Status |
|---|---|
| As quatro perguntas têm resultado esperado e evidência | ✅ Este registro |
| Falhas de provider são observáveis e não expõem segredo | ✅ Log acima e teste de FIN-18 |
| A pergunta de upload | Adiada por `UPLOADS_STREAMLIT_HABILITADOS=False` (FIN-14) |
| Fallback de provider pela UI | Não exercitado: a NVIDIA respondeu tudo. Já está coberto pela cadeia em [FIN-05](../FIN-05/README.md). |
