"""ParquetSource — fonte de dados local baseada em Parquet.

É o default local e funciona SEMPRE (pandas + pyarrow são dependências base do
núcleo). Sem dependência de plataforma.
"""

from __future__ import annotations

from typing import Any

import pandas as pd


class ParquetSource:
    """Lê/escreve Parquet a partir de um caminho vindo do config (Rule 07).

    Espera `config.path` (arquivo ou diretório Parquet).
    """

    def __init__(self, config: Any) -> None:
        path = getattr(config, "path", None)
        if not path:
            raise ValueError("ParquetSource requer 'path' no config da fonte de dados.")
        self.path = path

    def read(self, **options: Any) -> pd.DataFrame:
        return pd.read_parquet(self.path, **options)

    def write(self, df: pd.DataFrame, **options: Any) -> None:
        options.setdefault("index", False)
        df.to_parquet(self.path, **options)
