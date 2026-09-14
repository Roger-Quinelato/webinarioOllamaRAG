O Self-RAG decide quando buscar documentos de acordo com a seguinte descrição encontrada no trecho [1] da documentação asai2023_selfrag.pdf:

1. O SELF-RAG primeiro determina se é útil aumentar a geração subsequente com passagens recuperadas. Se sim, ele gera um token de busca que chama um modelo de busca quando necessário (Passo 1).
2. Em seguida, o SELF-RAG processa simultaneamente múltiplas passagens recuperadas, avaliando sua relevância e gerando correspondentes saídas de tarefas (Passo 2).
3. Em seguida, gera tokens de críticas para criticar sua própria saída e escolher a melhor (Passo 3) em termos de fidedignidade e qualidade geral. 

O Self-RAG diferencia-se de um RAG convencional (ver Figura 1 à esquerda) que não utiliza tokens de reflexão. O Self-RAG introduz "tokens de reflexão" que permitem ao modelo introspecção sobre suas saídas. Estes tokens vêm em duas variedades: "retrieve" e "critic". O modelo decide quando ativar a busca, ou alternativamente, um limiar pré-definido pode iniciar o processo. Durante a busca, o gerador realiza um nível de busca de fragmentos em múltiplas parágrafos para derivar a sequência mais coerente. Os scores de críticas são usados para atualizar os scores de divisão, com flexibilidade para ajustar esses pesos durante a inferência, moldando o comportamento do modelo.

Fontes:
[1] asai2023_selfrag.pdf, p. 1
[2] gao2023_survey.pdf, p. 12
[3] lewis2020_rag.pdf, p. 3
[4] lewis2020_rag.pdf, p. 5