"""orchestrator — etapa 5/5 da anatomia (Rule 00). A ESPINHA DORSAL.

Papel no contrato: amarrar o fluxo config → prepare → build → train → evaluate.

É o ÚNICO arquivo deste modelo que fala com tracking, e faz isso exclusivamente via
`common/tracking.py` (Rule 01). Os outros 4 arquivos não importam mlflow — nem
indiretamente. Nada é hardcoded: tudo vem do config (Rule 07).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from common.config import BaseModelConfig, load_config
from common.data_source import build_data_source
from common.tracking import Tracker
from models.exemplo_modelo.build_model import build_model
from models.exemplo_modelo.evaluate_model import evaluate_model
from models.exemplo_modelo.prepare_data import prepare_data
from models.exemplo_modelo.train import train


def run(config_path: str | Path) -> dict[str, Any]:
    """Roda o pipeline ponta a ponta e devolve o resultado da execução.

    Fluxo: carrega e valida o config → constrói a fonte de dados → prepara →
    constrói o modelo → treina → avalia → loga tudo via `common/tracking.py`.

    Devolve um dicionário com `metrics`, `run_id` e `params`.
    """
    config: BaseModelConfig = load_config(config_path)
    params = config.params

    source = build_data_source(config.data_source)
    prepared = prepare_data(source, params)

    model = build_model(params)

    tracker = Tracker(config.tracking)
    with tracker.start_run(run_name=config.name) as run_ctx:
        tracker.log_params(
            {
                **params,
                "n_features": len(prepared.feature_names),
                "n_train": len(prepared.x_train),
                "n_test": len(prepared.x_test),
                "data_source_type": config.data_source.type,
            }
        )

        trained = train(model, prepared.x_train, prepared.y_train)
        metrics = evaluate_model(trained, prepared.x_test, prepared.y_test)

        tracker.log_metrics(metrics)
        tracker.log_model(trained, "model")

        run_id = getattr(getattr(run_ctx, "info", None), "run_id", None)

    return {"metrics": metrics, "run_id": run_id, "params": dict(params)}
