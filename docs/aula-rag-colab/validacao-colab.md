# Roteiro de validação no Google Colab

> Issue [#155](https://github.com/Roger-Quinelato/webinarioOllamaRAG/issues/155) (EDU-COLAB-05.2).

O notebook é gerado e checado fora do Colab (`python notebooks/checar_aula.py`), e a lógica das células foi
exercitada com modelos simulados. **Tempos, memória e o comportamento real dos modelos só podem ser
confirmados no Colab.** Faça este roteiro a cada mudança relevante do gerador ou quando o Colab atualizar
suas bibliotecas.

## Passos

1. Abra `notebooks/aula_rag_colab.ipynb` pelo badge do README.
2. *Ambiente de execução → Alterar o tipo de ambiente → **T4 GPU** → Salvar*.
3. *Ambiente de execução → **Executar tudo***. Na célula de upload, clique em **Cancelar upload** (usa o artigo de exemplo).
4. Ao final, copie a saída da célula **"Diagnóstico da execução"** e cole como comentário na issue #155.
5. Repita enviando um **PDF próprio** (troque as perguntas das §7 e §13).
6. Repita **sem GPU** (*Alterar o tipo de ambiente → CPU*): confira o aviso na §1 e a troca para `Qwen3-1.7B` na §2.

## O que conferir

| Item | Esperado |
|---|---|
| Execução | nenhuma célula com erro nas três variações |
| §2 — pergunta sobre o artigo sem RAG | o modelo não conhece o artigo (diz que não sabe ou inventa) |
| §7 — pergunta boa × receita de bolo | similaridades da pergunta boa maiores |
| §9 — prompt real | mostra `<|im_start|>system`, os trechos numerados e a pergunta |
| §10/§11 — resposta com RAG | pelo menos uma citação `[n]` válida, com arquivo e página |
| §12 — capital da Austrália | recusa ("Não encontrei essa informação…"); se responder "Camberra", registrar |
| Pico de VRAM (diagnóstico) | < 14 GB na T4 |

## Registro

| Data | GPU | LLM | Pico de VRAM | Carregar LLM | Embeddings | Resposta com RAG | tokens/s | Observações |
|---|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | — | aguardando a primeira execução |
