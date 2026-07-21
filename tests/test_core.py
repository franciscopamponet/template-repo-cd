"""Testes do núcleo neutro: config, DataSource, splits.

Importante: importar `data.sources.spark_table_source` NÃO pode exigir pyspark
instalado (Rule 06 — imports de plataforma são lazy).
"""

from __future__ import annotations

import importlib

import pandas as pd
import pytest

from common.config import BaseModelConfig, TrackingConfig, load_config
from common.data_source import DataSource, build_data_source
from common.splits import random_split, temporal_split


def test_load_config_valida_exemplo():
    cfg = load_config("pipeline/config/exemplo_modelo.yaml")
    assert isinstance(cfg, BaseModelConfig)
    assert cfg.name == "exemplo_modelo"
    assert cfg.data_source.type == "parquet"
    assert cfg.tracking.experiment_name
    # Nada de asserção sobre `tracking.databricks` aqui: o valor depende do toggle
    # escolhido no init, e este teste viaja para a cópia (Decisão 1).
    # File store ('./mlruns') não é mais suportado pelo MLflow; o default é SQLite.
    assert cfg.tracking.tracking_uri.startswith("sqlite:///")


def test_tracking_local_e_o_default_do_schema():
    """O default do schema é local, independente do que o config de exemplo diga."""
    cfg = TrackingConfig(experiment_name="x")
    assert cfg.databricks is False
    assert cfg.tracking_uri.startswith("sqlite:///")


def test_load_config_arquivo_inexistente():
    with pytest.raises(FileNotFoundError):
        load_config("pipeline/config/nao_existe.yaml")


def test_parquet_source_roundtrip(tmp_path):
    cfg = BaseModelConfig.model_validate(
        {
            "name": "m",
            "data_source": {"type": "parquet", "path": str(tmp_path / "d.parquet")},
            "tracking": {"experiment_name": "m"},
        }
    )
    source = build_data_source(cfg.data_source)
    assert isinstance(source, DataSource)

    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    source.write(df)
    out = source.read()
    pd.testing.assert_frame_equal(out, df)


def test_factory_tipo_desconhecido():
    with pytest.raises(ValueError, match="desconhecido"):
        build_data_source(type("C", (), {"type": "foo"})())


def test_spark_source_importa_sem_pyspark():
    # O módulo importa mesmo sem pyspark; a dependência só é exigida no uso.
    mod = importlib.import_module("data.sources.spark_table_source")
    assert hasattr(mod, "SparkTableSource")


def test_random_split_estratificado():
    df = pd.DataFrame({"x": range(100), "y": [0, 1] * 50})
    train, test = random_split(df, test_size=0.25, random_state=1, stratify_col="y")
    assert len(test) == 25
    assert len(train) == 75


def test_temporal_split_por_cutoff():
    df = pd.DataFrame(
        {
            "t": pd.to_datetime(["2024-01-01", "2024-02-01", "2024-03-01", "2024-04-01"]),
            "v": [1, 2, 3, 4],
        }
    )
    train, test = temporal_split(df, "t", cutoff="2024-03-01")
    assert list(train["v"]) == [1, 2]
    assert list(test["v"]) == [3, 4]


def test_temporal_split_por_fracao_preserva_ordem():
    df = pd.DataFrame({"t": [3, 1, 2, 5, 4], "v": [30, 10, 20, 50, 40]})
    train, test = temporal_split(df, "t", test_size=0.4)
    assert list(train["t"]) == [1, 2, 3]
    assert list(test["t"]) == [4, 5]


def test_temporal_split_exige_um_modo():
    df = pd.DataFrame({"t": [1, 2], "v": [1, 2]})
    with pytest.raises(ValueError):
        temporal_split(df, "t")
    with pytest.raises(ValueError):
        temporal_split(df, "t", cutoff="2024-01-01", test_size=0.5)
