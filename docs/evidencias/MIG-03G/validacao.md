# Evidência de validação real — MIG-03G / #70

Data: 2026-09-20

## Resultado observado

Uma chamada mínima real foi feita pelo `ProviderOpenAI`, com credencial
configurada, ao endpoint Responses usando `gpt-5.6-luna`. A requisição alcançou
a OpenAI, mas não concluiu a geração: o provider retornou
`ErroProviderOpenAI` com os seguintes dados seguros:

```text
status_code=429
retry_after=None
mensagem=A OpenAI atingiu o limite de requisições. Aguarde um momento e tente novamente.
```

Nenhuma chave, conteúdo de entrada ou conteúdo de saída foi registrado. A
chamada não foi repetida durante o registro desta evidência.

## Estado do aceite

O critério de uma resposta real com status `completed` permanece pendente.
A issue #70 continua aberta e bloqueada pela normalização da quota ou do limite
da conta OpenAI. Esse bloqueio impede o aceite final da migração e o gate
pré-webinar, mas não impede MIG-04, já liberada pelo gate CTO híbrido.
