import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parents[1]
PORTA = 8502


def subir_app(porta=PORTA, timeout=90):
    """Descreve subir app."""
    processo = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", str(RAIZ / "app.py"),
         "--server.port", str(porta), "--server.headless", "true"],
        cwd=RAIZ, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    url = f"http://localhost:{porta}"
    inicio = time.perf_counter()
    while time.perf_counter() - inicio < timeout:
        try:
            if urllib.request.urlopen(url, timeout=2).status == 200:
                return processo, url
        except OSError:
            pass
        time.sleep(1)
    processo.terminate()
    raise RuntimeError(f"streamlit não respondeu HTTP 200 em {url} após {timeout}s")


# why: channel="msedge" usa o Edge já instalado na máquina de demo em vez de baixar o
# Chromium do Playwright (~150 MB) — a máquina tem pouco espaço/RAM (ver CLAUDE.md).
# why: `interagir` existe para T15 (capturas reais 8.2/8.4/8.5/8.6/8.7/8.8), que precisa
# mexer em sliders/filtros/chat antes do PNG — sem isso, capturar_app.py só serviria para
# a tela inicial e T15 duplicaria subir_app()/o boilerplate do Playwright.
def capturar(caminho_png, porta=PORTA, timeout_ms=60000, interagir=None):
    """Descreve capturar."""
    processo, url = subir_app(porta)
    try:
        with sync_playwright() as p:
            navegador = p.chromium.launch(channel="msedge")
            pagina = navegador.new_page(viewport={"width": 1440, "height": 900})
            pagina.goto(url)
            # why: o título só aparece depois que a coleção do Chroma é aberta e o app
            # termina de renderizar — um wait_for_timeout fixo capturava a página em
            # branco (achado do /code-review deste ticket, #13).
            pagina.wait_for_selector("text=Assistente RAG", timeout=timeout_ms)
            if interagir:
                interagir(pagina)
            pagina.screenshot(path=str(caminho_png), full_page=True)
            navegador.close()
    finally:
        processo.terminate()
        processo.wait(timeout=10)
    return Path(caminho_png)


if __name__ == "__main__":
    destino = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "docs" / "evidencias" / "captura_app.png"
    destino.parent.mkdir(parents=True, exist_ok=True)
    caminho = capturar(destino)
    print(f"Screenshot salvo em {caminho.relative_to(RAIZ)}")
