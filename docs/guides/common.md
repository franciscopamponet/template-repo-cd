# Guia — pipeline/common/

## Propósito
Abrigar a lógica compartilhada entre modelos: contratos, tracking e splits. É onde mora
o que todos os modelos reutilizam.

## Pode morar aqui
- O `Protocol` `DataSource` (definição da interface neutra de dados).
- `tracking.py` — **único** módulo que fala com MLflow (Rule 01).
- Utilidades de split, contratos e helpers usados por mais de um modelo.

## Não pode morar aqui
- Lógica específica de um único modelo (isso é `pipeline/models/<nome>/`).
- Implementações concretas de fonte de dados (isso é `pipeline/data/sources/`).
- Import de `platform/` (Rule 06).

## O que já mora aqui

| arquivo             | o que expõe |
| ------------------- | ----------- |
| [`config.py`](../../pipeline/common/config.py)         | `BaseModelConfig`, `DataSourceConfig`, `TrackingConfig`, `load_config()` |
| [`data_source.py`](../../pipeline/common/data_source.py) | `Protocol DataSource` (contrato) + `build_data_source()` (factory) |
| [`tracking.py`](../../pipeline/common/tracking.py)       | `Tracker` — o **único** wrapper de MLflow do repo (Rule 01) |
| [`splits.py`](../../pipeline/common/splits.py)           | `random_split()`, `temporal_split()` |

### `Tracker` (o ponto único de MLflow)
`import mlflow` acontece **só** aqui (Rule 01 — verificado por `tools/check_mlflow.py`).
API: `start_run()` (contextmanager), `log_params`, `log_metrics`, `log_model`
(flavor sklearn por default). O default local é backend **SQLite**
(`sqlite:///mlflow.db`) — o file store `./mlruns` foi descontinuado pelo MLflow 3.x.
Validado empiricamente no MLflow 3.14.0 fora do Databricks (ver nota no topo do
arquivo). O caminho `databricks: true` deixa o tracking_uri a cargo do ambiente
Databricks e **ainda não foi validado em workspace real**.

### `splits`
`random_split` (com estratificação opcional) e `temporal_split` (por `cutoff` de data
**ou** por fração final ordenada no tempo — nunca embaralha, para não vazar o futuro).
A mecânica mora aqui; os parâmetros vêm do config (Rule 07).

## Como eu adiciono um utilitário compartilhado

1. Confirme que serve a **mais de um modelo**. Se é de um só, o lugar é
   `pipeline/models/<nome>/`, não aqui.
2. Crie/edite o módulo em `pipeline/common/` (ex.: `pipeline/common/features.py` para encoders reusáveis).
3. **Nunca** `import mlflow` (só `tracking.py` pode) nem `import platform`/
   `from platform...` (Rule 06) — as cancelas `check_mlflow.py`/`check_platform.py`
   barram no CI.
4. Se o utilitário for parte de um contrato entre etapas, documente o formato de
   entrada/saída como fez `PreparedData`.
