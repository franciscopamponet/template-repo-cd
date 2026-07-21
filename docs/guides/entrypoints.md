# Guia — pipeline/entrypoints/

## Propósito
Abrigar os **launchers finos** que disparam o pipeline. São casca de entrada: leem o
config, escolhem o modelo e chamam o `orchestrator.py`. O modo (local vs. serverless)
é definido pelo toggle no `tools/init.py`.

## Pode morar aqui
- Launchers finos por modo de execução (local / serverless).
- Parsing de argumentos de linha de comando que apenas repassa ao núcleo.

## Não pode morar aqui
- Lógica de pipeline (prepare/build/train/evaluate) — isso é `pipeline/models/`.
- Regra de negócio ou tracking direto de MLflow (Rule 01).
- Dependência que quebre com `platform/` inexistente quando o toggle for Não (Rule 06).

## O que já mora aqui

| arquivo | modo | quando existe |
| ------- | ---- | ------------- |
| [`run_local.py`](../../pipeline/entrypoints/run_local.py)         | execução local        | sempre |
| [`run_serverless.py`](../../pipeline/entrypoints/run_serverless.py) | plataforma/Databricks | só se toggle = Sim (o `init.py` poda se Não) |

Os dois são **idênticos em estrutura**: parseiam `--config` e chamam
`models.<modelo>.orchestrator.run(config)`. A diferença de plataforma **não** está aqui
— mora no config (`tracking.databricks`, `data_source.type`). Esse é o invariante
central: o núcleo chamado é o mesmo nos dois modos.

```python
# a espinha de qualquer entrypoint — nada além disto
resultado = run(args.config)
print(f"run_id: {resultado['run_id']}")
print(f"métricas: {resultado['metrics']}")
```

## Como eu invoco o pipeline

```bash
# local (toggle = Não, ou local mesmo com Databricks configurado):
uv run python pipeline/entrypoints/run_local.py --config pipeline/config/<modelo>.yaml

# na plataforma (toggle = Sim), o job aponta para:
python pipeline/entrypoints/run_serverless.py --config pipeline/config/<modelo>.yaml
```

Validado ponta a ponta nos dois toggles: ambos treinam, avaliam e logam via
`pipeline/common/tracking.py`, produzindo `run_id` + métricas.

## Como eu adiciono/ajusto um entrypoint

Raramente é preciso. Se um novo modo de execução surgir, mantenha o launcher **fino**:
só parsing + chamada ao `orchestrator`. Qualquer lógica real vai para `pipeline/models/` ou
`pipeline/common/`. O `import` do orchestrator do modelo é atualizado pelo `init.py` no rename,
ou à mão ao trocar de modelo.
