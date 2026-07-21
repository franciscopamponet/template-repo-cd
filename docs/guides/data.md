# Guia — pipeline/data/

## Propósito
Abrigar as **implementações concretas** da interface de dados neutra `DataSource`
(definida em `pipeline/common/`). É a camada que sabe DE ONDE o dado vem; o resto do pipeline não.

## Pode morar aqui
- `pipeline/data/sources/` com implementações concretas: `ParquetSource`, `SparkTableSource`,
  `SQLSource`, etc., cada uma cumprindo o `Protocol` `DataSource`.
- Adaptadores de leitura/escrita específicos de uma origem.

## Não pode morar aqui
- A definição do `Protocol` `DataSource` (isso mora em `pipeline/common/`).
- Lógica de modelo (isso é `pipeline/models/`).
- Caminhos/tabelas hardcoded — eles vêm do config (Rule 07).

## Como funciona de verdade

O contrato está em [`pipeline/common/data_source.py`](../../pipeline/common/data_source.py):

```python
@runtime_checkable
class DataSource(Protocol):
    def read(self, **options) -> pd.DataFrame: ...
    def write(self, df: pd.DataFrame, **options) -> None: ...
```

A factory `build_data_source(config)` no mesmo arquivo recebe o `DataSourceConfig` e
devolve a implementação certa conforme `config.type`. Os imports concretos são **lazy**
(feitos dentro da factory / dos métodos), para o repo importar sem pyspark/sqlalchemy
instalados — Rule 06.

Implementações que já existem em [`pipeline/data/sources/`](../../pipeline/data/sources/):

| `type`         | classe             | dependência       | precisa de config |
| -------------- | ------------------ | ----------------- | ----------------- |
| `parquet`      | `ParquetSource`    | pandas+pyarrow (núcleo) | `path` |
| `spark_table`  | `SparkTableSource` | extra `spark`/`databricks` | `table`, `write_mode?` |
| `sql`          | `SQLSource`        | sqlalchemy + driver | `connection`, `query`/`table` |

`prepare_data` só chama `source.read()` — nunca sabe qual das três está por trás.

## Como eu adiciono uma nova fonte de dados

Ver a skill [`adicionar-nova-fonte-de-dados.md`](../skills/adicionar-nova-fonte-de-dados.md)
para o passo a passo completo. Em resumo:

1. Crie `pipeline/data/sources/<nome>_source.py` com uma classe que implemente `read`/`write`
   (não precisa herdar de nada — é um `Protocol`; basta ter os métodos).
2. Imports pesados **lazy**, dentro dos métodos (Rule 06).
3. Registre o novo `type` na factory `build_data_source` (um `if` + import lazy) e no
   `Literal` de `DataSourceConfig.type` em `pipeline/common/config.py`.
4. Nada de caminho/credencial no código: tudo vem de `getattr(config, ...)` (Rule 07).

O núcleo (`prepare_data`, `orchestrator`) **não muda** — é esse o ponto da interface neutra.
