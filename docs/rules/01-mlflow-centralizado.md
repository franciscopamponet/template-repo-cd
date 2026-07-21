# Rule 01 — MLflow é centralizado

Só o `orchestrator.py` fala com MLflow, e sempre através de `pipeline/common/tracking.py`.

**Faça:** rotear todo logging de experimento pelo `orchestrator.py` → `pipeline/common/tracking.py`.
**Não faça:** `import mlflow` em `prepare_data.py`, `build_model.py`, `train.py`,
`evaluate_model.py`, em `pipeline/data/`, em `pipeline/config/` ou em qualquer outro lugar. Nenhum
arquivo além de `pipeline/common/tracking.py` importa mlflow diretamente.
