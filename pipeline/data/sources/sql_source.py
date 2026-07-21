"""SQLSource — fonte de dados baseada em banco relacional via SQLAlchemy.

Os imports de sqlalchemy são LAZY (feitos dentro dos métodos), para que o repo
importe sem sqlalchemy disponível como dependência do núcleo (Rule 06). Quem usa
esta fonte instala o driver/engine apropriado.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd


class SQLSource:
    """Lê/escreve via SQL, com conexão e query/tabela vindas do config (Rule 07).

    Espera `config.connection` (URL SQLAlchemy). Para leitura, `config.query` OU
    `config.table`. Para escrita, `config.table`.
    """

    def __init__(self, config: Any) -> None:
        connection = getattr(config, "connection", None)
        if not connection:
            raise ValueError("SQLSource requer 'connection' (URL SQLAlchemy) no config.")
        self.connection = connection
        self.query = getattr(config, "query", None)
        self.table = getattr(config, "table", None)

    def _engine(self):
        # Import lazy: só carrega sqlalchemy quando a fonte é de fato usada.
        from sqlalchemy import create_engine

        return create_engine(self.connection)

    def read(self, **options: Any) -> pd.DataFrame:
        import pandas as pd

        if not self.query and not self.table:
            raise ValueError("SQLSource.read requer 'query' ou 'table' no config.")
        engine = self._engine()
        with engine.connect() as conn:
            if self.query:
                return pd.read_sql_query(self.query, conn, **options)
            return pd.read_sql_table(self.table, conn, **options)

    def write(self, df: pd.DataFrame, **options: Any) -> None:
        if not self.table:
            raise ValueError("SQLSource.write requer 'table' no config.")
        options.setdefault("if_exists", "replace")
        options.setdefault("index", False)
        engine = self._engine()
        with engine.connect() as conn:
            df.to_sql(self.table, conn, **options)
