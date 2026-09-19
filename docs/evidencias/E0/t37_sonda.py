import sys
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as tmp:
    tmp_path = Path(tmp)
    # create synthetic site-packages
    site_packages = tmp_path / "site-packages"
    site_packages.mkdir()
    
    # create a fake dist-info for a package called 'pacotefake'
    dist_info = site_packages / "pacotefake-1.0.dist-info"
    dist_info.mkdir()
    (dist_info / "METADATA").write_text("Name: pacotefake\nVersion: 1.0\n", encoding="utf-8")
    (dist_info / "RECORD").write_text("pacotefake/__init__.py,sha256=123,123\npacotefake-1.0.dist-info/RECORD,,\n", encoding="utf-8")
    
    # create a dummy requirements file
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("pacotefake==1.0\n", encoding="utf-8")
    
    # run the script with PYTHONPATH=site_packages
    env = os.environ.copy()
    env["PYTHONPATH"] = str(site_packages)
    
    print("Testando pacote fake com RECORD apontando para arquivo inexistente...")
    result = subprocess.run(
        [sys.executable, "-u", "scripts/00_checar_ambiente.py", str(req_file)],
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    Path("docs/evidencias/E0/stdout.txt").write_text(result.stdout, encoding="utf-8")
    print("Exit code:", result.returncode)
    if "corrompido:" in result.stdout:
        print("SUCESSO: Sonda detectou integridade corrompida!")
    else:
        print("FALHA: Nao detectou.")
