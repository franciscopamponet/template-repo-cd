"""Utilitários de split compartilhados entre modelos.

Split aleatório (train/test) e split temporal (por data de corte ou por fração
ordenada no tempo). Parâmetros vêm do config (Rule 07); aqui só a mecânica.
"""

from __future__ import annotations

import pandas as pd
from sklearn.model_selection import train_test_split as _sk_train_test_split


def random_split(
    df: pd.DataFrame,
    test_size: float = 0.2,
    random_state: int | None = None,
    stratify_col: str | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split aleatório train/test, com estratificação opcional por coluna."""
    stratify = df[stratify_col] if stratify_col else None
    train_df, test_df = _sk_train_test_split(
        df,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify,
    )
    return train_df, test_df


def temporal_split(
    df: pd.DataFrame,
    time_col: str,
    cutoff: str | pd.Timestamp | None = None,
    test_size: float | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split temporal: treino no passado, teste no futuro.

    Dois modos, mutuamente exclusivos:
      - `cutoff`: registros com `time_col < cutoff` vão para treino; `>= cutoff`,
        para teste.
      - `test_size`: ordena por `time_col` e reserva a fração final para teste.

    Não embaralha: preserva a ordem temporal para evitar vazamento do futuro.
    """
    if (cutoff is None) == (test_size is None):
        raise ValueError("Informe exatamente um de 'cutoff' ou 'test_size'.")

    ordered = df.sort_values(time_col)

    if cutoff is not None:
        cutoff_ts = pd.Timestamp(cutoff)
        times = pd.to_datetime(ordered[time_col])
        train_df = ordered[times < cutoff_ts]
        test_df = ordered[times >= cutoff_ts]
        return train_df, test_df

    n_test = int(round(len(ordered) * test_size))
    if n_test <= 0:
        return ordered, ordered.iloc[0:0]
    train_df = ordered.iloc[:-n_test]
    test_df = ordered.iloc[-n_test:]
    return train_df, test_df
