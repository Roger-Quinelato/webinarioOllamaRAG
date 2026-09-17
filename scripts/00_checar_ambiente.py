import importlib
import importlib.metadata
import os
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import config  # noqa: E402

# Uso: python scripts/00_checar_ambiente.py [caminho/para/requirements.txt]
# O argumento existe para provar que esta checagem reprova quando um pacote declarado falta —
# aponta-se para uma cópia do requirements.txt com um nome a mais, sem desinstalar nada do
# ambiente real. Sem argumento, é sempre o requirements.txt do projeto.
ARQUIVO_REQUISITOS = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "requirements.txt"

falhas = []


def checar(nome, ok, detalhe=""):
    # why: devolve `ok` para o chamador ramificar sem consultar `falhas` — a versão anterior
    # testava `if "ollama" not in falhas`, mas `falhas` guarda o rótulo ("import ollama"), então a
    # condição era sempre verdadeira e o bloco do servidor rodava com o import quebrado.
    print(f"[{'OK ' if ok else 'FALHOU'}] {nome}{' — ' + detalhe if detalhe else ''}")
    if not ok:
        falhas.append(nome)
    return ok


# hazard (achado A6-02, T33): a lista de pacotes era fixa no código e cobria 6 dos 10 nomes de
# requirements.txt — faltavam matplotlib (shap.plots.text, scripts/05) e ipykernel (kernel do
# notebook), então o script dizia "Ambiente pronto." num ambiente em que o bloco de SHAP quebra
# depois de ~40 s de cálculo, ao vivo. Agora a lista vem do próprio arquivo que o projeto declara:
# dependência nova aparece aqui sem ninguém lembrar de editar duas listas.
_REQUISITO_RE = re.compile(r"^(?P<nome>[A-Za-z0-9._-]+)\s*(?:\[[^\]]*\])?\s*(?:[=<>!~].*)?$")


def pacotes_declarados(arquivo):
    # hazard: descartar em silêncio a linha que o regex não entende (`-r outro.txt`, `-e .`,
    # `pacote @ https://…`) reproduziria o próprio defeito que este ticket corrige — o script
    # diria "Ambiente pronto." sem ter checado tudo. Por isso o que não é reconhecido volta
    # separado, para virar uma falha visível, em vez de sumir.
    nomes, condicionais, nao_reconhecidas = [], [], []
    for numero, bruta in enumerate(arquivo.read_text(encoding="utf-8").splitlines(), start=1):
        linha = bruta.split("#")[0].strip()
        if not linha:
            continue
        # Marcador de ambiente (`tomli==2.0.1; python_version<"3.11"`): o pacote pode legitimamente
        # não estar instalado neste Python, então checá-lo daria falso negativo. Fica registrado
        # como não checado — visível, não silencioso.
        if ";" in linha:
            condicionais.append(f"linha {numero}: {linha}")
            continue
        achado = _REQUISITO_RE.match(linha)
        if achado:
            nomes.append(achado.group("nome"))
        else:
            nao_reconhecidas.append(f"linha {numero}: {linha}")
    return nomes, condicionais, nao_reconhecidas


def _normalizar_nome_pacote(nome):
    # why: nome próprio, e não `_normalizar`, para não colidir com rag._normalizar(), que normaliza
    # espaços em texto de metadados — outra regra, outro propósito (a checagem e7_duplicadas pegou
    # a homonímia).
    return re.sub(r"[-_.]+", "-", nome).lower()


def _mapa_distribuicao_para_modulo():
    # why: packages_distributions() varre o site-packages inteiro; chamá-la uma vez por pacote
    # multiplicava esse custo por 10 num script que é a primeira coisa que o participante roda.
    mapa = {}
    for modulo, distribuicoes in importlib.metadata.packages_distributions().items():
        for distribuicao in distribuicoes:
            mapa.setdefault(_normalizar_nome_pacote(distribuicao), []).append(modulo)
    return mapa


def modulo_da_distribuicao(distribuicao, mapa):
    # why: o nome da distribuição nem sempre é o do módulo importável (`pillow` → `PIL`). O mapa
    # reverso resolve isso a partir do que está instalado; quando a distribuição não está instalada
    # ela não aparece no mapa, e aí o palpite normalizado falha no import — que é exatamente o
    # resultado desejado.
    # hazard: uma distribuição declara vários nomes de topo, e alguns são lixo — `matplotlib` e
    # `ipykernel` declaram `__pycache__`, `chromadb` declara `schemas`. Pegar "o primeiro" fazia o
    # script importar `__pycache__`, que existe como namespace package e importa sem erro: a
    # checagem passava sem tocar no pacote que devia checar. Por isso a preferência é o nome que
    # bate com o da distribuição, e nomes com sublinhado à frente ficam por último.
    normalizado = _normalizar_nome_pacote(distribuicao)
    candidatos = mapa.get(normalizado, [])
    for candidato in candidatos:
        if _normalizar_nome_pacote(candidato) == normalizado:
            return candidato
    publicos = [c for c in candidatos if not c.startswith("_")]
    return (publicos or candidatos or [distribuicao.replace("-", "_")])[0]


def variavel_ollama_models():
    valor = os.environ.get("OLLAMA_MODELS")
    if valor or sys.platform != "win32":
        return valor
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as chave:
            return winreg.QueryValueEx(chave, "OLLAMA_MODELS")[0]
    except OSError:
        return None


print(f"Python {sys.version.split()[0]} em {sys.prefix}")
checar("Python 3.10+", sys.version_info >= (3, 10), sys.version.split()[0])
checar("Rodando dentro de um ambiente virtual", sys.prefix != sys.base_prefix, sys.prefix)

if checar(f"{ARQUIVO_REQUISITOS.name} existe", ARQUIVO_REQUISITOS.is_file(), str(ARQUIVO_REQUISITOS)):
    pacotes, condicionais, nao_reconhecidas = pacotes_declarados(ARQUIVO_REQUISITOS)
else:
    pacotes, condicionais, nao_reconhecidas = [], [], []
print(f"{len(pacotes)} pacotes declarados em {ARQUIVO_REQUISITOS.name}: {', '.join(pacotes)}")
checar(f"{ARQUIVO_REQUISITOS.name} declara pelo menos uma dependência", bool(pacotes),
       str(ARQUIVO_REQUISITOS))
checar("Todas as linhas de requisito foram reconhecidas", not nao_reconhecidas,
       "não reconhecidas: " + "; ".join(nao_reconhecidas) if nao_reconhecidas else "")
for condicional in condicionais:
    print(f"[INFO] requisito com marcador de ambiente, não checado — {condicional}")
imports_quebrados = set()
mapa_modulos = _mapa_distribuicao_para_modulo()
for pacote in pacotes:
    modulo_esperado = modulo_da_distribuicao(pacote, mapa_modulos)
    rotulo = f"import {pacote}" + (f" (módulo {modulo_esperado})" if modulo_esperado != pacote else "")
    try:
        modulo = importlib.import_module(modulo_esperado)
        checar(rotulo, True, getattr(modulo, "__version__", "sem __version__"))
        # hazard: um diretório sem arquivos importa como namespace package, com `__file__ = None` —
        # foi assim que `import __pycache__` deu OK na 1ª versão desta checagem. A escolha do módulo
        # já evita cair nesses nomes; isto é o aviso de última linha. Não reprova porque existe
        # namespace package legítimo (`google`, de protobuf; `opentelemetry`), e reprovar um deles
        # mandaria reinstalar um pacote sadio. A detecção de verdade do modo de falha do A1-00
        # (RECORD apontando para arquivos que sumiram) é o ticket #44.
        if getattr(modulo, "__file__", None) is None:
            print(f"[AVISO] {modulo_esperado} importou como namespace package (sem arquivo próprio). "
                  f"Se {pacote} não funcionar, reinstale com "
                  f"`pip install --force-reinstall --no-deps -r requirements.lock`.")
    except Exception as erro:
        checar(rotulo, False, str(erro))
        imports_quebrados.add(pacote)

if "ollama" not in imports_quebrados:
    import httpx

    try:
        versao = httpx.get(f"{config.OLLAMA_HOST}/api/version", timeout=5).json()["version"]
        checar("Servidor Ollama respondendo", True, f"{config.OLLAMA_HOST} (versão {versao})")
        import rag

        instalados, faltando = rag.verificar_ollama(
            [config.MODELO_EMBEDDING, config.MODELO_CHAT, config.MODELO_CHAT_PLANO_B]
        )
        checar("Modelos baixados", not faltando,
               "faltando: " + ", ".join(faltando) if faltando else ", ".join(sorted(instalados)))
    except Exception as erro:
        checar("Servidor Ollama respondendo", False,
               f"{erro}. Abra o aplicativo Ollama ou rode `ollama serve`.")

pasta_modelos = variavel_ollama_models()
print(f"[INFO] OLLAMA_MODELS = {pasta_modelos or 'não definida (o Ollama usa a pasta padrão ~/.ollama/models)'}")

print()
if falhas:
    print(f"{len(falhas)} verificação(ões) falharam: {', '.join(falhas)}")
    sys.exit(1)
print("Ambiente pronto.")
