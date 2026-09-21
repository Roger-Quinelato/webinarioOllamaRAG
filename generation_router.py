"""Contrato e roteamento de providers externos de geração."""

import logging
import time

LOGGER = logging.getLogger("rag.geracao")


class ErroProviderGeracao(RuntimeError):
    """Falha externa segura e independente do provider de geração. Herda de RuntimeError."""

    def __init__(
        self,
        mensagem,
        *,
        provider=None,
        status_code=None,
        retry_after=None,
        request_id=None,
        retryable=None,
    ):
        """Inicializa instância com dependências e parâmetros."""
        super().__init__(mensagem)
        self.provider = provider
        self.status_code = status_code
        self.retry_after = retry_after
        self.request_id = request_id
        self.retryable = (
            status_code in {408, 429, 500, 502, 503, 504, 529} if retryable is None else retryable
        )


class ExecucaoGeracao:
    """Uma execução de geração: iterador de deltas com a telemetria da própria chamada."""

    def __init__(self, providers, mensagens, esperar, relogio=time.monotonic):
        """Inicializa instância com dependências e parâmetros."""
        self._providers = providers
        self._mensagens = mensagens
        self._esperar = esperar
        self._relogio = relogio
        self._fluxo = self._executar()
        self.telemetria = None

    def __iter__(self):
        """Devolve o próprio iterador."""
        return self

    def __next__(self):
        """Devolve o próximo delta."""
        return next(self._fluxo)

    def _registrar(self, nome, provider, tentados, tentativa, inicio, primeiro_token, **extra):
        """Grava a telemetria da execução e emite o registro sem prompt, chunk ou chave."""
        self.telemetria = {
            "generation_provider": nome,
            "generation_model": getattr(provider, "modelo", None),
            "fallback_used": len(tentados) > 1,
            "attempted_providers": list(tentados),
            "attempt": None if tentativa is None else tentativa + 1,
            "time_to_first_token": (
                None if primeiro_token is None else round(primeiro_token - inicio, 3)
            ),
            **extra,
        }
        LOGGER.info(
            "geracao provider=%s modelo=%s tentativa=%s ttft=%s fallback=%s tentados=%s",
            nome,
            self.telemetria["generation_model"],
            self.telemetria["attempt"],
            self.telemetria["time_to_first_token"],
            self.telemetria["fallback_used"],
            ",".join(tentados),
        )

    def _executar(self):
        """Tenta os providers em ordem e transmite os deltas do primeiro que responder."""
        tentados = []
        erros = []
        inicio = self._relogio()
        for provider in self._providers:
            nome = getattr(provider, "nome", type(provider).__name__)
            tentados.append(nome)
            for tentativa in range(2):
                primeiro_token = None
                try:
                    for pedaco in provider.transmitir(self._mensagens):
                        if primeiro_token is None:
                            primeiro_token = self._relogio()
                        yield pedaco
                    self._registrar(nome, provider, tentados, tentativa, inicio, primeiro_token)
                    return
                except ErroProviderGeracao as erro:
                    if primeiro_token is not None:
                        self._registrar(nome, provider, tentados, tentativa, inicio, primeiro_token)
                        raise
                    erros.append(erro)
                    LOGGER.warning(
                        "geracao_falha provider=%s tentativa=%s status=%s retryable=%s",
                        nome, tentativa + 1, erro.status_code, erro.retryable,
                    )
                    if self._deve_repetir(erro, tentativa):
                        self._esperar(erro.retry_after)
                        continue
                    break
        self._registrar(None, None, tentados, None, inicio, None)
        raise ErroProviderGeracao(
            "Nenhum provider de geração está disponível. Tente novamente em instantes.",
            provider=erros[-1].provider if erros else None,
            status_code=erros[-1].status_code if erros else None,
            retryable=False,
        ) from None

    @staticmethod
    def _deve_repetir(erro, tentativa):
        """Auxilia deve repetir."""
        return (
            tentativa == 0
            and erro.retryable
            and erro.retry_after is not None
            and 0 <= erro.retry_after <= 2
        )


class GenerationRouter:
    """Tenta providers em ordem sem repetir retrieval ou misturar streams.

    Não guarda estado de execução: cada chamada devolve uma ``ExecucaoGeracao`` com a
    própria telemetria, para que sessões concorrentes não leiam dados umas das outras.
    """

    def __init__(self, providers, *, esperar=time.sleep):
        """Inicializa instância com dependências e parâmetros."""
        self._providers = [provider for provider in providers if provider is not None]
        self._esperar = esperar

    def transmitir(self, mensagens):
        """Transmite valor do fluxo."""
        return ExecucaoGeracao(self._providers, mensagens, self._esperar)
