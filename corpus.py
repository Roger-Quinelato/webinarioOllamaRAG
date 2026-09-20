"""Leitura e preparação do Corpus Oficial, sem dependência de Ollama."""

import csv
import re
from pathlib import Path

from pypdf import PdfReader

import config

_LIGADURAS = {"ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl"}


def carregar_metadados(caminho=None):
    """Carrega metadados."""
    with open(caminho or config.ARQUIVO_METADADOS, encoding="utf-8", newline="") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    for linha in linhas:
        linha["ano"] = int(linha["ano"])
    return linhas


def limpar_texto(texto):
    """Limpa texto."""
    for ligadura, letras in _LIGADURAS.items():
        texto = texto.replace(ligadura, letras)
    texto = re.sub(r"(\w)-\n(\w)", r"\1\2", texto)
    return re.sub(r"\s+", " ", texto).strip()


def extrair_paginas(caminho, limpar=True):
    """Extrai paginas."""
    paginas = [pagina.extract_text() or "" for pagina in PdfReader(str(caminho)).pages]
    return [limpar_texto(pagina) for pagina in paginas] if limpar else paginas


def dividir_texto(texto, tamanho=None, sobreposicao=None):
    """Divide texto."""
    tamanho = tamanho or config.TAMANHO_CHUNK
    sobreposicao = config.SOBREPOSICAO if sobreposicao is None else sobreposicao
    if len(texto) <= tamanho:
        return [texto] if texto else []
    partes, inicio = [], 0
    while inicio < len(texto):
        fim = min(inicio + tamanho, len(texto))
        if fim < len(texto):
            corte = texto.rfind(" ", inicio + tamanho // 2, fim)
            fim = corte if corte != -1 else fim
        partes.append(texto[inicio:fim].strip())
        if fim >= len(texto):
            break
        inicio = max(fim - sobreposicao, inicio + 1)
    return partes


def gerar_chunks(metadados=None, pasta=None):
    """Gera chunks."""
    pasta = Path(pasta or config.PASTA_ARTIGOS)
    chunks = []
    for meta in metadados or carregar_metadados():
        base = {campo: meta[campo] for campo in config.COLUNAS_METADADOS}
        stem = Path(meta["arquivo"]).stem
        for pagina, texto_pagina in enumerate(extrair_paginas(pasta / meta["arquivo"]), start=1):
            for parte, texto in enumerate(dividir_texto(texto_pagina)):
                chunk_id = f"{stem}-p{pagina:03d}-c{parte:02d}"
                chunks.append({"id": chunk_id, "texto": texto,
                               "metadados": {**base, "pagina": pagina, "chunk_id": chunk_id,
                                              "tipo_chunk": "pagina"}})
        if meta["resumo"]:
            chunk_id = f"{stem}-resumo"
            chunks.append({"id": chunk_id, "texto": f"{meta['titulo']}. {meta['resumo']}",
                           "metadados": {**base, "pagina": 0, "chunk_id": chunk_id,
                                          "tipo_chunk": "resumo"}})
    return chunks
