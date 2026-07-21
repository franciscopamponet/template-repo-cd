# O que é este projeto

Este é o **esqueleto (boilerplate) canônico** para projetos de Ciência de Dados do
núcleo de dados da PoliJúnior. Ele NÃO é um projeto real: é o molde a partir do qual
cada projeto real nasce.

## Para que serve

Padronizar como um projeto de ciência de dados é estruturado, executado e evoluído,
de modo que qualquer pessoa (ou IA) que clone uma cópia dele entenda e siga o padrão
**sozinha**, sem depender de conhecimento externo.

## Princípio-guia: conhecimento nativo, separado por natureza

Toda a inteligência de execução viaja DENTRO do repo, versionada. Se algo depende de
conhecimento externo (a cabeça de uma pessoa, um vault pessoal, um doc no Drive) para
funcionar, está errado. O conhecimento é separado pela sua natureza (decisão 8):

- **`docs/`** — o manual do **molde**: contexto, rules, guias, skills e decisões do
  esqueleto. Igual em todo projeto. É onde você está agora.
- **`.claude/`** — o contexto do **projeto** específico (negócio, dados, domínio),
  preenchido ao longo da cópia. Começa em branco.

## Como se usa

1. **Copie** este esqueleto para um novo diretório (cópia independente — ver
   [decisoes.md](decisoes.md), decisão 0). Não há repo-mãe hospedando N projetos.
2. **Rode `tools/init.py` uma única vez.** Ele pergunta o toggle Databricks (S/N),
   poda a pasta `platform/` se Não, define o modo dos `pipeline/entrypoints/` e nomeia o projeto.
3. **Comece a trabalhar** dentro da estrutura já pronta: config por modelo em `pipeline/config/`,
   modelos em `pipeline/models/<nome>/` (anatomia de 5 arquivos), lógica compartilhada em `pipeline/common/`.

Passo a passo detalhado na skill
[`iniciar-projeto-novo-a-partir-do-esqueleto.md`](../skills/iniciar-projeto-novo-a-partir-do-esqueleto.md).

## Estado atual (o esqueleto está VIVO)

Todas as camadas existem e o pipeline foi **validado ponta a ponta nos dois toggles**
(Databricks Sim e Não): `init.py` → `uv sync` → treino/avaliação → logging via MLflow,
com a suíte de testes e as cancelas de CI verdes nas duas cópias.

- **Modelo de referência**: [`pipeline/models/exemplo_modelo/`](../../pipeline/models/exemplo_modelo/) —
  um classificador (RandomForest) completo na anatomia de 5 arquivos, com config em
  [`pipeline/config/exemplo_modelo.yaml`](../../pipeline/config/exemplo_modelo.yaml).
- **Núcleo**: `pipeline/common/` (config pydantic, `Protocol DataSource` + factory, `Tracker` de
  MLflow, splits), `pipeline/data/sources/` (Parquet/Spark/SQL), `pipeline/entrypoints/` (local/serverless).
- **Cancelas de CI**: `tools/check.py` roda tudo (ruff, pytest, raiz mínima, manifesto
  em sync, isolamento de MLflow e de plataforma). Ver `.github/workflows/ci.yml`.
- **MLflow**: default local é backend **SQLite** (o file store `./mlruns` foi
  descontinuado). O caminho Databricks ainda **não** foi validado em workspace real
  (ver nota em `pipeline/common/tracking.py`).

## O que ler antes de mexer

- [arquitetura.md](arquitetura.md) — a estrutura-alvo e os invariantes.
- [decisoes.md](decisoes.md) — as decisões já ratificadas (não reabrir).
- `../rules/` — comportamento inegociável. **Leitura obrigatória antes de qualquer alteração.**
- `../guides/` — um guia por camada (config, data, models, common, entrypoints, platform).
- `../skills/` — procedimentos passo a passo para as tarefas comuns.
