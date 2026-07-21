# Guia — pipeline/config/

## Propósito
Guardar a configuração por modelo que dirige o pipeline. Caminhos, tabelas,
hiperparâmetros, escolha de `DataSource` e nomes de experimento moram aqui — não no
código (ver Rule 07).

## Pode morar aqui
- Um arquivo YAML por modelo, com nome batendo com o modelo (`pipeline/config/<nome>.yaml` ↔
  `pipeline/models/<nome>/`) — ver Rule 05.
- Valores de ambiente/execução que o pipeline lê em tempo de rodada.

## Não pode morar aqui
- Lógica Python de pipeline (isso é `pipeline/models/` / `pipeline/common/`).
- Segredos/credenciais versionados.

## Como funciona de verdade

O formato é **YAML**, validado com **pydantic** em [`pipeline/common/config.py`](../../pipeline/common/config.py).
Três schemas compõem o config de um modelo:

- `DataSourceConfig` — `type: parquet | spark_table | sql` + campos livres repassados à
  implementação (`extra="allow"`, ex.: `path`, `table`, `connection`, `query`).
- `TrackingConfig` — `experiment_name`, `databricks` (bool), `tracking_uri`
  (default `sqlite:///mlflow.db`), `registry_uri`. Consumido **só** por
  `pipeline/common/tracking.py` (Rule 01).
- `BaseModelConfig` — o schema raiz (`extra="forbid"`): `name`, `data_source`,
  `tracking`, `output_dir`, `params` (dict livre de hiperparâmetros).

O núcleo carrega assim:

```python
from common.config import BaseModelConfig, load_config

config = load_config("pipeline/config/meu_modelo.yaml")          # valida contra BaseModelConfig
# FileNotFoundError se o caminho não existe; ValidationError se o YAML viola o schema
```

O template comentado de referência é [`pipeline/config/exemplo_modelo.yaml`](../../pipeline/config/exemplo_modelo.yaml).

## Como eu adiciono um config aqui

1. Copie `pipeline/config/exemplo_modelo.yaml` para `pipeline/config/<nome>.yaml` (nome = pasta do
   modelo, Rule 05).
2. Ajuste `name`, `data_source` (tipo + campos), `tracking.experiment_name` e `params`.
3. Nada de valor fixo no `.py`: se o modelo precisa de um novo hiperparâmetro, ele
   entra em `params:` e o código o lê com `params.get("...")` (Rule 07).

## Como eu adiciono um campo NOVO ao schema

`params` é um dict livre — a maioria dos hiperparâmetros **não** exige mudar o schema.
Só estenda o schema quando quiser **validação forte** de um campo. Nesse caso, crie um
subschema no próprio modelo e passe-o ao loader:

```python
# em pipeline/models/<nome>/orchestrator.py
from common.config import BaseModelConfig, load_config
from pydantic import BaseModel

class MeuModeloConfig(BaseModelConfig):
    limiar: float = 0.5     # agora validado (tipo, default)

config = load_config(path, MeuModeloConfig)
```

Não edite `BaseModelConfig` para necessidade de um único modelo — isso é
`pipeline/common/` só quando serve a mais de um modelo.
