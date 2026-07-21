"""build_model — etapa 2/5 da anatomia (Rule 00).

Papel no contrato: construir o objeto de modelo (ainda não treinado) a partir dos
hiperparâmetros do config.

Sem treino e sem I/O: esta etapa não lê dado, não escreve arquivo e não fala com
tracking. NÃO importa mlflow (Rule 01). Hiperparâmetros vêm do config (Rule 07).
"""

from __future__ import annotations

from typing import Any

from sklearn.base import BaseEstimator
from sklearn.ensemble import RandomForestClassifier


def build_model(params: dict[str, Any]) -> BaseEstimator:
    """Devolve o estimador configurado, sem treinar.

    Params esperados no config (Rule 07), todos opcionais com default do sklearn:
      - `n_estimators`, `max_depth`, `min_samples_leaf`, `random_state`, `class_weight`.
    """
    hiperparametros = {
        "n_estimators": params.get("n_estimators", 100),
        "max_depth": params.get("max_depth"),
        "min_samples_leaf": params.get("min_samples_leaf", 1),
        "random_state": params.get("random_state"),
        "class_weight": params.get("class_weight"),
    }
    return RandomForestClassifier(**hiperparametros)
