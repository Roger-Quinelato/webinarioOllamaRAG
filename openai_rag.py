"""Fachada RAG grounded para uma única Base Ativa usando OpenAI."""

import logging
import re
from dataclasses import dataclass

import config
from generation_router import ErroProviderGeracao, GenerationRouter

LOGGER = logging.getLogger("rag.geracao")
MAX_CHUNKS_RETRIEVAL = 5
MAX_CHUNKS_PROMPT = 3
_CITACAO_RE = re.compile(r"\[(\d+)\]")
_MENSAGEM_RECUSA = config.RESPOSTA_NAO_ENCONTRADA
_AVISO_PARCIAL = "\n\nResposta Parcial: a geração foi interrompida antes da conclusão."


@dataclass(frozen=True)
class BaseAtiva:
    """A única coleção que uma pergunta pode consultar."""

    nome: str
    colecao: object
    tipo: str = "Corpus Oficial"
    provedor_embedding: str = "Ollama"
    modelo_embedding: str = config.MODELO_EMBEDDING
    dimensao_embedding: int = config.DIMENSAO_EMBEDDING
    versao_colecao: str = config.VERSAO_COLECAO_EMBEDDING
    sessao_id: str | None = None


class FluxoResposta:
    """Fluxo de deltas que conserva o ResultadoRAG após o consumo."""

    def __init__(self, rag, pergunta, base_ativa, historico, k, where):
        """Inicializa instância com dependências e parâmetros."""
        self._rag, self._args = rag, (pergunta, base_ativa)
        self._kwargs = {"historico": historico, "k": k, "where": where}
        self.resultado = None

    def __iter__(self):
        """Itera sobre deltas e metadados do fluxo."""
        chunks = self._rag.buscar(*self._args, k=self._kwargs["k"], where=self._kwargs["where"])
        if not chunks:
            self.resultado = {"texto": _MENSAGEM_RECUSA, "status": "Recusa",
                              "classe_fontes": "sem_resultados", "fontes_citadas": [],
                              "chunks_recuperados": [], "base_ativa": self._args[1].nome,
                              "generation_provider": None, "generation_model": None,
                              "fallback_used": False, "attempted_providers": []}
            LOGGER.info(
                "resposta base_ativa=%s chunks=0 status=Recusa recusa=True parcial=False",
                self._args[1].nome,
            )
            yield _MENSAGEM_RECUSA
            return
        mensagens = _montar_mensagens(self._args[0], chunks, self._kwargs["historico"] or [])
        provider = self._rag.generation_provider
        texto, tentativa = "", 0
        while True:
            execucao = provider.transmitir(mensagens)
            try:
                for pedaco in execucao:
                    texto += pedaco
                    yield pedaco
                self.resultado = self._rag._resultado(
                    texto.strip(), chunks, self._args[1], status="completa",
                    geracao=getattr(execucao, "telemetria", None),
                )
                _registrar(self.resultado, execucao, tentativa)
                return
            except Exception as erro:
                if not texto and tentativa == 0 and not isinstance(provider, GenerationRouter):
                    tentativa += 1
                    continue
                if texto:
                    texto += _AVISO_PARCIAL
                    self.resultado = self._rag._resultado(
                        texto, chunks, self._args[1], status="Resposta Parcial",
                        geracao=getattr(execucao, "telemetria", None),
                    )
                    _registrar(self.resultado, execucao, tentativa)
                    yield _AVISO_PARCIAL
                    return
                if isinstance(erro, ErroProviderGeracao):
                    raise
                raise ErroProviderGeracao("A geração falhou antes do primeiro token.") from None


class OpenAIRAG:
    """Coordena retrieval, grounding, fontes e geração para uma Base Ativa."""

    def __init__(self, embedding_provider, generation_provider):
        """Inicializa instância com dependências e parâmetros."""
        self.embedding_provider = embedding_provider
        self.generation_provider = generation_provider

    def buscar(self, pergunta, base_ativa, *, k=MAX_CHUNKS_RETRIEVAL, where=None):
        """Busca valor do fluxo."""
        if not isinstance(base_ativa, BaseAtiva):
            raise TypeError("A pergunta precisa receber exatamente uma Base Ativa.")
        metadados = getattr(base_ativa.colecao, "metadata", None) or {}
        esperados = {
            "provedor_embedding": base_ativa.provedor_embedding,
            "modelo_embedding": base_ativa.modelo_embedding,
            "dimensao_embedding": base_ativa.dimensao_embedding,
            "versao_colecao": base_ativa.versao_colecao,
            "status": "ready",
        }
        incompatibilidades = [
            campo for campo, esperado in esperados.items() if metadados.get(campo) != esperado
        ]
        if incompatibilidades:
            raise ValueError(
                "A Base Ativa é incompatível ("
                + ", ".join(incompatibilidades)
                + "). Execute a reindexação explícita antes de consultar."
            )
        k = min(max(k, 1), MAX_CHUNKS_RETRIEVAL)
        vetores = self.embedding_provider.gerar_embeddings([pergunta])
        if len(vetores) != 1:
            raise ValueError(
                "O Provider Ollama precisa devolver exatamente um embedding para a pergunta. "
                f"Confira a configuração do {base_ativa.modelo_embedding} antes de consultar."
            )
        vetor = vetores[0]
        if (
            len(vetor) != base_ativa.dimensao_embedding
            or len(vetor) != metadados["dimensao_embedding"]
        ):
            raise ValueError(
                "O embedding da pergunta tem dimensão incompatível com a Base Ativa. "
                f"Confira a configuração do {base_ativa.modelo_embedding} "
                "e execute a reindexação explícita antes de consultar."
            )
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
            if distancia <= config.DISTANCIA_MAXIMA_RETRIEVAL
        ]

    def responder(self, pergunta, base_ativa, *, historico=None, k=MAX_CHUNKS_RETRIEVAL, where=None):
        """Responde valor do fluxo."""
        fluxo = self.transmitir(pergunta, base_ativa, historico=historico, k=k, where=where)
        for _ in fluxo:
            pass
        return fluxo.resultado

    def transmitir(self, pergunta, base_ativa, *, historico=None, k=MAX_CHUNKS_RETRIEVAL, where=None):
        """Transmite valor do fluxo."""
        return FluxoResposta(self, pergunta, base_ativa, historico, k, where)

    @staticmethod
    def _resultado(texto, chunks, base_ativa, *, status, geracao=None):
        """Auxilia resultado."""
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
            "generation_provider": (geracao or {}).get("generation_provider"),
            "generation_model": (geracao or {}).get("generation_model"),
            "fallback_used": (geracao or {}).get("fallback_used", False),
            "attempted_providers": (geracao or {}).get("attempted_providers", []),
        }


def _registrar(resultado, execucao, tentativa):
    """Registra o mínimo do TDD; nunca inclui chave, prompt nem texto de chunk ou de resposta."""
    telemetria = getattr(execucao, "telemetria", None) or {}
    LOGGER.info(
        "resposta base_ativa=%s provider=%s modelo=%s chunks=%s tentativa=%s status=%s "
        "recusa=%s parcial=%s ttft=%s",
        resultado["base_ativa"],
        resultado["generation_provider"],
        resultado["generation_model"],
        len(resultado["chunks_recuperados"]),
        telemetria.get("attempt") or tentativa + 1,
        resultado["status"],
        resultado["classe_fontes"] == "recusa",
        resultado["status"] == "Resposta Parcial",
        telemetria.get("time_to_first_token"),
    )


def _montar_mensagens(pergunta, chunks, historico):
    """Monta mensagens."""
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
    """Auxilia Fontes Citadas."""
    indices = []
    for correspondencia in _CITACAO_RE.finditer(texto):
        indice = int(correspondencia.group(1))
        if 1 <= indice <= min(len(chunks), MAX_CHUNKS_PROMPT) and indice not in indices:
            indices.append(indice)
    return [chunks[indice - 1] for indice in indices]


def _eh_recusa(texto):
    """Auxilia é Recusa."""
    return texto.strip().startswith(_MENSAGEM_RECUSA)
