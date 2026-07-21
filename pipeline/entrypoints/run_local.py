"""Launcher fino — execução LOCAL (toggle Databricks = Não).

Papel: parsear o caminho do config e chamar o orchestrator. Nada além disso.
Zero lógica de negócio (ver `docs/guides/entrypoints.md`).

Uso:
    uv run python entrypoints/run_local.py --config config/exemplo_modelo.yaml
"""

from __future__ import annotations

import argparse

from models.exemplo_modelo.orchestrator import run


def main() -> None:
    parser = argparse.ArgumentParser(description="Roda o pipeline localmente.")
    parser.add_argument("--config", required=True, help="Caminho do YAML de config do modelo.")
    args = parser.parse_args()

    resultado = run(args.config)
    print(f"run_id: {resultado['run_id']}")
    print(f"métricas: {resultado['metrics']}")


if __name__ == "__main__":
    main()
