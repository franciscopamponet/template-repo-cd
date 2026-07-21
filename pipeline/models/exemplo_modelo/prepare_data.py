"""prepare_data — etapa 1/5 da anatomia (Rule 00).

Papel no contrato: pedir o dado à interface `DataSource` e devolver os conjuntos
prontos para treino/avaliação.

NÃO sabe de onde o dado vem (Decisão 3): recebe um `DataSource` já construído pela
factory a partir do config. NÃO importa mlflow (Rule 01). Nenhum caminho, coluna ou
parâmetro é hardcoded — tudo vem do config (Rule 07).
"""

from __future__ import annotations

from typing import Any, NamedTuple

import pandas as pd

from common.data_source import DataSource
from common.splits import random_split, temporal_split


class PreparedData(NamedTuple):
    """Contrato de saída desta etapa, consumido por train e evaluate_model."""

    x_train: pd.DataFrame
    x_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    feature_names: list[str]


def prepare_data(source: DataSource, params: dict[str, Any]) -> PreparedData:
    """Lê da fonte, seleciona features/alvo e divide em treino/teste.

    Params esperados no config (Rule 07):
      - `target` (obrigatório): nome da coluna alvo.
      - `features` (opcional): lista de colunas. Default: todas menos o alvo.
      - `split` (opcional): 'random' (default) ou 'temporal'.
      - `test_size`, `random_state`, `stratify_col`: para split aleatório.
      - `time_col`, `cutoff`: para split temporal.
    """
    target = params.get("target")
    if not target:
        raise ValueError("params.target é obrigatório no config (coluna alvo).")

    df = source.read()
    if target not in df.columns:
        raise ValueError(f"Coluna alvo {target!r} não existe na fonte de dados.")

    features = params.get("features") or [c for c in df.columns if c != target]
    faltando = [c for c in features if c not in df.columns]
    if faltando:
        raise ValueError(f"Colunas de feature ausentes na fonte: {faltando}")

    split_kind = params.get("split", "random")
    if split_kind == "temporal":
        time_col = params.get("time_col")
        if not time_col:
            raise ValueError("split 'temporal' exige params.time_col no config.")
        train_df, test_df = temporal_split(
            df,
            time_col=time_col,
            cutoff=params.get("cutoff"),
            test_size=None if params.get("cutoff") else params.get("test_size"),
        )
    elif split_kind == "random":
        train_df, test_df = random_split(
            df,
            test_size=params.get("test_size", 0.2),
            random_state=params.get("random_state"),
            stratify_col=params.get("stratify_col"),
        )
    else:
        raise ValueError(f"params.split inválido: {split_kind!r}. Use 'random' ou 'temporal'.")

    return PreparedData(
        x_train=train_df[features],
        x_test=test_df[features],
        y_train=train_df[target],
        y_test=test_df[target],
        feature_names=list(features),
    )
