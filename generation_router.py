"""Contrato e roteamento de providers externos de geração."""

import time


class ErroProviderGeracao(RuntimeError):
    """Falha externa segura e independente do provider de geração."""

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
        super().__init__(mensagem)
        self.provider = provider
        self.status_code = status_code
        self.retry_after = retry_after
        self.request_id = request_id
        self.retryable = (
            status_code in {408, 429, 500, 502, 503, 504, 529} if retryable is None else retryable
        )


class GenerationRouter:
    """Tenta providers em ordem sem repetir retrieval ou misturar streams."""

    def __init__(self, providers, *, esperar=time.sleep):
        self._providers = [provider for provider in providers if provider is not None]
        self._esperar = esperar
        self.ultima_execucao = None

    def transmitir(self, mensagens):
        tentados = []
        erros = []
        for provider in self._providers:
            nome = getattr(provider, "nome", type(provider).__name__)
            tentados.append(nome)
            for tentativa in range(2):
                emitiu_token = False
                try:
                    for pedaco in provider.transmitir(mensagens):
                        emitiu_token = True
                        yield pedaco
                    self.ultima_execucao = {
                        "generation_provider": nome,
                        "generation_model": getattr(provider, "modelo", None),
                        "fallback_used": len(tentados) > 1,
                        "attempted_providers": tentados,
                    }
                    return
                except ErroProviderGeracao as erro:
                    if emitiu_token:
                        self.ultima_execucao = {
                            "generation_provider": nome,
                            "generation_model": getattr(provider, "modelo", None),
                            "fallback_used": len(tentados) > 1,
                            "attempted_providers": tentados,
                        }
                        raise
                    erros.append(erro)
                    if self._deve_repetir(erro, tentativa):
                        self._esperar(erro.retry_after)
                        continue
                    break
        self.ultima_execucao = {
            "generation_provider": None,
            "generation_model": None,
            "fallback_used": len(tentados) > 1,
            "attempted_providers": tentados,
        }
        raise ErroProviderGeracao(
            "Nenhum provider de geração está disponível. Tente novamente em instantes.",
            provider=erros[-1].provider if erros else None,
            status_code=erros[-1].status_code if erros else None,
            retryable=False,
        ) from None

    @staticmethod
    def _deve_repetir(erro, tentativa):
        return (
            tentativa == 0
            and erro.retryable
            and erro.retry_after is not None
            and 0 <= erro.retry_after <= 2
        )
