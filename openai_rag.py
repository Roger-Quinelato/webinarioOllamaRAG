"""Fachada RAG grounded para uma única Base Ativa usando OpenAI."""

import re
from dataclasses import dataclass

import config
from openai_provider import ErroProviderOpenAI


MAX_CHUNKS_RETRIEVAL = 5
MAX_CHUNKS_PROMPT = 3
_CITACAO_RE = re.compile(r"\[(\d+)\]")
_MENSAGEM_RECUSA = config.RESPOSTA_NAO_ENCONTRADA


@dataclass(frozen=True)
class BaseAtiva:
    """A única coleção que uma pergunta pode consultar."""

    nome: str
    colecao: object


class OpenAIRAG:
    """Coordena retrieval, grounding, fontes e geração para uma Base Ativa."""

    def __init__(self, provider):
        self.provider = provider

    def buscar(self, pergunta, base_ativa, *, k=MAX_CHUNKS_RETRIEVAL, where=None):
        if not isinstance(base_ativa, BaseAtiva):
            raise TypeError("A pergunta precisa receber exatamente uma Base Ativa.")
        k = min(max(k, 1), MAX_CHUNKS_RETRIEVAL)
        vetor = self.provider.gerar_embeddings([pergunta])[0]
        opcoes = {
            "query_embeddings": [vetor],
            "n_results": k,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            opcoes["where"] = where
        resposta = base_ativa.colecao.query(**opcoes)
        documentos = resposta.get("documents", [[]])[0]
        metadados = resposta.get("metadatas", [[]])[0]
        distancias = resposta.get("distances", [[]])[0]
        return [
            {
                "posicao": posicao,
                "texto": texto,
                "distancia": distancia,
                **metadado,
            }
            for posicao, (texto, metadado, distancia) in enumerate(
                zip(documentos, metadados, distancias), start=1
            )
        ]

    def responder(self, pergunta, base_ativa, *, historico=None, k=MAX_CHUNKS_RETRIEVAL, where=None):
        chunks = self.buscar(pergunta, base_ativa, k=k, where=where)
        if not chunks:
            return {
                "texto": _MENSAGEM_RECUSA,
                "status": "Recusa",
                "classe_fontes": "sem_resultados",
                "fontes_citadas": [],
                "chunks_recuperados": [],
                "base_ativa": base_ativa.nome,
            }
        mensagens = _montar_mensagens(pergunta, chunks, historico or [])
        texto = ""
        tentativa = 0
        while True:
            try:
                for pedaco in self.provider.transmitir(mensagens):
                    texto += pedaco
                break
            except Exception as erro:
                if not texto and tentativa == 0:
                    tentativa += 1
                    continue
                if texto:
                    texto += "\n\nResposta Parcial: a geração foi interrompida antes da conclusão."
                    return self._resultado(texto, chunks, base_ativa, status="Resposta Parcial")
                if isinstance(erro, ErroProviderOpenAI):
                    raise
                raise ErroProviderOpenAI("A geração falhou antes do primeiro token. Tente novamente.") from None
        return self._resultado(texto.strip(), chunks, base_ativa, status="completa")

    def transmitir(self, pergunta, base_ativa, *, historico=None, k=MAX_CHUNKS_RETRIEVAL, where=None):
        """Entrega os deltas ao chamador, preservando retry e resposta parcial."""
        chunks = self.buscar(pergunta, base_ativa, k=k, where=where)
        if not chunks:
            yield _MENSAGEM_RECUSA
            return
        mensagens = _montar_mensagens(pergunta, chunks, historico or [])
        texto = ""
        tentativa = 0
        while True:
            try:
                for pedaco in self.provider.transmitir(mensagens):
                    texto += pedaco
                    yield pedaco
                return
            except Exception as erro:
                if not texto and tentativa == 0:
                    tentativa += 1
                    continue
                if texto:
                    yield "\n\nResposta Parcial: a geração foi interrompida antes da conclusão."
                    return
                if isinstance(erro, ErroProviderOpenAI):
                    raise
                raise ErroProviderOpenAI("A geração falhou antes do primeiro token. Tente novamente.") from None

    @staticmethod
    def _resultado(texto, chunks, base_ativa, *, status):
        citadas = _fontes_citadas(texto, chunks)
        if _eh_recusa(texto):
            classe = "recusa"
            citadas = []
        elif citadas:
            classe = "citadas"
        else:
            classe = "fallback"
        return {
            "texto": texto,
            "status": status,
            "classe_fontes": classe,
            "fontes_citadas": citadas,
            "chunks_recuperados": chunks,
            "base_ativa": base_ativa.nome,
        }


def _montar_mensagens(pergunta, chunks, historico):
    contexto = "\n\n".join(
        f"[{indice}] ({chunk.get('arquivo', 'arquivo desconhecido')}, p. {chunk.get('pagina', '?')}, "
        f"{chunk.get('ano', '?')})\n{chunk['texto']}"
        for indice, chunk in enumerate(chunks[:MAX_CHUNKS_PROMPT], start=1)
    )
    mensagens = [
        {
            "role": "system",
            "content": (
                "Responda em português usando SOMENTE os trechos fornecidos. "
                f"Se a resposta não estiver nos trechos, responda exatamente: {_MENSAGEM_RECUSA} "
                "Cite cada afirmação sustentada usando o número do trecho entre colchetes, como [1]."
            ),
        }
    ]
    mensagens.extend(historico[-4:])
    mensagens.append({"role": "user", "content": f"Trechos:\n{contexto}\n\nPergunta: {pergunta}"})
    return mensagens


def _fontes_citadas(texto, chunks):
    indices = []
    for correspondencia in _CITACAO_RE.finditer(texto):
        indice = int(correspondencia.group(1))
        if 1 <= indice <= min(len(chunks), MAX_CHUNKS_PROMPT) and indice not in indices:
            indices.append(indice)
    return [chunks[indice - 1] for indice in indices]


def _eh_recusa(texto):
    return texto.strip().startswith(_MENSAGEM_RECUSA)
