"""Sonda do eixo A6 — reprodutibilidade e ambiente (RODADA-1, só leitura).

Roda com: .venv/Scripts/python.exe docs/auditoria/rodadas/RODADA-1/A6-sonda.py
Não instala, não desinstala, não escreve nada fora do stdout.

Blocos:
  A6/imports   — imports de terceiros usados no código × requirements.txt/-dev.txt/.lock
  A6/venv      — integridade da .venv: dist-info cujo código sumiu (o modo de falha do A1-00)
  A6/scripts00 — o que scripts/00_checar_ambiente.py de fato checa × critérios 0.1-0.8
"""

import ast
import json
import os
import pathlib
import sys
from importlib import metadata

RAIZ = pathlib.Path(__file__).resolve().parents[4]
PULAR = {".venv", ".claude", "chroma_db", "Ollama", "__pycache__", ".git", "node_modules"}
LOCAIS = {"rag", "config", "app"}
SEP = "=" * 78


def cabecalho(titulo):
    """Descreve cabecalho."""
    print()
    print(SEP)
    print(titulo)
    print(SEP)


# ---------------------------------------------------------------- A6/imports
def ler_requisitos(caminho):
    """Lê requisitos."""
    pacotes = {}
    for linha in (RAIZ / caminho).read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or linha.startswith("-r"):
            continue
        nome, _, versao = linha.partition("==")
        pacotes[nome.strip().lower().replace("_", "-")] = versao.strip()
    return pacotes


def imports_do_codigo():
    """Descreve imports do codigo."""
    achados = {}
    stdlib = set(sys.stdlib_module_names)

    def registra(modulo, origem):
        """Registra valor do fluxo."""
        topo = modulo.split(".")[0]
        if topo in stdlib or topo in LOCAIS:
            return
        achados.setdefault(topo, set()).add(origem)

    def varrer(fonte, origem):
        """Varre valor do fluxo."""
        try:
            arvore = ast.parse(fonte)
        except SyntaxError as erro:
            print(f"  [erro de parse] {origem}: {erro}")
            return
        for no in ast.walk(arvore):
            if isinstance(no, ast.Import):
                for alias in no.names:
                    registra(alias.name, origem)
            elif isinstance(no, ast.ImportFrom) and no.level == 0 and no.module:
                registra(no.module, origem)

    for caminho in sorted(RAIZ.rglob("*.py")):
        if any(parte in PULAR for parte in caminho.parts):
            continue
        rel = caminho.relative_to(RAIZ).as_posix()
        varrer(caminho.read_text(encoding="utf-8"), rel)
    for caminho in sorted(RAIZ.rglob("*.ipynb")):
        if any(parte in PULAR for parte in caminho.parts):
            continue
        rel = caminho.relative_to(RAIZ).as_posix()
        nb = json.loads(caminho.read_text(encoding="utf-8"))
        for i, celula in enumerate(nb.get("cells", [])):
            if celula.get("cell_type") == "code":
                varrer("".join(celula["source"]), f"{rel}#celula{i}")
    return achados


def bloco_imports():
    """Descreve bloco imports."""
    cabecalho("A6/imports — imports de terceiros × requirements")
    txt = ler_requisitos("requirements.txt")
    dev = ler_requisitos("requirements-dev.txt")
    lock = ler_requisitos("requirements.lock")
    print(f"requirements.txt={len(txt)}  requirements-dev.txt(extras)={len(dev)}  requirements.lock={len(lock)}")

    print("\n-- declarado em requirements.txt/-dev.txt e ausente ou divergente no lock --")
    divergiu = False
    for nome, versao in {**txt, **dev}.items():
        if nome not in lock:
            print(f"  AUSENTE no lock: {nome}=={versao}")
            divergiu = True
        elif lock[nome] != versao:
            print(f"  DIVERGENTE: {nome} requirements={versao} lock={lock[nome]}")
            divergiu = True
    if not divergiu:
        print("  nenhum")

    mapa = metadata.packages_distributions()
    achados = imports_do_codigo()
    print("\n-- import de terceiros usado no código -> distribuição -> onde está declarado --")
    for topo in sorted(achados):
        dists = [d.lower().replace("_", "-") for d in mapa.get(topo, [])]
        if not dists:
            onde = "NAO INSTALADO / desconhecido"
        else:
            partes = []
            for d in dists:
                em = []
                if d in txt:
                    em.append("txt")
                if d in dev:
                    em.append("dev")
                if d in lock:
                    em.append("lock")
                partes.append(f"{d}[{'+'.join(em) if em else 'NAO DECLARADO'}]")
            onde = " ".join(partes)
        origens = sorted(achados[topo])
        print(f"  {topo:22s} -> {onde}")
        print(f"  {'':22s}    usado em: {', '.join(origens[:6])}{' …' if len(origens) > 6 else ''}")

    print("\n-- declarado em requirements.txt e nunca importado diretamente --")
    usados_dist = set()
    for topo in achados:
        for d in mapa.get(topo, []):
            usados_dist.add(d.lower().replace("_", "-"))
    for nome in txt:
        if nome not in usados_dist:
            print(f"  {nome}")


# ------------------------------------------------------------------ A6/venv
def bloco_venv():
    """Descreve bloco venv."""
    cabecalho("A6/venv — dist-info sem o código correspondente (modo de falha do A1-00)")
    sp = pathlib.Path(sys.prefix) / "Lib" / "site-packages"
    print(f"site-packages: {sp}")
    if not sp.is_dir():
        print("  site-packages não encontrado")
        return
    print("ATENÇÃO: Distribution.files do Python 3.12 aplica skip_missing_files() e descarta")
    print("silenciosamente o que sumiu do disco — usar essa API aqui daria falso negativo.")
    print("Esta sonda lê o RECORD como texto, sem passar por Distribution.files.\n")
    quebradas = []
    total = 0
    import csv as _csv
    for dinfo in sorted(sp.glob("*.dist-info")):
        registro = dinfo / "RECORD"
        if not registro.exists():
            print(f"  [sem RECORD] {dinfo.name}")
            continue
        total += 1
        linhas = registro.read_text(encoding="utf-8").splitlines()
        codigo = []
        for campos in _csv.reader(linhas):
            if not campos:
                continue
            caminho = campos[0].replace("\\", "/")
            if caminho.startswith(dinfo.name + "/") or "__pycache__/" in caminho:
                continue
            codigo.append(caminho)
        if not codigo:
            continue
        faltando = [c for c in codigo if not (sp / c).exists()]
        if faltando:
            quebradas.append((dinfo.name, len(faltando), len(codigo), faltando[:3]))
    print(f"dist-info com RECORD lidos: {total}")
    if not quebradas:
        print("nenhuma distribuição com arquivo de RECORD faltando — venv íntegra")
    else:
        print(f"distribuições com arquivo faltando: {len(quebradas)}")
        for nome, nfalta, ntot, amostra in sorted(quebradas, key=lambda x: -x[1])[:60]:
            print(f"  {nome:40s} {nfalta}/{ntot} arquivos ausentes  ex.: {amostra}")

    print("\n-- existe alguma checagem no repositório que detecte isso? --")
    alvos = ["scripts/00_checar_ambiente.py", "ferramentas/verificar.py"]
    padroes = ["dist-info", "RECORD", "pip check", "pip_check", "requirements.lock", "metadata.distributions", "importlib.metadata"]
    for alvo in alvos:
        texto = (RAIZ / alvo).read_text(encoding="utf-8")
        achou = [p for p in padroes if p in texto]
        print(f"  {alvo}: {achou if achou else 'nenhum padrão de integridade encontrado'}")
    tsh = (RAIZ / "docs" / "troubleshooting.md").read_text(encoding="utf-8")
    print("  docs/troubleshooting.md menciona 'dist-info': ", "dist-info" in tsh)
    print("  docs/troubleshooting.md menciona 'requirements.lock': ", "requirements.lock" in tsh)
    print("  docs/troubleshooting.md menciona 'force-reinstall': ", "force-reinstall" in tsh)


# -------------------------------------------------------------- A6/scripts00
def bloco_scripts00():
    """Descreve bloco scripts00."""
    cabecalho("A6/scripts00 — o que 00_checar_ambiente.py de fato checa")
    texto = (RAIZ / "scripts" / "00_checar_ambiente.py").read_text(encoding="utf-8")
    arvore = ast.parse(texto)
    chamadas = []
    for no in ast.walk(arvore):
        if isinstance(no, ast.Call) and isinstance(no.func, ast.Name) and no.func.id == "checar":
            arg = no.args[0]
            if isinstance(arg, ast.Constant):
                rotulo = repr(arg.value)
            elif isinstance(arg, ast.JoinedStr):
                rotulo = "f-string: " + "".join(
                    v.value if isinstance(v, ast.Constant) else "{...}" for v in arg.values
                )
            else:
                rotulo = ast.dump(arg)[:60]
            chamadas.append((no.lineno, rotulo))
    print(f"chamadas a checar() (as únicas que podem FALHAR o script): {len(chamadas)}")
    for linha, rotulo in chamadas:
        print(f"  linha {linha:3d}: {rotulo}")

    print("\npacotes que o script importa (lista literal):")
    for no in ast.walk(arvore):
        if isinstance(no, ast.Assign):
            for alvo in no.targets:
                if isinstance(alvo, ast.Name) and alvo.id == "pacotes":
                    print(f"  linha {no.lineno}: {[e.value for e in no.value.elts]}")

    txt = ler_requisitos("requirements.txt")
    importados = {"ollama", "chromadb", "streamlit", "pypdf", "shap", "numpy", "httpx"}
    print("\ndeclarados em requirements.txt e NÃO importados por scripts/00:")
    mapa = metadata.packages_distributions()
    dist_para_topo = {}
    for topo, dists in mapa.items():
        for d in dists:
            dist_para_topo.setdefault(d.lower().replace("_", "-"), set()).add(topo)
    for nome in txt:
        topos = dist_para_topo.get(nome, {nome})
        if not (topos & importados):
            print(f"  {nome}  (módulos: {sorted(topos)})")

    print("\npalavras-chave ausentes do script (critério 0.5 = pip check / versões fixadas):")
    for chave in ["pip", "requirements", "check", "kernelspec", "jupyter"]:
        print(f"  '{chave}' presente: {chave in texto}")

    print("\ncritério 0.2 (OLLAMA_MODELS aponta para D:\\webinarioOllamaRAG\\Ollama\\models):")
    print(f"  linha 62-63 usa print('[INFO] ...'), não checar(): "
          f"{'[INFO] OLLAMA_MODELS' in texto and 'checar(\"OLLAMA_MODELS' not in texto}")
    print(f"  valor atual na sessão: OLLAMA_MODELS={os.environ.get('OLLAMA_MODELS')!r}")


# ----------------------------------------------------------------- A6/venv2
def bloco_venv2():
    """Segunda medição da integridade da .venv, de forma diferente da primeira.

    A primeira (A6/venv) confere arquivo por arquivo do RECORD. Esta confere só os
    nomes importáveis de topo de cada distribuição — entrada de forma e tamanho
    diferentes, como pede a §4 do protocolo.
    """
    cabecalho("A6/venv2 — segunda medição: nomes de topo importáveis por distribuição")
    mapa = metadata.packages_distributions()
    por_dist = {}
    for topo, dists in mapa.items():
        for d in dists:
            por_dist.setdefault(d, set()).add(topo)
    sp = pathlib.Path(sys.prefix) / "Lib" / "site-packages"
    orfas = []
    conferidas = 0
    for dist, topos in sorted(por_dist.items()):
        reais = {t for t in topos if t != "__pycache__"}
        if not reais:
            continue
        conferidas += 1
        presentes = [t for t in reais if (sp / t).is_dir() or (sp / f"{t}.py").is_file()]
        if not presentes:
            orfas.append((dist, sorted(reais)))
    print(f"distribuições com nome de topo importável: {conferidas}")
    if orfas:
        print(f"ÓRFÃS (dist-info presente, nenhum nome de topo no disco): {len(orfas)}")
        for dist, topos in orfas:
            print(f"  {dist}: {topos}")
    else:
        print("nenhuma órfã — concorda com a primeira medição (venv íntegra)")

    print("\n-- prova de que o detector dispara: site-packages sintético só com dist-info --")
    import shutil
    import tempfile
    origem = next(sp.glob("ollama-*.dist-info"), None)
    if origem is None:
        print("  (não achei ollama-*.dist-info para a prova)")
        return
    with tempfile.TemporaryDirectory() as tmp:
        falso = pathlib.Path(tmp) / "site-packages"
        falso.mkdir()
        shutil.copytree(origem, falso / origem.name)  # só o dist-info, sem o pacote
        import csv as _csv
        ctx = metadata.MetadataPathFinder.find_distributions(
            metadata.DistributionFinder.Context(path=[str(falso)])
        )
        for dist in ctx:
            nome = dist.metadata["Name"]
            print(f"  metadata.version('{nome}') = {dist.version}  <- o pip/pip list o dá como instalado")
            print(f"  diretório '{nome}/' existe no disco? {(falso / nome).exists()}  <- import falharia")
            api = [f for f in (dist.files or []) if ".dist-info/" not in str(f).replace("\\", "/")]
            print(f"  Distribution.files (API do 3.12): {len(api)} arquivos de código "
                  f"-> detector via API dispara: {bool(api)}  (FALSO NEGATIVO)")
            dinfo = falso / origem.name
            linhas = (dinfo / "RECORD").read_text(encoding="utf-8").splitlines()
            codigo = [c[0].replace("\\", "/") for c in _csv.reader(linhas)
                      if c and not c[0].replace("\\", "/").startswith(dinfo.name + "/")
                      and "__pycache__/" not in c[0].replace("\\", "/")]
            faltando = [c for c in codigo if not (falso / c).exists()]
            print(f"  RECORD lido como texto: {len(codigo)} arquivos de código, {len(faltando)} ausentes "
                  f"-> detector via RECORD dispara: {bool(faltando)}")


# ----------------------------------------------------------- A6/scripts00-sim
def _rodar_00_sem(bloqueados, alvo="runpy.run_path(r'scripts/00_checar_ambiente.py', run_name='__main__')"):
    """Roda scripts/00 num subprocesso onde os pacotes de `bloqueados` não importam.

    Não desinstala nada: um finder em sys.meta_path levanta ImportError para esses nomes.
    """
    import subprocess
    codigo = (
        "import sys, runpy\n"
        f"BLOQ = {sorted(bloqueados)!r}\n"
        "class Bloqueia:\n"
        "    def find_spec(self, nome, caminho=None, alvo=None):\n"
        "        if nome.split('.')[0] in BLOQ:\n"
        "            raise ImportError('[sonda A6] ' + nome + ' indisponível')\n"
        "        return None\n"
        "sys.meta_path.insert(0, Bloqueia())\n"
        + alvo + "\n"
    )
    ambiente = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, "-c", codigo], cwd=RAIZ, capture_output=True,
                          text=True, encoding="utf-8", errors="replace", env=ambiente)


def bloco_scripts00_sim():
    """Descreve bloco scripts00 sim."""
    cabecalho("A6/scripts00-sim — scripts/00 aprova ambiente ao qual falta pacote do requirements?")
    for bloqueados in (["pandas"], ["matplotlib"], ["ipykernel"], ["httpx"]):
        proc = _rodar_00_sem(bloqueados)
        linhas = [ln for ln in proc.stdout.strip().splitlines()
                  if ln.startswith("[FALHOU]") or ln.startswith("Ambiente pronto")
                  or "falharam" in ln]
        print(f"\n-- bloqueando {bloqueados} --")
        for ln in linhas or ["(nenhuma falha; todas as checagens passaram)"]:
            print(f"   {ln}")
        print(f"   exit={proc.returncode}")
        # confirma que o bloqueio de fato impede o import
        conf = _rodar_00_sem(bloqueados, alvo=f"import {bloqueados[0]}")
        ultima = (conf.stderr.strip().splitlines() or ["(sem stderr)"])[-1]
        print(f"   [controle] import {bloqueados[0]} nesse mesmo subprocesso: {ultima} (exit={conf.returncode})")


if __name__ == "__main__":
    print(f"A6-sonda — raiz: {RAIZ}")
    print(f"python: {sys.executable}")
    bloco_imports()
    bloco_venv()
    bloco_venv2()
    bloco_scripts00()
    bloco_scripts00_sim()
