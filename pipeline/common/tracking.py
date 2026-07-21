"""Único ponto de contato do repo com MLflow (Rule 01).

Nenhum outro arquivo importa mlflow diretamente. Só o `orchestrator.py` de cada
modelo usa este wrapper, e este wrapper é quem encapsula a diferença entre rodar
dentro e fora do Databricks.

# VALIDADO EMPIRICAMENTE (MLflow 3.14.0, fora do Databricks):
#   - O file store './mlruns' NÃO funciona mais: o MLflow o colocou em maintenance
#     mode e levanta MlflowException. Por isso o default local passou a ser um
#     backend SQLite ('sqlite:///mlflow.db'), que é o caminho recomendado.
#   - Com o backend SQLite, o Model Registry funciona fora do Databricks
#     (register_model + versionamento verificados de ponta a ponta).
#   - A convenção de experiment_name com path '/Shared/...' é específica do
#     Databricks e NÃO se aplica localmente: usamos nome simples.
#
# TODO — AINDA NÃO VALIDADO EMPIRICAMENTE:
#   - O caminho Databricks (`tracking.databricks: true`) segue sem validação em
#     ambiente real. Não cravar certezas sobre ele até rodar num workspace de fato.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from common.config import TrackingConfig

# Backend local default. File store ('./mlruns') não é mais suportado pelo MLflow
# (ver nota de validação no topo). SQLite é o caminho recomendado e habilita o
# Model Registry fora do Databricks.
DEFAULT_TRACKING_URI = "sqlite:///mlflow.db"


class Tracker:
    """Wrapper fino sobre MLflow, configurado a partir de `TrackingConfig`.

    Uso típico (no `orchestrator.py`):

        tracker = Tracker(config.tracking)
        with tracker.start_run():
            tracker.log_params(params)
            tracker.log_metrics(metrics)
            tracker.log_model(model, "model")
    """

    def __init__(self, config: TrackingConfig) -> None:
        import mlflow

        self._mlflow = mlflow
        self.config = config

        if config.databricks:
            # Caminho Databricks: NÃO validado empiricamente (ver TODO no topo).
            # Deixamos o tracking_uri/registry_uri a cargo do ambiente Databricks,
            # sobrescrevendo apenas se o config trouxer valores explícitos.
            if config.tracking_uri and config.tracking_uri != DEFAULT_TRACKING_URI:
                mlflow.set_tracking_uri(config.tracking_uri)
            if config.registry_uri:
                mlflow.set_registry_uri(config.registry_uri)
        else:
            # Caminho LOCAL (validado): backend SQLite, experimento por nome simples.
            mlflow.set_tracking_uri(config.tracking_uri)
            if config.registry_uri:
                mlflow.set_registry_uri(config.registry_uri)

        mlflow.set_experiment(config.experiment_name)

    @contextmanager
    def start_run(self, run_name: str | None = None, **kwargs: Any):
        with self._mlflow.start_run(run_name=run_name, **kwargs) as run:
            yield run

    def log_params(self, params: dict[str, Any]) -> None:
        self._mlflow.log_params(params)

    def log_metrics(self, metrics: dict[str, float], step: int | None = None) -> None:
        self._mlflow.log_metrics(metrics, step=step)

    def log_model(self, model: Any, name: str, **kwargs: Any) -> Any:
        """Loga o modelo. `registered_model_name=...` registra no Model Registry.

        sklearn é o flavor default do esqueleto; modelos com outro flavor
        sobrescrevem via kwargs/uso direto no orchestrator.
        """
        # MLflow 3.x: o parâmetro é `name`; `artifact_path` está deprecado.
        return self._mlflow.sklearn.log_model(model, name=name, **kwargs)

    def set_experiment(self, experiment_name: str) -> None:
        self._mlflow.set_experiment(experiment_name)
