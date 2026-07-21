# Guia — pipeline/models/

## Propósito
Abrigar cada modelo em `pipeline/models/<nome>/`, seguindo a **anatomia de 5 arquivos**
(Rule 00). É o coração do núcleo do pipeline.

## Pode morar aqui
- Uma pasta por modelo, em `snake_case`, com **exatamente** os 5 arquivos:
  `prepare_data.py`, `build_model.py`, `train.py`, `evaluate_model.py`,
  `orchestrator.py`.
- Lógica específica daquele modelo.

## Não pode morar aqui
- Um 6º arquivo, renomeações ou fusões dos 5 (Rule 00).
- `import mlflow` fora do fluxo `orchestrator.py` → `pipeline/common/tracking.py` (Rule 01).
- Lógica compartilhada entre modelos (isso é `pipeline/common/`).
- Caminhos/hiperparâmetros hardcoded (Rule 07).

## O contrato entre os 5 arquivos

Referência real: [`pipeline/models/exemplo_modelo/`](../../pipeline/models/exemplo_modelo/). Cada arquivo
tem um papel e um contrato de entrada/saída fixo:

| # | arquivo             | recebe                         | devolve                     | pode falar com MLflow? |
| - | ------------------- | ------------------------------ | --------------------------- | ---------------------- |
| 1 | `prepare_data.py`   | `DataSource`, `params`         | `PreparedData` (NamedTuple) | não |
| 2 | `build_model.py`    | `params`                       | estimador **não** treinado  | não |
| 3 | `train.py`          | estimador, `x_train`, `y_train`| estimador treinado          | não |
| 4 | `evaluate_model.py` | estimador, `x_test`, `y_test`  | `dict[str, float]` métricas | não |
| 5 | `orchestrator.py`   | `config_path`                  | `dict` (metrics/run_id/params) | **sim, e só ele** |

`PreparedData` (definido em `prepare_data.py`) carrega `x_train, x_test, y_train,
y_test, feature_names`. Os 4 primeiros arquivos são puros: sem I/O de tracking, sem
`import mlflow`. O `orchestrator` é a espinha dorsal — ele carrega o config, constrói a
fonte de dados, chama os 4 na ordem e loga tudo via `pipeline/common/tracking.py` (Rule 01):

```python
config = load_config(config_path)
source = build_data_source(config.data_source)
prepared = prepare_data(source, config.params)
model = build_model(config.params)
tracker = Tracker(config.tracking)
with tracker.start_run(run_name=config.name):
    tracker.log_params({...})
    trained = train(model, prepared.x_train, prepared.y_train)
    metrics = evaluate_model(trained, prepared.x_test, prepared.y_test)
    tracker.log_metrics(metrics)
    tracker.log_model(trained, "model")
```

## Como eu adiciono um novo modelo

Ver a skill [`adicionar-novo-modelo.md`](../skills/adicionar-novo-modelo.md) para o
passo a passo. Em resumo: copie `pipeline/models/exemplo_modelo/` para `pipeline/models/<novo>/`, crie
`pipeline/config/<novo>.yaml` com o mesmo nome (Rule 05), atualize os imports internos (o
`orchestrator` importa `models.<novo>.prepare_data` etc.) e mantenha os 5 arquivos —
nem mais, nem menos. Lógica que serviria a vários modelos vai para `pipeline/common/`, não para
um 6º arquivo.
