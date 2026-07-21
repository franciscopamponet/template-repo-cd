"""SparkTableSource — fonte de dados baseada em tabela Spark (ex.: Databricks).

Os imports de spark são LAZY (feitos dentro dos métodos), para que o repo importe
sem pyspark/databricks instalados (Rule 06 — plataforma opcional). Só quem realmente
usa esta fonte precisa do extra `spark`/`databricks`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd


class SparkTableSource:
    """Lê/escreve uma tabela Spark cujo nome vem do config (Rule 07).

    Espera `config.table` (nome qualificado da tabela). Opcionalmente
    `config.write_mode` (default: 'overwrite').
    """

    def __init__(self, config: Any) -> None:
        table = getattr(config, "table", None)
        if not table:
            raise ValueError("SparkTableSource requer 'table' no config da fonte de dados.")
        self.table = table
        self.write_mode = getattr(config, "write_mode", "overwrite")

    def _spark(self):
        # Import lazy: só carrega pyspark quando a fonte é de fato usada.
        from pyspark.sql import SparkSession

        return SparkSession.builder.getOrCreate()

    def read(self, **options: Any) -> pd.DataFrame:
        spark = self._spark()
        return spark.read.table(self.table).toPandas()

    def write(self, df: pd.DataFrame, **options: Any) -> None:
        spark = self._spark()
        mode = options.pop("mode", self.write_mode)
        spark_df = spark.createDataFrame(df)
        spark_df.write.mode(mode).saveAsTable(self.table)
