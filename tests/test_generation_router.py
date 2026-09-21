import unittest

from generation_router import ErroProviderGeracao, GenerationRouter


class ProviderFake:
    """Representa Provider Fake."""
    def __init__(self, nome, tentativas):
        """Inicializa instância com dependências e parâmetros."""
        self.nome = nome
        self._tentativas = list(tentativas)
        self.mensagens = []

    def transmitir(self, mensagens):
        """Transmite valor do fluxo."""
        self.mensagens.append(mensagens)
        for evento in self._tentativas.pop(0):
            if isinstance(evento, Exception):
                raise evento
            yield evento


class GenerationRouterTest(unittest.TestCase):
    """Agrupa testes de Generation Router Test. Herda de unittest.TestCase."""
    def test_limite_openai_antes_do_primeiro_token_usa_nvidia(self):
        """Verifica que limite OpenAI antes do primeiro token usa NVIDIA."""
        openai = ProviderFake(
            "OpenAI",
            [[ErroProviderGeracao("limite", provider="OpenAI", status_code=429)]],
        )
        nvidia = ProviderFake("NVIDIA", [["Resposta [1]"]])
        router = GenerationRouter([openai, nvidia, None])
        mensagens = [{"role": "user", "content": "Pergunta"}]

        self.assertEqual("".join(router.transmitir(mensagens)), "Resposta [1]")
        self.assertEqual(router.ultima_execucao["generation_provider"], "NVIDIA")
        self.assertTrue(router.ultima_execucao["fallback_used"])
        self.assertEqual(router.ultima_execucao["attempted_providers"], ["OpenAI", "NVIDIA"])
        self.assertEqual(openai.mensagens, [mensagens])
        self.assertEqual(nvidia.mensagens, [mensagens])

    def test_retry_after_curto_repete_provider_antes_do_fallback(self):
        """Verifica que retry after curto repete provider antes do fallback."""
        openai = ProviderFake(
            "OpenAI",
            [
                [ErroProviderGeracao("limite", provider="OpenAI", status_code=429, retry_after=1)],
                ["Resposta [1]"],
            ],
        )
        router = GenerationRouter([openai])

        self.assertEqual("".join(router.transmitir([])), "Resposta [1]")
        self.assertEqual(len(openai.mensagens), 2)
        self.assertFalse(router.ultima_execucao["fallback_used"])

    def test_retry_after_longo_avanca_para_nvidia_sem_repetir_openai(self):
        """Verifica que retry after longo avanca para NVIDIA sem repetir OpenAI."""
        openai = ProviderFake(
            "OpenAI",
            [[ErroProviderGeracao("limite", provider="OpenAI", status_code=429, retry_after=3)]],
        )
        nvidia = ProviderFake("NVIDIA", [["Resposta [1]"]])
        router = GenerationRouter([openai, nvidia])

        self.assertEqual("".join(router.transmitir([])), "Resposta [1]")
        self.assertEqual(len(openai.mensagens), 1)
        self.assertEqual(router.ultima_execucao["attempted_providers"], ["OpenAI", "NVIDIA"])

    def test_falha_apos_token_nao_chama_provider_seguinte(self):
        """Verifica que falha após token não chama provider seguinte."""
        openai = ProviderFake(
            "OpenAI",
            [["Começo", ErroProviderGeracao("interrompido", provider="OpenAI", status_code=503)]],
        )
        nvidia = ProviderFake("NVIDIA", [["Não deve ser chamado"]])
        router = GenerationRouter([openai, nvidia])
        fluxo = router.transmitir([])

        self.assertEqual(next(fluxo), "Começo")
        with self.assertRaisesRegex(ErroProviderGeracao, "interrompido"):
            next(fluxo)
        self.assertEqual(nvidia.mensagens, [])
        self.assertEqual(router.ultima_execucao["generation_provider"], "OpenAI")
        self.assertEqual(router.ultima_execucao["attempted_providers"], ["OpenAI"])

    def test_todos_os_providers_indisponiveis_expoem_erro_seguro(self):
        """Verifica que todos os providers indisponiveis expõem erro seguro."""
        openai = ProviderFake(
            "OpenAI", [[ErroProviderGeracao("limite", provider="OpenAI", status_code=429)]]
        )
        nvidia = ProviderFake(
            "NVIDIA", [[ErroProviderGeracao("indisponível", provider="NVIDIA", status_code=503)]]
        )
        router = GenerationRouter([openai, nvidia, None])

        with self.assertRaisesRegex(ErroProviderGeracao, "Nenhum provider de geração"):
            list(router.transmitir([]))


if __name__ == "__main__":
    unittest.main()
