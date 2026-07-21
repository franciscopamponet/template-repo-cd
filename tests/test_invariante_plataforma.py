"""Trava o INVARIANTE CENTRAL: o núcleo é idêntico com ou sem Databricks.

Nada em `models/`, `common/`, `config/`, `data/` ou `entrypoints/` pode depender de
`platform/` (Rule 06). Se o toggle for Não, o `tools/init.py` poda `platform/` e o
repo tem que continuar rodando.

Estes testes existem para que uma violação futura quebre o CI, não a produção.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

NUCLEO = ["pipeline/common", "pipeline/models", "pipeline/data", "pipeline/entrypoints"]


def arquivos_do_nucleo() -> list[Path]:
    arquivos: list[Path] = []
    for pasta in NUCLEO:
        arquivos.extend(Path(pasta).rglob("*.py"))
    return [p for p in arquivos if "__pycache__" not in p.parts]


def test_existem_arquivos_para_checar():
    """Guarda contra o teste passar por vacuidade (glob vazio)."""
    assert len(arquivos_do_nucleo()) >= 7


@pytest.mark.parametrize("caminho", arquivos_do_nucleo(), ids=str)
def test_nucleo_nao_importa_platform(caminho: Path):
    """Rule 06: nenhum import de `platform` (o nosso) no núcleo.

    Usa AST em vez de grep para não confundir com a string 'platform' em
    comentários/docstrings, e para pegar `import x as y`.
    """
    arvore = ast.parse(caminho.read_text(encoding="utf-8"), filename=str(caminho))

    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            for alias in no.names:
                raiz = alias.name.split(".")[0]
                assert raiz != "platform", f"{caminho} importa platform"
        elif isinstance(no, ast.ImportFrom) and no.module:
            raiz = no.module.split(".")[0]
            assert raiz != "platform", f"{caminho} importa de platform"


def test_nucleo_roda_sem_a_pasta_platform(tmp_path, monkeypatch):
    """Simula o toggle = Não: sem `platform/`, o núcleo ainda importa e roda."""
    import os
    import shutil
    import subprocess
    import sys

    raiz = Path.cwd()
    copia = tmp_path / "projeto"
    # Copia o núcleo, deixando platform/ de fora — exatamente o que o init.py faz.
    shutil.copytree(
        raiz,
        copia,
        ignore=shutil.ignore_patterns(
            "platform", ".venv", ".git", "__pycache__", "*.db", "mlruns", "mlartifacts"
        ),
    )
    assert not (copia / "platform").exists()

    # O núcleo mora sob pipeline/ (src-layout): é ele que entra no PYTHONPATH.
    env = {**os.environ, "PYTHONPATH": str(copia / "pipeline")}
    resultado = subprocess.run(
        [
            sys.executable,
            "-c",
            "from models.exemplo_modelo.orchestrator import run; "
            "from common.data_source import build_data_source; "
            "print('nucleo OK sem platform/')",
        ],
        cwd=copia,
        env=env,
        capture_output=True,
        text=True,
    )
    assert resultado.returncode == 0, f"núcleo quebrou sem platform/: {resultado.stderr}"
    assert "nucleo OK sem platform/" in resultado.stdout
