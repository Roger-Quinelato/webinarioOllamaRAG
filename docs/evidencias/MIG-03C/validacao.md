# Evidência MIG-03C — issue #68

Data: 2026-09-20

## Política e configuração

A política determinística escolhe o ponto médio entre a maior distância das
perguntas positivas e a menor distância das perguntas negativas. Isso reserva
margens iguais para variação nos dois lados do intervalo separador. Se os
intervalos se sobrepõem, a calibração reprova em vez de inventar um limiar.

Com os dados reais:

- maior positiva: `0.44007039070129395`;
- menor negativa: `0.5800204873085022`;
- limiar ativo: `0.5100454390048981`;
- margem em cada lado: `0.06997504830360413`.

O valor ativo existe em um único ponto, `config.DISTANCIA_MAXIMA_RETRIEVAL`, e é
consumido tanto pela Fachada RAG quanto pelo script de calibração.

## TDD nos seams públicos

O primeiro teste RED no seam público de calibração falhou porque a política
ainda não existia:

```text
ImportError: cannot import name 'calcular_limiar_com_margem' from 'retrieval_calibration'
FAILED (errors=1)
```

Depois do primeiro GREEN, os testes dos limites reais falharam porque não havia
um valor canônico e a distância negativa ainda passava pelo corte antigo de
`0.60`:

```text
AttributeError: module 'config' has no attribute 'DISTANCIA_MAXIMA_RETRIEVAL'
openai_provider.ErroProviderOpenAI: A geração falhou antes do primeiro token.
FAILED (errors=2)
```

Após o segundo GREEN, a Fachada RAG aceita o limite positivo medido e transforma
o limite negativo em Recusa sem chamar o provider de geração.

## Calibração real completa

Comando:

```text
$env:PYTHONUTF8='1'
.venv\Scripts\python.exe scripts\calibrar_retrieval_hibrido.py
```

Saída completa das oito perguntas positivas e cinco negativas:

```json
{
  "limiar_validado": 0.5100454390048981,
  "limiar_calculado": 0.5100454390048981,
  "maior_distancia_positiva": 0.44007039070129395,
  "menor_distancia_negativa": 0.5800204873085022,
  "margem_positivas": 0.06997504830360413,
  "margem_negativas": 0.06997504830360413,
  "intervalo_seguro": [
    0.44007039070129395,
    0.5800204873085022
  ],
  "positivas": [
    {
      "pergunta": "Como funciona a arquitetura RAG proposta por Lewis et al.?",
      "distancia": 0.4104672074317932,
      "arquivo": "gao2023_survey.pdf"
    },
    {
      "pergunta": "O que é Dense Passage Retrieval (DPR)?",
      "distancia": 0.3088452219963074,
      "arquivo": "karpukhin2020_dpr.pdf"
    },
    {
      "pergunta": "Quais métricas o Ragas usa para avaliar fidelidade e relevância?",
      "distancia": 0.39288443326950073,
      "arquivo": "es2023_ragas.pdf"
    },
    {
      "pergunta": "O que são os tokens de reflexão do Self-RAG?",
      "distancia": 0.34669792652130127,
      "arquivo": "asai2023_selfrag.pdf"
    },
    {
      "pergunta": "Por que a posição da informação no contexto afeta a performance, segundo Lost in the Middle?",
      "distancia": 0.286432683467865,
      "arquivo": "liu2023_lost_middle.pdf"
    },
    {
      "pergunta": "Quais são os principais desafios de RAG discutidos no survey de Gao et al.?",
      "distancia": 0.44007039070129395,
      "arquivo": "gao2023_survey.pdf"
    },
    {
      "pergunta": "Como o DPR treina o retriever com exemplos negativos?",
      "distancia": 0.3437419533729553,
      "arquivo": "karpukhin2020_dpr.pdf"
    },
    {
      "pergunta": "O que é retrieval-augmented generation?",
      "distancia": 0.2875502109527588,
      "arquivo": "gao2023_survey.pdf"
    }
  ],
  "negativas": [
    {
      "pergunta": "Qual é a receita de pão de queijo mineiro?",
      "distancia": 0.6412662267684937,
      "arquivo": "lewis2020_rag.pdf"
    },
    {
      "pergunta": "Qual é a capital da Mongólia?",
      "distancia": 0.581831693649292,
      "arquivo": "asai2023_selfrag.pdf"
    },
    {
      "pergunta": "Quais são as regras do xadrez?",
      "distancia": 0.6048406362533569,
      "arquivo": "lewis2020_rag.pdf"
    },
    {
      "pergunta": "Como trocar o óleo de um carro?",
      "distancia": 0.5800204873085022,
      "arquivo": "rocha2025_ragsft.pdf"
    },
    {
      "pergunta": "Qual é a previsão do tempo para amanhã em Belo Horizonte?",
      "distancia": 0.6257079839706421,
      "arquivo": "asai2023_selfrag.pdf"
    }
  ]
}
```

## Reindexação herdada da issue #67

Coleção `artigos_rag_hibrido_a280e65e16ee`: 8 artigos, 661 chunks e embeddings,
dimensão 1024, duração `1318.342029499996` segundos. A evidência runtime canônica
foi atualizada em [`../MIG-02H/validacao.md`](../MIG-02H/validacao.md).

## Validação final

```text
> .venv\Scripts\python.exe -m unittest discover -s tests -v
Ran 34 tests in 18.477s
OK
TEST_EXIT_CODE=0

> .venv\Scripts\python.exe -m compileall -q config.py openai_rag.py retrieval_calibration.py scripts tests
COMPILE_EXIT_CODE=0

> git diff --check
DIFF_CHECK_EXIT_CODE=0
```

Os avisos do Git sobre futura conversão LF/CRLF são informativos e não indicam
erro de whitespace no diff.

## Estado do gate

MIG-04 continua bloqueada até o gate CTO conjunto da reindexação híbrida e da
Fachada RAG.
