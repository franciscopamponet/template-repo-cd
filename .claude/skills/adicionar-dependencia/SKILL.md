---
name: adicionar-dependencia
description: Use quando o usuário quer adicionar ou remover uma DEPENDÊNCIA do projeto. Conduz o fluxo pyproject → uv lock → regerar conda → CI, mantendo o manifesto em sync (Rules 02 e 03).
---

# Adicionar uma dependência

`pyproject.toml` é a **fonte única** de dependências (Rule 02). `conda.yaml` e qualquer
requirements são **derivados** dele, nunca escritos à mão (Rule 03). Esta skill mantém
tudo em sync e o CI verde.

## Fluxo: pyproject → uv lock → regerar conda → CI

1. **Adicione via `uv`** (ele edita o `pyproject.toml` e atualiza o `uv.lock`):
   ```bash
   uv add nome-do-pacote            # dependência base do núcleo
   uv add --optional spark pyspark  # extra opcional (não entra no núcleo)
   uv add --dev pytest-cov          # ferramenta de desenvolvimento
   ```
   Nunca edite o `conda.yaml` nem crie um `requirements.txt` à mão — isso recria o bug
   de divergência que a Rule 02 existe para matar.

2. **Regenere o manifesto de plataforma** (só se `platform/` existe, i.e. toggle = Sim):
   ```bash
   uv run python tools/gen_conda.py
   ```
   Isso reescreve `platform/conda.yaml` a partir do novo `pyproject.toml`, de forma
   determinística. Os extras `databricks`/`spark` **não** entram no conda de propósito
   (o runtime Databricks já os fornece).

3. **Rode as cancelas** para provar que está tudo em sync antes de commitar:
   ```bash
   python3 tools/check.py
   ```
   A etapa "manifesto em sync" (`tools/check_manifest.py`) falha se o `conda.yaml`
   estiver defasado do `pyproject.toml` (Rule 03).

4. **Commite os arquivos JUNTOS** — nunca o `pyproject.toml` sozinho:
   ```bash
   git add pyproject.toml uv.lock platform/conda.yaml
   git commit -m "deps: adiciona <pacote>"
   ```
   O CI (`.github/workflows/ci.yml`) refaz a checagem de sync; um `pyproject` alterado
   com `conda.yaml` defasado é falha de CI.

## Onde cada dependência entra
- **Núcleo** (`dependencies`): só o que todo projeto precisa sempre. Pesa em todo mundo.
- **Extra opcional** (`optional-dependencies`, ex.: `spark`, `databricks`): dependência
  de uma fonte/plataforma específica. Fica de fora do `uv sync` default (Rule 06).
- **Dev** (`dependency-groups.dev`): ferramentas de build/teste (ruff, pytest).

## Checklist de saída
- [ ] Dependência adicionada só no `pyproject.toml` (via `uv`), nunca à mão no conda.
- [ ] `uv.lock` atualizado.
- [ ] `platform/conda.yaml` regerado (se toggle = Sim).
- [ ] `python3 tools/check.py` verde (inclui "manifesto em sync").
- [ ] `pyproject.toml` + `uv.lock` + `conda.yaml` no mesmo commit.
