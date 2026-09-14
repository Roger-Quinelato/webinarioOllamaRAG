import importlib
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import config  # noqa: E402

falhas = []


def checar(nome, ok, detalhe=""):
    print(f"[{'OK ' if ok else 'FALHOU'}] {nome}{' — ' + detalhe if detalhe else ''}")
    if not ok:
        falhas.append(nome)


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

pacotes = ["ollama", "chromadb", "streamlit", "pypdf", "shap", "numpy"]
for pacote in pacotes:
    try:
        modulo = importlib.import_module(pacote)
        checar(f"import {pacote}", True, getattr(modulo, "__version__", "sem __version__"))
    except Exception as erro:
        checar(f"import {pacote}", False, str(erro))

if "ollama" not in falhas:
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
