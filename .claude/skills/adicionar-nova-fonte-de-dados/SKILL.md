---
name: adicionar-nova-fonte-de-dados
description: Use quando o usuário quer adicionar uma NOVA FONTE DE DADOS (um DataSource — ler/escrever de um novo formato ou origem, ex.: Excel, API, outro banco) sem tocar no núcleo do pipeline.
---

# Adicionar uma nova fonte de dados

Como implementar um novo `DataSource` sem tocar no núcleo (Decisão 3 / Rule 06).
Referência viva: `pipeline/data/sources/parquet_source.py` (a mais simples).

## O contrato
Uma fonte é qualquer classe com dois métodos (é um `Protocol`, não precisa herdar nada):

```python
def read(self, **options) -> pd.DataFrame: ...
def write(self, df: pd.DataFrame, **options) -> None: ...
```

Definido em `pipeline/common/data_source.py`. O pipeline chama `source.read()` e nunca sabe qual
implementação está por trás.

## Passos

1. **Crie `pipeline/data/sources/<nome>_source.py`** com a classe. Leia toda configuração de
   `config` via `getattr` — nada de caminho/credencial no código (Rule 07):
   ```python
   class MinhaFonte:
       def __init__(self, config):
           self.endpoint = getattr(config, "endpoint", None)
           if not self.endpoint:
               raise ValueError("MinhaFonte requer 'endpoint' no config da fonte.")

       def read(self, **options):
           import biblioteca_pesada  # LAZY: só carrega quando a fonte é usada (Rule 06)
           ...
           return df  # pandas

       def write(self, df, **options):
           ...
   ```

2. **Imports pesados são LAZY** — dentro dos métodos, nunca no topo do módulo. É o que
   permite o repo importar sem a dependência instalada (Rule 06). Veja
   `SparkTableSource`/`SQLSource` como modelo.

3. **Registre o tipo na factory** `build_data_source` em `pipeline/common/data_source.py`:
   ```python
   if source_type == "minha_fonte":
       from data.sources.minha_fonte_source import MinhaFonte
       return MinhaFonte(config)
   ```

4. **Adicione o tipo ao schema** `DataSourceConfig.type` em `pipeline/common/config.py`:
   ```python
   type: Literal["parquet", "spark_table", "sql", "minha_fonte"] = "parquet"
   ```
   (Campos extras da fonte já são aceitos — `DataSourceConfig` usa `extra="allow"`.)

5. **Se precisar de uma dependência nova**, adicione-a como extra opcional no
   `pyproject.toml` (não no núcleo, para não pesar quem não usa a fonte) e siga a skill
   [adicionar-dependencia](../adicionar-dependencia/SKILL.md).

6. **Use pelo config**, sem tocar em `prepare_data` nem no `orchestrator`:
   ```yaml
   data_source:
     type: minha_fonte
     endpoint: ...
   ```

## Checklist de saída
- [ ] A classe implementa `read`/`write` devolvendo/recebendo `pd.DataFrame`.
- [ ] Imports pesados são lazy (repo importa sem a dependência) — Rule 06.
- [ ] `type` registrado na factory **e** no `Literal` de `DataSourceConfig`.
- [ ] `prepare_data.py` e `orchestrator.py` **não** foram alterados.
- [ ] `python3 tools/check.py` verde.
