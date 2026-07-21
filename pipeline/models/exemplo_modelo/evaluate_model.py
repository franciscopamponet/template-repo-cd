"""evaluate_model — etapa 4/5 da anatomia (Rule 00).

Papel no contrato: calcular as métricas do modelo treinado sobre o conjunto de teste
e devolvê-las como um dicionário simples.

Devolve métricas; não as loga. NÃO importa mlflow (Rule 01) — quem loga é o
`orchestrator.py`, via `common/tracking.py`.
"""

from __future__ import annotations

import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)


def evaluate_model(
    model: BaseEstimator,
    x_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict[str, float]:
    """Devolve um dicionário de métricas do modelo no conjunto de teste.

    `average='weighted'` mantém as métricas válidas tanto no caso binário quanto no
    multiclasse. `zero_division=0` evita exceção em classes sem predição.
    """
    y_pred = model.predict(x_test)
    media = "weighted"
    return {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "f1": float(f1_score(y_test, y_pred, average=media, zero_division=0)),
        "precision": float(precision_score(y_test, y_pred, average=media, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, average=media, zero_division=0)),
    }
