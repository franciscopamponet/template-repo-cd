"""Launcher fino — execução via PLATAFORMA / serverless (toggle Databricks = Sim).

Papel: parsear o caminho do config e chamar o orchestrator. Nada além disso.
Zero lógica de negócio (ver `docs/guides/entrypoints.md`).

Só faz sentido com o toggle = Sim; o `tools/init.py` poda este arquivo se o toggle
for Não. O núcleo chamado aqui é EXATAMENTE o mesmo do `run_local.py` — a diferença
de plataforma mora no config (`tracking.databricks`, `data_source.type`), nunca no
núcleo (Rule 06 / invariante central).

Uso (job na plataforma):
    python entrypoints/run_serverless.py --config config/exemplo_modelo.yaml
"""

from __future__ import annotations

import argparse

from models.exemplo_modelo.orchestrator import run


def main() -> None:
    parser = argparse.ArgumentParser(description="Roda o pipeline na plataforma.")
    parser.add_argument("--config", required=True, help="Caminho do YAML de config do modelo.")
    args = parser.parse_args()

    resultado = run(args.config)
    print(f"run_id: {resultado['run_id']}")
    print(f"métricas: {resultado['metrics']}")


if __name__ == "__main__":
    main()
