# Roteiro do facilitador — Encontro 2

**Condução:** Roger Quinelato · **Suporte no chat:** João Victor Rikio Enomoto · **Duração:** ~1h54 (ajustar após o ensaio de 21/09)

Tempos reais de cada etapa nesta máquina: [medicoes.md](medicoes.md). Problemas e respostas prontas para o chat: [troubleshooting.md](troubleshooting.md).

## Antes da live (T-30 min)

1. Feche os programas pesados. O LLM divide CPU e RAM com a transmissão.
2. Abra o aplicativo Ollama e rode `python scripts/00_checar_ambiente.py`. A saída tem que terminar em `Ambiente pronto.`
3. Rode `python scripts/07_ollama.py` uma vez para aquecer o modelo. A primeira resposta é a mais lenta: carregar um modelo levou de 40 a 80 s nesta máquina. Na aula, use **um único modelo de chat** do começo ao fim. Trocar de modelo custa outra carga e, na medição, derrubou o 3b para 3 tokens/s ([medicoes.md](medicoes.md), 9.3).
4. Abra o `webinario_rag.ipynb` no VS Code com o kernel **Python (webinario-rag)** e confira `REINDEXAR = False`, `LLM_AO_VIVO = True` e `SHAP_AO_VIVO = True`. Com menos de 1 GB de RAM livre, comece com `SHAP_AO_VIVO = False`.
5. Em outro terminal, deixe `streamlit run app.py` pronto, mas ainda sem abrir o navegador.
6. Envie ao João os links do repositório, do vídeo de instalação e do troubleshooting.

**Plano B geral:** se o LLM travar, mude `LLM_AO_VIVO = False` (ou `SHAP_AO_VIVO = False`), rode a célula de configuração e depois a célula que travou. Todas as células lentas carregam o resultado salvo em `resultados/`. O notebook inteiro nesse modo foi testado e roda em 61 s.

**Modelo ao vivo (decisão parcial do autor, 2026-09-15 — ticket #19):** `config.MODELO_CHAT` agora é `qwen2.5:1.5b` por padrão, para validar a pipeline inteira primeiro; `qwen2.5:3b` vira o "plano B" em `config.MODELO_CHAT_PLANO_B`, para testar depois se a máquina/o notebook aguenta bem no ensaio de 21/09. O 1.5b respondeu em ~20 s contra 42–164 s do 3b nesta máquina. Perguntas-teste definitivas ainda não foram definidas (fica para depois; ticket #19 segue aberto para essa parte).

---

## Bloco 1 — Recapitulando o pipeline RAG (10 min)

- **Fala:** "No Encontro 1 o João mostrou por que LLMs alucinam e como o RAG resolve. Hoje a gente constrói o pipeline inteiro, na máquina local, sem framework, para enxergar cada peça."
- **Demo:** diagrama do bloco 1 no notebook, depois a célula `verificar_ollama`, que mostra os três modelos.
- **Instalação:** não instalar ao vivo. Mostrar 1 min do vídeo do YouTube do CIIA e o README.
- **Checkpoint:** "Quem vai replicar depois: o passo a passo está no README, do Ollama até o Streamlit."
- **Plano B:** se o Ollama não responder, abrir o aplicativo e rodar a célula de novo. Enquanto isso, seguir com o diagrama.

## Bloco 2 — Indexação (18 min)

- **Fala:** "Metadado é decisão de engenharia: escolhemos `ano`, `tema` e `idioma` porque viram filtros."
- **Demo, em ordem:**
  1. Tabela do `metadados.csv`.
  2. Chunking da página 3 do Lewis 2020, mostrando a sobreposição entre dois chunks.
  3. Contagem de chunks por artigo e por tipo (`pagina` × `resumo`).
  4. Célula de indexação. Com `REINDEXAR = False`, ela só reabre a coleção; mostrar a dimensão do vetor e os metadados.
  5. Extração de metadados pelo LLM × CSV, apontando onde o LLM erra.
  6. Resumo do abstract ao vivo × resumo salvo no CSV.
- **Checkpoint:** "Por que o resumo também é indexado como um chunk?" A resposta prepara o bloco 3b.
- **Tempo medido:** extração 16,6 s e resumo 8,1 s com o modelo aquecido; 135 s e 232 s frios.
- **Plano B:** extração ou resumo lentos → `LLM_AO_VIVO = False`. **Nunca reindexar ao vivo:** leva 1104–1141 s, mais que o bloco inteiro.

## Bloco 3 — Retrieval top-k na prática (15 min)

- **Fala:** "Distância de cosseno: quanto menor, mais parecido. Aumentar o k traz mais contexto, mas também mais ruído."
- **Demo:**
  1. Mesma pergunta com k = 1, 4 e 8; comentar em que posição os trechos deixam de ser relevantes.
  2. Filtros `ano >= 2023`, `tema = retrieval` e `idioma = pt` (T12/#12: 2 artigos em português já entram no filtro).
  3. Cross-lingual: pergunta em português e em inglês; comparar as distâncias.
- **Checkpoint:** pedir no chat um valor de k para uma pergunta e testar ao vivo.
- **Plano B:** nenhum. A busca não usa o LLM, só embedding, e é rápida.

## Bloco 3b — Busca em dois estágios (7 min)

- **Fala:** "Primeiro escolhemos os artigos pelos resumos; depois buscamos os trechos só dentro deles."
- **Demo:** as duas células do bloco 3b.
  1. "Como avaliar se a resposta é fiel ao contexto recuperado?": o estágio 1 **ajuda** e o top-4 fica só com o Ragas.
  2. "Recuperar mais documentos sempre melhora a resposta do modelo?": o estágio 1 **atrapalha**. A busca simples acha o *Lost in the Middle*, mas o resumo dele não fala em "mais documentos" e o artigo fica de fora.
- **Checkpoint:** "Então resumo bom é pré-requisito. Como vocês gerariam resumos melhores?"
- **Plano B:** a saída salva em `docs/evidencias/E4/04_dois_estagios.txt` mostra os dois casos.

## Bloco 4 — SHAP (12 min)

- **Fala (obrigatória):** "Isto explica o **retrieval**: quais palavras da pergunta aproximam o vetor dela do vetor do chunk. Não explica o raciocínio do LLM."
- **Demo:**
  1. Célula do SHAP ao vivo: gráfico de texto e checagem de aditividade (base + soma = similaridade).
  2. Tabela do Shapley dos chunks, pré-computada: "quanto cada trecho contribuiu para a resposta final".
- **Checkpoint:** "Que palavra da pergunta vocês trocariam para trazer outro chunk?"
- **Tempo medido:** 19–41 s com o `bge-m3` já carregado e até 112 s frio ou com pouca RAM.
- **Plano B:** `SHAP_AO_VIVO = False` mostra o gráfico salvo (`resultados/shap_similaridade_chunk1.html`).

## Bloco 5 — Prompt augmentation: com e sem contexto (12 min)

- **Fala:** "O RAG não muda o modelo; muda o prompt."
- **Demo:**
  1. Prompt montado impresso, com instruções, trechos numerados e a pergunta.
  2. Mesma pergunta sem contexto × com contexto.
  3. Tabela com as outras perguntas salvas, incluindo a pergunta fora da base.
- **Checkpoint:** "Onde a resposta sem contexto inventou algo?"
- **Plano B:** `LLM_AO_VIVO = False`.
- **Pendência do autor:** substituir as perguntas marcadas com `TODO` pelas definitivas.

## Bloco 6 — Integração com Ollama (12 min)

- **Fala:** "`responder()` junta busca, prompt e chamada ao Ollama em streaming, e devolve as fontes."
- **Demo:** célula de streaming e depois `config.py`, mostrando que trocar o modelo é uma linha.
- **Checkpoint:** mostrar a tabela de velocidade de medicoes.md em vez de trocar de modelo ao vivo: 3b com ~7 tokens/s de geração, 1.5b com ~14 tokens/s.
- **Plano B:** `LLM_AO_VIVO = False` mostra a resposta salva em `resultados/resposta_bloco6.md`.

## Bloco 7 — Chatbot com Streamlit (15 min)

- **Fala:** "O app é uma casca: todas as funções vêm do `rag.py`."
- **Demo:**
  1. Mostrar o código do `app.py` (célula do bloco 7).
  2. Terminal: `streamlit run app.py`.
  3. Fazer duas perguntas seguidas para mostrar o histórico.
  4. Mudar o k, filtrar por tema, alternar simples × dois estágios.
  5. Abrir o expander de fontes, que mostra arquivo, página, trecho e resumo.
- **Checkpoint:** pedir uma pergunta do chat e fazê-la no app. No máximo 4 perguntas neste bloco: sem cache, cada resposta do 3b levou 42–118 s.
- **Atenção:** o envio é pelo botão de seta; nos testes, o Enter não enviou.
- **Plano B:** se o Ollama cair, o app mostra o aviso sem quebrar; reabra o Ollama. Trocar o modelo na barra lateral custa outra carga de 40–80 s, então só faça isso em último caso.
- **Decisão do autor, 2026-09-15 (ticket #14, respondida em chat):** o seletor de modelo (`st.selectbox("Modelo de chat", ...)`) e o botão "Limpar conversa" **ficam no app**, contra a recomendação do ticket de tirar o seletor — o autor prefere poder trocar de modelo ao vivo na demo. Nenhuma mudança de código foi necessária (os dois já existem em `app.py`); esta é só a decisão registrada.

## Bloco 8 — Avaliação, reranking e próximos passos (8 min)

- **Fala:** apresentar RAGAS (fidelidade, relevância da resposta, precisão do contexto), reranking com cross-encoder, "lost in the middle" e busca híbrida.
- **Demo:** tabela da avaliação no estilo RAGAS, se tiver sido gerada.
- **Checkpoint:** "Qual das três métricas vocês olhariam primeiro no projeto de vocês, e por quê?"
- **Plano B:** se `resultados/avaliacao_estilo_ragas.json` não existir, a célula avisa. Explique as métricas pelo slide.
- **Encerramento:** links do repositório e do vídeo, pesquisa de avaliação e perguntas.

## Folga (5 min)

A folga absorve atrasos dos blocos 2, 5 e 7, que são os que usam o LLM.
