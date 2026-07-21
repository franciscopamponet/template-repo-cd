"""train — etapa 3/5 da anatomia (Rule 00).

Papel no contrato: receber o modelo construído + os dados já preparados e devolver o
modelo treinado.

Não lê config, não faz I/O e NÃO importa mlflow (Rule 01). Quem loga o treino é o
`orchestrator.py`, via `common/tracking.py`.
"""

from __future__ import annotations

import pandas as pd
from sklearn.base import BaseEstimator


def train(model: BaseEstimator, x_train: pd.DataFrame, y_train: pd.Series) -> BaseEstimator:
    """Treina o modelo e o devolve ajustado."""
    model.fit(x_train, y_train)
    return model
