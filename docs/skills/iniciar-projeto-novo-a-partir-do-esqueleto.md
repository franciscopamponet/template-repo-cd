# Skill — Iniciar um projeto novo a partir do esqueleto

Do zero a um projeto rodando: copiar o esqueleto, rodar `tools/init.py` uma vez e dar
os primeiros passos. Distribuição por **cópia independente** (Decisão 0): não há
repo-mãe nem vínculo vivo com o esqueleto depois da cópia (evolução forward-only).

## 1. Copie o esqueleto
Copie a pasta do esqueleto para o diretório do novo projeto — uma cópia independente,
sem `.git` do esqueleto:
```bash
cp -r caminho/para/esqueleto meu-projeto-novo
cd meu-projeto-novo
rm -rf .git && git init        # o projeto novo é dono do próprio histórico
```

## 2. Rode o scaffolder UMA vez
```bash
python3 tools/init.py          # interativo (usa só a stdlib; roda antes do uv sync)
# ou não-interativo:
python3 tools/init.py --name "Previsão de Churn" --databricks no --model churn --yes
```
O `init.py` pergunta:
- **Nome do projeto** → vira o `name`/descrição do `pyproject`, título do README, etc.
- **Databricks? S/N** — o toggle (Decisão 1):
  - **Não** → remove `platform/`, `pipeline/entrypoints/run_serverless.py`, o extra `databricks`
    do pyproject e `tools/gen_conda.py`. As **cancelas** (`check_*.py`, `check.py`)
    **sobrevivem** — o CI é o mesmo com ou sem Databricks (ver decisão 7 em docs/context/decisoes.md).
  - **Sim** → mantém `platform/` e regenera o `conda.yaml` em sync (Rule 03).
- **Nome do primeiro modelo** (snake_case) → renomeia `pipeline/models/exemplo_modelo/` e
  `pipeline/config/exemplo_modelo.yaml` para esse nome, atualizando todas as referências.

Ao terminar, o script **se autodestrói** (`tools/init.py` some) — ele só faz sentido
uma vez. Rodar de novo é barrado por uma checagem de pré-voo.

## 3. Instale as dependências
```bash
uv sync
```
Instala o núcleo (sem extras de plataforma por default — Rule 06).

## 4. Primeiros passos
```bash
# edite o config do seu modelo (fonte de dados, params) — Rule 07:
$EDITOR pipeline/config/<modelo>.yaml

# gere/aponte para o dado que o config espera, então rode ponta a ponta:
uv run python pipeline/entrypoints/run_local.py --config pipeline/config/<modelo>.yaml
# saída esperada: run_id: ... / métricas: {'accuracy': ..., 'f1': ...}

# valide o repo inteiro antes do primeiro commit:
uv run pytest
python3 tools/check.py
```

Se o toggle foi **Sim**, ainda preencha os `<PREENCHER: ...>` em
`platform/databricks.yml` e `platform/resources/` e valide o bundle:
```bash
databricks bundle validate -t dev
```

## 5. Antes de mexer em qualquer coisa
Leia `docs/rules/` (obrigatório) e o guia da camada que você vai tocar em
`docs/guides/`. Para tarefas comuns, há skills irmãs:
[`adicionar-novo-modelo.md`](adicionar-novo-modelo.md),
[`adicionar-nova-fonte-de-dados.md`](adicionar-nova-fonte-de-dados.md),
[`adicionar-dependencia.md`](adicionar-dependencia.md).

## Validação
Este fluxo foi exercido ponta a ponta nos dois toggles (Sim e Não): init → uv sync →
pipeline treinando e logando via MLflow, com a suíte e as cancelas verdes nas duas
cópias.
