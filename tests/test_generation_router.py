import unittest

from generation_router import ErroProviderGeracao, ExecucaoGeracao, GenerationRouter


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

        execucao = router.transmitir(mensagens)

        self.assertEqual("".join(execucao), "Resposta [1]")
        self.assertEqual(execucao.telemetria["generation_provider"], "NVIDIA")
        self.assertTrue(execucao.telemetria["fallback_used"])
        self.assertEqual(execucao.telemetria["attempted_providers"], ["OpenAI", "NVIDIA"])
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

        execucao = router.transmitir([])

        self.assertEqual("".join(execucao), "Resposta [1]")
        self.assertEqual(len(openai.mensagens), 2)
        self.assertFalse(execucao.telemetria["fallback_used"])
        self.assertEqual(execucao.telemetria["attempt"], 2)

    def test_retry_after_longo_avanca_para_nvidia_sem_repetir_openai(self):
        """Verifica que retry after longo avanca para NVIDIA sem repetir OpenAI."""
        openai = ProviderFake(
            "OpenAI",
            [[ErroProviderGeracao("limite", provider="OpenAI", status_code=429, retry_after=3)]],
        )
        nvidia = ProviderFake("NVIDIA", [["Resposta [1]"]])
        router = GenerationRouter([openai, nvidia])

        execucao = router.transmitir([])

        self.assertEqual("".join(execucao), "Resposta [1]")
        self.assertEqual(len(openai.mensagens), 1)
        self.assertEqual(execucao.telemetria["attempted_providers"], ["OpenAI", "NVIDIA"])

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
        self.assertEqual(fluxo.telemetria["generation_provider"], "OpenAI")
        self.assertEqual(fluxo.telemetria["attempted_providers"], ["OpenAI"])

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

    def test_telemetria_pertence_a_cada_execucao_e_nao_ao_roteador(self):
        """Verifica que execuções do mesmo roteador não compartilham telemetria."""
        primeiro = ProviderFake("OpenAI", [["A"], ["B"]])
        router = GenerationRouter([primeiro])
        execucao_a = router.transmitir([])
        execucao_b = router.transmitir([])

        self.assertEqual("".join(execucao_a), "A")
        self.assertEqual("".join(execucao_b), "B")
        self.assertIsNot(execucao_a.telemetria, execucao_b.telemetria)
        self.assertFalse(hasattr(router, "ultima_execucao"))

    def test_mede_tempo_ate_o_primeiro_token(self):
        """Verifica que a telemetria registra o tempo até o primeiro token."""
        instantes = iter([10.0, 12.5, 13.0])
        execucao = ExecucaoGeracao(
            [ProviderFake("OpenAI", [["A", "B"]])], [], lambda _: None, relogio=lambda: next(instantes)
        )

        self.assertEqual("".join(execucao), "AB")
        self.assertEqual(execucao.telemetria["time_to_first_token"], 2.5)

    def test_registro_omite_prompt_chave_e_texto(self):
        """Verifica que o registro traz provider e tentativa, mas nunca prompt, chave ou resposta."""
        openai = ProviderFake(
            "OpenAI", [[ErroProviderGeracao("segredo-sk-123", provider="OpenAI", status_code=503)]]
        )
        nvidia = ProviderFake("NVIDIA", [["texto da resposta"]])
        mensagens = [{"role": "user", "content": "prompt confidencial"}]

        with self.assertLogs("rag.geracao", level="INFO") as registro:
            "".join(GenerationRouter([openai, nvidia]).transmitir(mensagens))

        saida = " | ".join(registro.output)
        self.assertIn("provider=NVIDIA", saida)
        self.assertIn("tentativa=1", saida)
        for proibido in ("prompt confidencial", "sk-123", "texto da resposta"):
            self.assertNotIn(proibido, saida)


if __name__ == "__main__":
    unittest.main()
