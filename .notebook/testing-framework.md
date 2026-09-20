# Testing Framework

**Pattern:** The project uses Python's standard `unittest` framework.
**Gotcha:** Running `pytest` will fail as it is not part of the standard dependencies. 

**Execution:**
```bash
.\.venv\Scripts\python.exe -m unittest discover tests/
```
