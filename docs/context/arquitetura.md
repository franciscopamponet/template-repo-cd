# Arquitetura

## Estrutura-alvo do repo

```
.
├── CLAUDE.md                 ← ponto de entrada ÚNICO (IA ou pessoa); aponta para docs/ e .claude/
├── README.md
├── pyproject.toml            ← FONTE ÚNICA de dependências (uv)
├── uv.lock
├── .gitignore
├── .github/workflows/        ← CI: lint, testes, check de raiz mínima, check de manifesto em sync
├── docs/                     ← MANUAL DO MOLDE — igual em todo projeto do núcleo
│   ├── context/              ← o que é o esqueleto, arquitetura, decisões, glossário
│   ├── rules/                ← comportamento: o que se pode e não pode fazer (verificado no CI)
│   ├── guides/               ← 1 guia por etapa: config, data, models, common, entrypoints, platform
│   ├── skills/               ← procedimentos reutilizáveis (.md)
│   └── GUIA-DO-ANALISTA.md   ← onboarding narrado, da cópia ao primeiro pipeline
├── .claude/                  ← CONTEXTO DESTE PROJETO — preenchido ao longo do tempo (pasta oculta)
│   ├── context/              ← projeto, arquitetura, decisões e glossário DA CÓPIA (a preencher)
│   └── rules/ guides/ skills/← espaço para acréscimos específicos do projeto
├── tools/
│   └── init.py               ← roda 1x após copiar: pergunta o toggle, poda platform/, nomeia o projeto
├── tests/                    ← testes do molde
├── pipeline/                 ← ★ ONDE O ANALISTA TRABALHA (decisão 9)
│   ├── config/               ← config por modelo (pipeline config-driven)
│   ├── data/                 ← implementações concretas da interface de dados (data/sources/)
│   ├── models/<modelo>/      ← anatomia OBRIGATÓRIA de 5 arquivos por modelo:
│   │   ├── prepare_data.py
│   │   ├── build_model.py
│   │   ├── train.py
│   │   ├── evaluate_model.py
│   │   └── orchestrator.py   ← espinha dorsal + ÚNICO ponto de contato com MLflow
│   ├── common/               ← lógica compartilhada entre modelos (contratos, tracking, splits)
│   └── entrypoints/          ← launchers finos (modo local/serverless, conforme toggle)
└── platform/                 ← infra opcional; SÓ sobrevive se toggle = SIM (fica FORA de pipeline/)
    ├── databricks.yml
    ├── resources/
    ├── MLProject
    └── conda.yaml            ← GERADO a partir do pyproject, nunca escrito à mão
```

## Invariante central

**O núcleo é IDÊNTICO com ou sem Databricks.** O pipeline
`config → prepare → build → train → evaluate → orchestrator` não depende de
plataforma. `platform/` é a casca inteira que o toggle liga/desliga. Nada do núcleo
importa de `platform/`; se o toggle for Não, o repo tem que rodar com `platform/`
inexistente.

MLflow é **OBRIGATÓRIO sempre**. O toggle decide apenas ONDE ele guarda os dados
(local vs. Databricks), nunca SE ele existe.

## Princípio da raiz mínima

A raiz é uma **vitrine de ponteiros**, não um depósito. Só fica na raiz o que
tecnicamente não funciona em outro lugar. O critério é **requisito técnico**, não
gosto. A documentação do molde mora em `docs/`; o contexto do projeto, em `.claude/`.

### Por que cada arquivo da raiz não pode sair de lá

| Arquivo                  | Motivo técnico (por que não pode sair da raiz)                         |
| ------------------------ | --------------------------------------------------------------------- |
| `pyproject.toml` / `uv.lock` | O `uv` só procura na raiz.                                         |
| `.gitignore`             | O Git só lê neste caminho exato.                                      |
| `.github/workflows/`     | O GitHub Actions só executa a partir daqui.                          |
| `README.md`              | É o que o GitHub renderiza na página do repo.                        |
| `CLAUDE.md`              | Tool discovery: ponto de entrada único; é como uma IA que clona o repo descobre sozinha que há um padrão a seguir. |

**Qualquer outro arquivo na raiz é violação da regra.**

## Anatomia de 5 arquivos (por modelo)

Todo modelo em `pipeline/models/<nome>/` tem exatamente:

1. `prepare_data.py`   — prepara os dados (pede o dado à interface `DataSource`, nunca sabe de onde vem).
2. `build_model.py`    — constrói o modelo.
3. `train.py`          — treina.
4. `evaluate_model.py` — avalia.
5. `orchestrator.py`   — espinha dorsal + **único ponto de contato com MLflow** (via `pipeline/common/tracking.py`).

## Interface de dados neutra

Um `Protocol` `DataSource` definido em `pipeline/common/`, com implementações concretas
(`SparkTableSource`, `ParquetSource`, `SQLSource`) em `pipeline/data/sources/`, escolhidas
via config. O código de preparação só pede o dado à interface; nunca sabe de onde ele vem.
