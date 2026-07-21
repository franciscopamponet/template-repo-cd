# Guia — platform/

## Propósito
Abrigar a casca **opcional** de Databricks. Só sobrevive se o toggle for SIM; o
`tools/init.py` poda a pasta inteira se for Não (Rule 06). O núcleo é idêntico com ou
sem ela.

## Pode morar aqui
- `databricks.yml`, `resources/`, `MLProject`.
- `conda.yaml` — **gerado** a partir do `pyproject.toml`, nunca escrito à mão (Rule 02, 03).

## Não pode morar aqui
- Qualquer coisa que o núcleo importe (o núcleo nunca depende de `platform/` — Rule 06).
- `conda.yaml`/requirements editados manualmente.

## O que já mora aqui

| arquivo | papel |
| ------- | ----- |
| [`databricks.yml`](../../platform/databricks.yml) | Databricks Asset Bundle: `targets` (dev/prod), `variables`, host do workspace. Traz placeholders `<PREENCHER: ...>`. |
| [`resources/treino_<modelo>.yml`](../../platform/resources/) | job serverless de treino; aponta para `pipeline/entrypoints/run_serverless.py` e passa só o `--config` (Rule 07). |
| [`MLProject`](../../platform/MLProject) | manifesto MLflow Project (`mlflow run . -e treino -P config=...`); ambiente vem do `conda.yaml`. |
| `conda.yaml` | **gerado** por `tools/gen_conda.py` a partir do `pyproject.toml`. Cabeçalho "ARQUIVO GERADO — NÃO EDITE". |

## Como o `conda.yaml` é derivado (e por que nunca à mão)

`pyproject.toml` é a fonte única (Rule 02). `tools/gen_conda.py` lê as `dependencies`
base do projeto e escreve o `conda.yaml` de forma **determinística** (mesma entrada,
mesma saída byte a byte). Os extras `databricks`/`spark` ficam **de fora** de propósito:
o runtime do Databricks já fornece o Spark, e `databricks-connect` serve para conectar
de fora, não para rodar dentro do cluster.

```bash
uv run python tools/gen_conda.py           # regera
uv run python tools/gen_conda.py --check    # CI: falha se estiver defasado (Rule 03)
```

A cancela `tools/check_manifest.py` refaz essa checagem no CI e **pula** quando
`platform/` não existe (toggle = Não) — o CI é o mesmo com ou sem Databricks
(ver a decisão 7 em [decisoes.md](../context/decisoes.md)).

## Como eu mexo aqui

- **Mudou dependência?** Nunca edite o `conda.yaml`. Edite o `pyproject.toml`, rode
  `gen_conda.py` e commite os dois juntos — ver a skill
  [`adicionar-dependencia.md`](../skills/adicionar-dependencia.md).
- **Deploy do bundle?** Preencha os `<PREENCHER: ...>` em `databricks.yml` e
  `resources/`, então:
  ```bash
  databricks bundle validate -t dev
  databricks bundle deploy -t dev
  databricks bundle run treino_<modelo> -t dev
  ```
- **Novo modelo com job próprio?** Copie `resources/treino_<modelo>.yml`, renomeie
  batendo com o modelo (Rule 05) e ajuste o `--config`.

> Toggle = Não: nada disto existe no projeto, e o núcleo roda igual. Não importe de
> `platform/` a partir de `pipeline/config/`, `pipeline/data/`, `pipeline/models/`, `pipeline/common/` ou `pipeline/entrypoints/`.
