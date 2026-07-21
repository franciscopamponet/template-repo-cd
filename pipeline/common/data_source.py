"""Contrato neutro de acesso a dados (Decisão 3).

Define o `Protocol` `DataSource` e a factory que, a partir do config, devolve a
implementação concreta correta. O pipeline pede o dado à interface e nunca sabe de
onde ele vem.

Este arquivo é o CONTRATO: não importa spark, databricks nem sqlalchemy. As
implementações concretas moram em `data/sources/` e trazem essas dependências de
forma lazy (Rule 06 — plataforma opcional).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    import pandas as pd


@runtime_checkable
class DataSource(Protocol):
    """Interface mínima e estável de uma fonte de dados.

    Implementações concretas: `ParquetSource`, `SparkTableSource`, `SQLSource`
    (em `data/sources/`). Escolhidas via config (Rule 07).
    """

    def read(self, **options: Any) -> pd.DataFrame:
        """Lê os dados da fonte e devolve um DataFrame pandas."""
        ...

    def write(self, df: pd.DataFrame, **options: Any) -> None:
        """Escreve um DataFrame pandas de volta na fonte."""
        ...


def build_data_source(config: Any) -> DataSource:
    """Devolve a implementação concreta de `DataSource` conforme o config.

    O `config` é um `DataSourceConfig` (ver `common/config.py`), com um campo `type`
    que seleciona a implementação. Os imports das implementações são feitos aqui
    dentro (lazy) para manter este contrato livre de dependências de plataforma.

    Tipos suportados: `parquet` (default local), `spark_table`, `sql`.
    """
    source_type = getattr(config, "type", None)

    if source_type == "parquet":
        from data.sources.parquet_source import ParquetSource

        return ParquetSource(config)
    if source_type == "spark_table":
        from data.sources.spark_table_source import SparkTableSource

        return SparkTableSource(config)
    if source_type == "sql":
        from data.sources.sql_source import SQLSource

        return SQLSource(config)

    raise ValueError(
        f"Tipo de fonte de dados desconhecido: {source_type!r}. "
        "Suportados: 'parquet', 'spark_table', 'sql'."
    )
