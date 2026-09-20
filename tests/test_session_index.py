import unittest
from types import SimpleNamespace

import chromadb

from ollama_embedding_provider import ProviderEmbeddingsOllama
from openai_rag import BaseAtiva
from session_index import criar_indice_sessao

def chunks_de_teste():
    return [
        {
            "id": f"upload-{numero}",
            "texto": f"Trecho do upload {numero}.",
            "metadados": {
                "arquivo": "upload.pdf",
                "pagina": numero,
                "ano": 2025,
                "tema": "upload",
                "idioma": "pt",
                "chunk_id": f"upload-{numero}",
            },
        }
        for numero in range(1, 4)
    ]

class SessionIndexTest(unittest.TestCase):
    def test_cria_indice_sessao_retorna_base_ativa_valida(self):
        chamadas = []
        def embed(**kwargs):
            chamadas.append(kwargs)
            return SimpleNamespace(embeddings=[[0.1, 0.2, 0.3] for _ in kwargs["input"]])

        provider = ProviderEmbeddingsOllama(client=SimpleNamespace(embed=embed))
        chunks = chunks_de_teste()
        
        base = criar_indice_sessao(provider, "sessao-123", chunks)
        
        self.assertIsInstance(base, BaseAtiva)
        self.assertEqual(base.nome, "Índice de Sessão (sessao-123)")
        self.assertEqual(base.tipo, "Índice de Sessão")
        self.assertEqual(base.sessao_id, "sessao-123")
        
        metadados = base.colecao.metadata
        self.assertEqual(metadados["provedor_embedding"], "Ollama")
        self.assertEqual(metadados["modelo_embedding"], "bge-m3")
        self.assertEqual(metadados["dimensao_embedding"], 3)
        self.assertEqual(metadados["versao_colecao"], "bge-m3-v1")
        self.assertEqual(metadados["status"], "ready")
        self.assertEqual(metadados["corpus"], "Índice de Sessão")
        self.assertEqual(base.colecao.count(), 3)
        
    def test_indices_de_sessao_diferentes_sao_isolados(self):
        def embed(**kwargs):
            return SimpleNamespace(embeddings=[[0.1, 0.2, 0.3] for _ in kwargs["input"]])

        provider = ProviderEmbeddingsOllama(client=SimpleNamespace(embed=embed))
        
        base1 = criar_indice_sessao(provider, "sessao-1", chunks_de_teste())
        base2 = criar_indice_sessao(provider, "sessao-2", chunks_de_teste())
        
        self.assertNotEqual(base1.colecao.name, base2.colecao.name)
        
        base1.colecao.add(
            ids=["chunk-extra"],
            documents=["extra"],
            metadatas=[{"arquivo": "extra.pdf", "pagina": 1}],
            embeddings=[[0.1, 0.2, 0.3]]
        )
        self.assertEqual(base1.colecao.count(), 4)
        self.assertEqual(base2.colecao.count(), 3)

if __name__ == "__main__":
    unittest.main()
