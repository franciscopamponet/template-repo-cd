"""Carregamento e validação de config (Rule 07 — pipeline config-driven).

Todo caminho, tabela, hiperparâmetro e nome de recurso vem daqui. Nada de valores
hardcoded no código do pipeline. O config é YAML, validado com pydantic.

Cada modelo estende `BaseModelConfig` com seus próprios hiperparâmetros, e carrega o
YAML com `load_config(caminho, SchemaDoModelo)`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, TypeVar

import yaml
from pydantic import BaseModel, ConfigDict, Field


class DataSourceConfig(BaseModel):
    """Config da fonte de dados. O campo `type` seleciona a implementação concreta.

    Campos extras são permitidos e repassados à implementação (ex.: `path` para
    parquet, `table` para spark, `query`/`connection` para sql).
    """

    model_config = ConfigDict(extra="allow")

    type: Literal["parquet", "spark_table", "sql"] = "parquet"


class TrackingConfig(BaseModel):
    """Config de tracking do MLflow (consumido apenas por `common/tracking.py`).

    `databricks=False` (default) → tracking local no `tracking_uri`, experimento por
    nome simples. O default é um backend SQLite: o file store (`./mlruns`) não é mais
    suportado pelo MLflow e o SQLite habilita o Model Registry local.
    `databricks=True` → modo Databricks (ver TODO em `common/tracking.py`; ainda não
    validado empiricamente).
    """

    experiment_name: str
    databricks: bool = False
    tracking_uri: str = "sqlite:///mlflow.db"
    registry_uri: str | None = None


class BaseModelConfig(BaseModel):
    """Schema base que todo modelo estende.

    Contém o comum a qualquer modelo: nome, fonte de dados, tracking e caminhos de
    saída. Hiperparâmetros específicos entram em `params` (ou num subschema próprio
    do modelo que herda desta classe).
    """

    model_config = ConfigDict(extra="forbid")

    name: str
    data_source: DataSourceConfig
    tracking: TrackingConfig
    output_dir: str = "data/processed"
    params: dict[str, Any] = Field(default_factory=dict)


ConfigT = TypeVar("ConfigT", bound=BaseModel)


def load_config(path: str | Path, schema: type[ConfigT] = BaseModelConfig) -> ConfigT:
    """Carrega um YAML e valida contra `schema` (default: `BaseModelConfig`).

    Levanta `FileNotFoundError` se o caminho não existir e `pydantic.ValidationError`
    se o conteúdo violar o schema.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config não encontrado: {path}")

    with path.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}

    return schema.model_validate(raw)
