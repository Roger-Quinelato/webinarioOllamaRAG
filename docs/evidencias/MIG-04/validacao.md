# Evidência MIG-04

**Issue:** #62
**Objetivo:** Criar o Índice de Sessão temporário e provar o isolamento entre sessões e entre bases.

## Verificação Test-First
Os testes foram criados (`tests/test_session_index.py`) e validados na estratégia red-green, assegurando:
- Criação de coleção efêmera correta.
- Metadados e compatibilidade conferidos com `bge-m3`.
- Isolamento garantido: uploads em uma sessão não vazam para outras sessões (testado adicionando a uma coleção e verificando o count das coleções efêmeras).

**Comando:**
```bash
.\.venv\Scripts\python.exe -m unittest discover tests/
```
**Resultado:** Todos os testes passaram (41 testes).
