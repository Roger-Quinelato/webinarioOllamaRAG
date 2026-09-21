"""Provas reexecutáveis dos caminhos de reprovação adicionados no T38 (#45)."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import verificar


class _ColecaoVazia:
    """Representa Colecao Vazia."""
    def count(self):
        """Descreve count."""
        return 0

    def get(self, **_):
        """Descreve get."""
        return {"metadatas": []}


def _deve_reprovar(nome, chamada):
    """Auxilia deve reprovar."""
    try:
        chamada()
    except SystemExit as erro:
        if erro.code == 1:
            print(f"{nome}: REPROVOU como esperado")
            return
    raise AssertionError(f"{nome}: não reprovou com exit 1")


def main():
    """Descreve main."""
    _deve_reprovar(
        "e1_resumos sem metadados",
        lambda: _com_patch("rag.carregar_metadados", lambda: [], verificar.e1_resumos),
    )
    _deve_reprovar(
        "e2 coleção vazia",
        lambda: _com_patch("rag.abrir_colecao", lambda: _ColecaoVazia(), verificar.e2),
    )
    _deve_reprovar(
        "e2_sobreposicao sem pares",
        lambda: _com_patches(
            {"rag.extrair_paginas": lambda _: ["", "", "texto"],
             "rag.dividir_texto": lambda _: ["texto"]},
            verificar.e2_sobreposicao,
        ),
    )
    _deve_reprovar(
        "e2_reabrir coleção vazia",
        lambda: _com_patch("rag.abrir_colecao", lambda: _ColecaoVazia(), verificar.e2_reabrir),
    )
    _deve_reprovar(
        "e3 coleção vazia",
        lambda: _com_patch("rag.abrir_colecao", lambda: _ColecaoVazia(), verificar.e3),
    )
    _deve_reprovar(
        "e6_ollama_desligado quando chamadas não falham",
        lambda: _com_patches(
            {"rag.gerar_embeddings": lambda _: [], "rag.responder": lambda *_: []},
            verificar.e6_ollama_desligado,
        ),
    )
    with tempfile.TemporaryDirectory() as diretorio:
        raiz = Path(diretorio)
        (raiz / "webinario_rag.ipynb").write_text(
            json.dumps({"cells": []}), encoding="utf-8"
        )
        _deve_reprovar(
            "e7_estrutura sem blocos",
            lambda: _com_patch("verificar.RAIZ", raiz, verificar.e7_estrutura),
        )


def _com_patch(alvo, valor, chamada):
    """Auxilia com patch."""
    with patch(alvo, valor):
        chamada()


def _com_patches(valores, chamada):
    """Auxilia com patches."""
    with patch.multiple(verificar.rag, **{
        alvo.removeprefix("rag."): valor for alvo, valor in valores.items()
    }):
        chamada()


if __name__ == "__main__":
    main()
