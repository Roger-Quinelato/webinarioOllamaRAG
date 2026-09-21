# ADR-004: ordem configurável dos providers de geração

- **Data**: 2026-09-21
- **Status**: Aceito
- **Decisores**: equipe do webinário
- **Tags**: rag, geração, disponibilidade, FIN-03

## Contexto

A ADR-003 fixou a ordem OpenAI, NVIDIA e Gemini. A conta OpenAI está sem saldo
(HTTP 429 `credit_balance_exhausted`), então cada pergunta gasta uma tentativa
antes de chegar a outro provider. A evidência real de 2026-09-20
([MIG-05](../evidencias/MIG-05/validacao-real-2026-09-20.md)) mostra Gemini
com o menor tempo até o primeiro token quando responde, mas com Recusas na
recuperação e HTTP 503 na citação. NVIDIA foi a única a acertar recuperação,
citação e filtro; a lentidão (20–29 s) vem do modelo de *reasoning*, trocado
pelo padrão `meta/llama-3.2-11b-vision-instruct`, disponível com Free Endpoint
(o `meta/llama-3.1-8b-instruct` anterior não consta do catálogo).
A FIN-03 pede reordenar ou recarregar a conta.

## Decisão

A ordem padrão passa a ser NVIDIA, Gemini e OpenAI. A variável
`GENERATION_PROVIDERS_ORDER`, lida do ambiente e depois de `st.secrets`,
substitui a ordem com nomes separados por vírgula (`gemini`, `nvidia`,
`openai`). Um provider omitido fica desativado mesmo com chave configurada.
Nome desconhecido, repetido ou lista vazia gera aviso acionável na UI, sem
traceback.

As demais regras da ADR-003 continuam: troca somente antes do primeiro token,
**Resposta Parcial** depois dele e nenhum fallback automático para geração
local.

## Consequências

- OpenAI sem saldo deixa de atrasar a primeira tentativa.
- O facilitador ajusta a ordem no dia do ensaio sem alterar código.
- A ordem padrão ainda precisa ser confirmada pela nova matriz da FIN-05. Se
  a NVIDIA com o modelo de instrução ficar lenta ou instável e o Gemini
  responder a recuperação, use `GENERATION_PROVIDERS_ORDER=gemini,nvidia,openai`.

## Links

- Supera somente a ordem de providers da
  [ADR-003](003-fallback-remoto-de-geracao.md).
- Issue FIN-03 (#78).
