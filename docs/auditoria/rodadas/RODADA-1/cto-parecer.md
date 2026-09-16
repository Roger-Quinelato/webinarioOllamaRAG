# Parecer do CTO — RODADA-1 (piloto, eixo A1)

**Data:** 2026-09-16 · **Escopo deste parecer:** os 8 achados de [`A1-achados.md`](A1-achados.md).

Validação independente: cada `arquivo:linha` foi reaberto e cada comportamento foi reproduzido com
**entradas diferentes** das usadas pelo auditor, por script próprio
([`cto-sonda.py`](cto-sonda.py), saída em [`cto-sonda.txt`](cto-sonda.txt)). Nenhum número foi copiado
do relatório do auditor.

---

### A1-00 — CONFIRMADO

- **veredito:** confirmado
- **como-validei:** `pip check` no estado atual devolve `exit=0` e "No broken requirements found", e
  `scripts/00_checar_ambiente.py` sai com 0 — ou seja, o reparo descrito no achado realmente aconteceu.
  O estado original não é mais reproduzível, mas está documentado na evidência de E0 e é coerente com
  a falha de importação que bloqueou o início da auditoria.
- **severidade-final:** crítica (auditor: crítica)
- **acao:** ticket — pertence ao eixo A6; o backlog precisa de (a) uma checagem que detecte
  `dist-info` sem o diretório de código correspondente, porque `pip list` não pega esse caso, e (b) uma
  linha no `troubleshooting.md` com o comando de reparo pelo `requirements.lock`.

### A1-01 — CONFIRMADO

- **veredito:** confirmado
- **como-validei:** testei dois preâmbulos realistas diferentes do usado pelo auditor —
  `"Com base nos trechos fornecidos: <recusa>"` e `"Resposta: <recusa>"`. Ambos devolvem
  `eh_recusa=False` e `fontes=[1, 2, 3, 4]`. O comentário em `rag.py:348-350` documenta a normalização
  de espaços e citações, mas não o prefixo; `startswith` é a limitação real.
- **severidade-final:** média (auditor: média). Não subo para alta porque o caso demonstrado ao vivo
  (`scripts/06`, pergunta do pão de queijo) produziu recusa no início, e o T05 tem evidência disso.
- **acao:** ticket — tratar prefixo antes da frase de recusa, mantendo o critério 6.4 como está.

### A1-02 — RECLASSIFICADO (média → baixa)

- **veredito:** reclassificado
- **como-validei:** `"Segundo [2] e [9]."` devolve `[2]` — o caso misto, que é o provável na prática,
  já funciona. Só a citação exclusivamente inválida (`"Segundo [9]."`, `"Segundo [0]."`) cai no
  fallback. Esse fallback está explicitamente documentado em `rag.py:359-365` como escolha de projeto
  ("se o modelo não citou nenhum, cai para os recuperados, para nunca ficar sem fontes").
- **severidade-final:** baixa
- **acao:** aceitar-como-conhecido, com devolução para o auditor estreitar o escopo do achado — ver
  [`devolucoes/A1-02.md`](devolucoes/A1-02.md).

### A1-03 — CONFIRMADO

- **veredito:** confirmado
- **como-validei:** escrevi um CSV temporário com `ano=vinte e vinte` e chamei `rag.carregar_metadados`
  nele: `ValueError: invalid literal for int() with base 10: 'vinte e vinte'`, cru, antes de
  `validar_metadados` rodar. Confirma a inversão de ordem descrita no achado.
- **severidade-final:** média (auditor: média)
- **acao:** ticket — validar antes de converter, ou converter dentro de `validar_metadados` com
  mensagem própria. Cuidado: `carregar_metadados` é usada por todo o pipeline, então a correção não
  pode passar a devolver `ano` como string.

### A1-04 — CONFIRMADO

- **veredito:** confirmado
- **como-validei:** com uma página de teste diferente (terminando em `Keywords:` em vez de
  `1 Introduction`), o texto normalizado devolveu `'Texto do abstract aqui. Keywords: rag, retrieval
  Resto.'` — engoliu não só a seção seguinte como o resto da página. O defeito é mais amplo do que o
  auditor mostrou: vale para qualquer marcador de fim, não só "Introduction".
- **severidade-final:** média (auditor: média)
- **acao:** ticket — fazer o lookahead tolerar espaço em branco genérico em vez de exigir `\n`.

### A1-05 — CONFIRMADO

- **veredito:** confirmado
- **como-validei:** confirmei por leitura do corpo de `gerar_chunks` que não há nenhum `print` ali, e
  que o aviso "preencha o resumo à mão" existe apenas em `scripts/01_preparar_corpus.py`. Ou seja: quem
  indexar sem passar pelo script 01 não recebe aviso nenhum.
- **severidade-final:** média (auditor: média)
- **acao:** ticket — `indexar()`/`gerar_chunks()` devem reportar quantos artigos ficaram sem chunk de
  resumo, e `verificar.py e2` deve reprovar se a contagem de resumos for menor que a de artigos.

### A1-06 — CONFIRMADO

- **veredito:** confirmado
- **como-validei:** rodei `verificar.py e4_limiar` de novo, em execução separada: mesma menor distância
  fora da base (0,6566) e mesmo limiar (0,60). A leitura do código de `_escolher_limiar_estagio_1`
  confirma que só a sobreposição reprova; não há margem mínima.
- **severidade-final:** média (auditor: média)
- **acao:** ticket — exigir margem mínima explícita em `e4_limiar` e falhar abaixo dela.

### A1-07 — REJEITADO

- **veredito:** rejeitado
- **como-validei:** repeti a medição com quatro textos de tamanhos diferentes e uma chave de busca de
  30 caracteres: `min=149 max=149 zeros=0`, nenhuma parte terminando no meio de uma palavra. O
  intervalo "142–149" do achado é artefato da medição do auditor (chave de 40 caracteres, que casa uma
  ocorrência anterior do mesmo trecho), não do código. O fato real é constante e trivial: 149 em vez de
  150, porque `rag.py:144` avança um caractere para depois do espaço, justamente para não cortar
  palavra.
- **severidade-final:** não se aplica
- **acao:** descartar — ver [`devolucoes/A1-07.md`](devolucoes/A1-07.md).

---

## Lacunas

### LACUNA A1 — `_erro_ollama` trata qualquer erro de resposta como servidor fora do ar

- **onde:** `rag.py:33-43`
- **por-que-era-do-escopo-A1:** o eixo A1 é dono de `rag.py` e o achado 6.7 (mensagem de erro clara) é
  o critério mais citado do arquivo. O auditor examinou `cli_seguro` e os casos de conexão, mas não
  exercitou o outro ramo do mesmo `except`.
- **o-que-investigar:** `_ERROS_CONEXAO` inclui `ollama.ResponseError`. Testei
  `_erro_ollama(ollama.ResponseError("internal server error", 500), "qwen2.5:1.5b")` e a mensagem
  devolvida é "Não consegui falar com o Ollama … Abra o aplicativo Ollama (ou rode `ollama serve`)" —
  instrução errada quando o servidor está de pé e devolveu 500 (falta de RAM, modelo corrompido).
  Avaliar se o caso merece mensagem própria, medir a severidade para a aula (a máquina tem 7,9 GB e
  erro por memória é plausível) e registrar o achado no formato padrão.

### Sem lacuna — determinismo verificado e correto

Aproveitei para cobrir um item da seção "Não verificado" do auditor: `_opcoes()` usa `seed=42` e
`temperature=0.1`, e duas chamadas idênticas ao `qwen2.5:1.5b` devolveram exatamente o mesmo texto.
Não vira achado; fica registrado para o eixo A3 não repetir o trabalho.

---

## Placar — eixo A1

| Métrica | Valor |
|---|---:|
| Achados propostos | 8 |
| Confirmados | 6 |
| Reclassificados | 1 |
| Rejeitados | 1 |
| Duplicados | 0 |
| Lacunas abertas pelo CTO | 1 |

**Leitura:** taxa de confirmação de 75%, com uma rejeição por erro de medição (A1-07) e uma
reclassificação por ignorar decisão já documentada no próprio código (A1-02). Os dois erros são do
mesmo tipo: afirmar sem conferir o que o comentário adjacente já explicava, ou sem repetir a medição
com outra entrada. Para os eixos A2–A6, o prompt do auditor deve exigir explicitamente: repetir toda
medição numérica com uma segunda entrada antes de reportar, e ler os comentários `why:`/`hazard:` da
região antes de classificar o comportamento como defeito.
