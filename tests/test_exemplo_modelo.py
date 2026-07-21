"""Testes do modelo de referência: as 5 etapas e o fluxo do orchestrator.

Cobre também os contratos estruturais: a anatomia de 5 arquivos (Rule 00) e o
isolamento do MLflow (Rule 01).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from sklearn.ensemble import RandomForestClassifier

from common.config import load_config
from common.data_source import build_data_source
from models.exemplo_modelo.build_model import build_model
from models.exemplo_modelo.evaluate_model import evaluate_model
from models.exemplo_modelo.orchestrator import run
from models.exemplo_modelo.prepare_data import prepare_data
from models.exemplo_modelo.train import train

MODELO_DIR = Path("pipeline/models/exemplo_modelo")
ANATOMIA = {
    "prepare_data.py",
    "build_model.py",
    "train.py",
    "evaluate_model.py",
    "orchestrator.py",
}


# --------------------------------------------------------------------------
# Contratos estruturais
# --------------------------------------------------------------------------


def test_anatomia_de_5_arquivos_exata():
    """Rule 00: exatamente os 5 arquivos, nem mais nem menos."""
    encontrados = {p.name for p in MODELO_DIR.iterdir() if p.is_file()}
    assert encontrados == ANATOMIA


def test_apenas_orchestrator_fala_com_tracking():
    """Rule 01: nenhum dos outros 4 arquivos importa mlflow ou tracking."""
    for nome in ANATOMIA - {"orchestrator.py"}:
        texto = (MODELO_DIR / nome).read_text(encoding="utf-8")
        assert "import mlflow" not in texto, f"{nome} importa mlflow"
        assert "common.tracking" not in texto, f"{nome} fala com tracking"


# --------------------------------------------------------------------------
# Etapas isoladas
# --------------------------------------------------------------------------


def test_prepare_data_divide_e_seleciona(config_sintetico):
    cfg = load_config(config_sintetico)
    source = build_data_source(cfg.data_source)
    prepared = prepare_data(source, cfg.params)

    assert list(prepared.feature_names) == ["x1", "x2", "x3"]
    assert len(prepared.x_train) == 150
    assert len(prepared.x_test) == 50
    assert "y" not in prepared.x_train.columns
    assert len(prepared.y_train) == 150


def test_prepare_data_exige_target(config_sintetico):
    cfg = load_config(config_sintetico)
    source = build_data_source(cfg.data_source)
    with pytest.raises(ValueError, match="target"):
        prepare_data(source, {})


def test_prepare_data_rejeita_target_inexistente(config_sintetico):
    cfg = load_config(config_sintetico)
    source = build_data_source(cfg.data_source)
    with pytest.raises(ValueError, match="não existe"):
        prepare_data(source, {"target": "inexistente"})


def test_build_model_usa_hiperparametros_do_config():
    model = build_model({"n_estimators": 7, "max_depth": 3, "random_state": 1})
    assert isinstance(model, RandomForestClassifier)
    assert model.n_estimators == 7
    assert model.max_depth == 3


def test_train_devolve_modelo_ajustado(config_sintetico):
    cfg = load_config(config_sintetico)
    source = build_data_source(cfg.data_source)
    prepared = prepare_data(source, cfg.params)
    model = build_model(cfg.params)

    treinado = train(model, prepared.x_train, prepared.y_train)
    # Um estimador sklearn só tem classes_ depois do fit.
    assert hasattr(treinado, "classes_")


def test_evaluate_model_devolve_metricas(config_sintetico):
    cfg = load_config(config_sintetico)
    source = build_data_source(cfg.data_source)
    prepared = prepare_data(source, cfg.params)
    treinado = train(build_model(cfg.params), prepared.x_train, prepared.y_train)

    metrics = evaluate_model(treinado, prepared.x_test, prepared.y_test)
    assert set(metrics) == {"accuracy", "f1", "precision", "recall"}
    assert all(0.0 <= v <= 1.0 for v in metrics.values())
    # O dado sintético tem sinal claro; um modelo funcional supera o acaso.
    assert metrics["accuracy"] > 0.7


# --------------------------------------------------------------------------
# Fluxo ponta a ponta
# --------------------------------------------------------------------------


def test_orchestrator_ponta_a_ponta(config_sintetico):
    resultado = run(config_sintetico)

    assert set(resultado) == {"metrics", "run_id", "params"}
    assert resultado["run_id"], "o orchestrator deve registrar um run no tracking"
    assert resultado["metrics"]["accuracy"] > 0.7
    assert resultado["params"]["target"] == "y"
