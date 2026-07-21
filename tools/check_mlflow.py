#!/usr/bin/env python3
"""Cancela: MLFLOW É CENTRALIZADO (Rule 01).

Só `pipeline/common/tracking.py` importa mlflow. Nenhum outro arquivo — nem os 4
primeiros da anatomia, nem `pipeline/data/`, nem `pipeline/config/`, nem entrypoints.
Quem quiser logar experimento passa pelo `orchestrator.py` -> `pipeline/common/tracking.py`.

Usa AST, não grep: uma docstring que MENCIONA mlflow ("NÃO importa mlflow") não é
uma violação, e `import mlflow as mf` é.

Stdlib only: roda sem `uv sync`.

Uso:
    python3 tools/check_mlflow.py
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# O único arquivo do repo autorizado a falar com mlflow.
AUTORIZADO = Path("pipeline/common/tracking.py")

IGNORAR_PASTAS = {".venv", ".git", "__pycache__", ".pytest_cache", ".ruff_cache", "dist"}


def arquivos_python() -> list[Path]:
    return [p for p in RAIZ.rglob("*.py") if not IGNORAR_PASTAS & set(p.relative_to(RAIZ).parts)]


def importa_mlflow(caminho: Path) -> list[str]:
    """Devolve as linhas de import de mlflow encontradas no arquivo."""
    try:
        arvore = ast.parse(caminho.read_text(encoding="utf-8"), filename=str(caminho))
    except SyntaxError as erro:
        print(f"AVISO: não consegui parsear {caminho}: {erro}")
        return []

    violacoes = []
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            for alias in no.names:
                if alias.name.split(".")[0] == "mlflow":
                    violacoes.append(f"linha {no.lineno}: import {alias.name}")
        elif isinstance(no, ast.ImportFrom) and no.module and no.module.split(".")[0] == "mlflow":
            violacoes.append(f"linha {no.lineno}: from {no.module} import ...")
    return violacoes


def main() -> int:
    encontrados: dict[Path, list[str]] = {}

    for caminho in arquivos_python():
        relativo = caminho.relative_to(RAIZ)
        if relativo == AUTORIZADO:
            continue
        violacoes = importa_mlflow(caminho)
        if violacoes:
            encontrados[relativo] = violacoes

    if not encontrados:
        print(f"OK: só {AUTORIZADO} importa mlflow (Rule 01).")
        return 0

    print("ERRO: VAZAMENTO DE MLFLOW (Rule 01)\n")
    print("MLflow é centralizado: só pipeline/common/tracking.py importa mlflow. O tracking")
    print("passa pelo orchestrator.py -> pipeline/common/tracking.py. Espalhar `import mlflow`")
    print("acopla o pipeline à ferramenta e quebra o toggle de plataforma.\n")

    for arquivo, violacoes in sorted(encontrados.items()):
        print(f"  {arquivo}")
        for v in violacoes:
            print(f"      {v}")

    print("\nComo corrigir: remova o import e roteie o que você precisa por")
    print("pipeline/common/tracking.py, chamado a partir do orchestrator.py do seu modelo.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
