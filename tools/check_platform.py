#!/usr/bin/env python3
"""Cancela: PLATAFORMA É OPCIONAL (Rule 06) — o invariante central.

O núcleo é IDÊNTICO com ou sem Databricks. Nada em `models/`, `common/`, `config/`,
`data/` ou `entrypoints/` pode importar de `platform/`. Se o toggle for Não, o
`tools/init.py` poda `platform/` e o repo tem que continuar rodando.

Usa AST, não grep: a palavra "platform" numa docstring não é violação.

NOTA SOBRE `import platform` DA STDLIB:
    `platform` também é um módulo da stdlib (platform.system() etc). Hoje, a pasta
    platform/ deste repo não contém nenhum .py, então um `import platform` resolve
    para a stdlib — a violação seria de intenção, não de efeito. Ainda assim, este
    script proíbe o nome no núcleo: num repo onde `platform/` existe, `import platform`
    é ambíguo para quem lê, e a ambiguidade é exatamente o que a Rule 06 evita.
    Se você precisa mesmo da stdlib, use `import sys` / `sysconfig`, ou isole o uso
    fora do núcleo.

Stdlib only: roda sem `uv sync`.

Uso:
    python3 tools/check_platform.py
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# O núcleo: o que precisa sobreviver à poda de platform/. Mora todo sob pipeline/.
NUCLEO = ["pipeline"]

PROIBIDO = "platform"

IGNORAR = {"__pycache__", ".venv", ".git"}


def arquivos_do_nucleo() -> list[Path]:
    arquivos: list[Path] = []
    for pasta in NUCLEO:
        base = RAIZ / pasta
        if not base.exists():
            continue
        arquivos.extend(
            p for p in base.rglob("*.py") if not IGNORAR & set(p.relative_to(RAIZ).parts)
        )
    return sorted(arquivos)


def importa_platform(caminho: Path) -> list[str]:
    try:
        arvore = ast.parse(caminho.read_text(encoding="utf-8"), filename=str(caminho))
    except SyntaxError as erro:
        print(f"AVISO: não consegui parsear {caminho}: {erro}")
        return []

    violacoes = []
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            for alias in no.names:
                if alias.name.split(".")[0] == PROIBIDO:
                    violacoes.append(f"linha {no.lineno}: import {alias.name}")
        elif isinstance(no, ast.ImportFrom) and no.module and no.module.split(".")[0] == PROIBIDO:
            violacoes.append(f"linha {no.lineno}: from {no.module} import ...")
    return violacoes


def main() -> int:
    arquivos = arquivos_do_nucleo()

    if not arquivos:
        # Guarda contra passar por vacuidade: se o glob quebrar, isto acusa.
        print("ERRO: não encontrei nenhum arquivo do núcleo para checar.")
        print(f"Esperava .py em: {', '.join(NUCLEO)}")
        return 1

    encontrados: dict[Path, list[str]] = {}
    for caminho in arquivos:
        violacoes = importa_platform(caminho)
        if violacoes:
            encontrados[caminho.relative_to(RAIZ)] = violacoes

    if not encontrados:
        print(f"OK: o núcleo não importa platform/ ({len(arquivos)} arquivos checados, Rule 06).")
        return 0

    print("ERRO: VAZAMENTO DE PLATAFORMA (Rule 06)\n")
    print("INVARIANTE CENTRAL: o núcleo é idêntico com ou sem Databricks. platform/ é")
    print("a casca que o toggle liga/desliga — se o toggle for Não, ela DEIXA DE EXISTIR.")
    print("Um import de platform/ no núcleo faz o projeto quebrar sem Databricks.\n")

    for arquivo, violacoes in sorted(encontrados.items()):
        print(f"  {arquivo}")
        for v in violacoes:
            print(f"      {v}")

    print("\nComo corrigir: o núcleo recebe valores, não busca plataforma. Passe o que")
    print("você precisa via config/ (Rule 07). Se for stdlib `platform`, veja a nota no")
    print("topo deste script — o nome é ambíguo aqui e deve ser evitado no núcleo.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
