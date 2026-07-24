# CLAUDE.md — Ponto de entrada para qualquer IA ou pessoa

Este repositório é um **esqueleto canônico** para projetos de Ciência de Dados do
núcleo de dados da PoliJúnior. Toda a inteligência de execução viaja **dentro** do repo,
versionada — nada depende de conhecimento externo.

Apesar do nome do arquivo, o conteúdo é **neutro**: vale para qualquer IA ou pessoa, não
só para o Claude. Este é o único ponto de entrada da raiz (ver decisão 8 em
`docs/context/decisoes.md`).

## PARA A IA: o que abrir ANTES de ajudar

Você recebe este `CLAUDE.md` automaticamente, mas **não** o conteúdo dos arquivos que
ele cita — você precisa abri-los. Antes de guiar qualquer pessoa, faça nesta ordem:

1. **Descubra a fase do repo:**
   - **Cópia nova, ainda não inicializada** — sinais: existe `tools/init.py`, existe
     `pipeline/models/exemplo_modelo/`, e o `pyproject.toml` ainda tem
     `name = "esqueleto-ciencia-de-dados"`. Nesse caso, **o PRIMEIRO arquivo a abrir e
     seguir é [`docs/skills/iniciar-projeto-novo-a-partir-do-esqueleto.md`](docs/skills/iniciar-projeto-novo-a-partir-do-esqueleto.md)**
     (o passo a passo), com [`docs/GUIA-DO-ANALISTA.md`](docs/GUIA-DO-ANALISTA.md) ao
     lado para o *porquê* de cada passo. É ele que conduz o analista da cópia ao
     primeiro pipeline rodando.
   - **Projeto já inicializado** (o `init.py` já rodou e sumiu) — leia `docs/rules/`
     (obrigatório), o `.claude/context/` (o que ESTE projeto é) e o guia da camada que
     você vai tocar em `docs/guides/`.
2. **Só então** responda ou aja.

## As duas metades: molde × projeto

A documentação está separada pela **natureza** da informação:

- **`docs/`** — o **manual do molde**. Descreve o esqueleto em si: como ele é composto e
  como se mexe nele. Igual em todo projeto do núcleo. **Não muda de projeto para projeto.**
- **`.claude/`** — o contexto **deste projeto**. Descreve o problema de negócio, os
  dados, o domínio e as decisões da SUA cópia. Começa em branco e é **preenchido ao
  longo do projeto**. (Pasta oculta — use `ls -a`.)

Regra de ouro: se a informação descreve *o padrão*, mora em `docs/`; se descreve *este
projeto*, mora em `.claude/`.

## Onde as coisas moram

No molde (`docs/`):

- `docs/context/`  — o que é o esqueleto, arquitetura, decisões ratificadas, glossário.
- `docs/rules/`    — comportamento **inegociável**: o que você pode e não pode fazer.
  **Leitura obrigatória antes de alterar qualquer coisa.** É verificado pelo CI.
- `docs/guides/`   — um guia por camada (config, data, models, common, entrypoints, platform).
- `docs/skills/`   — procedimentos passo a passo (adicionar modelo, fonte de dados, dependência…).
- `docs/context/decisoes.md` — todas as decisões de arquitetura do esqueleto, num arquivo só.
- `docs/GUIA-DO-ANALISTA.md`  — onboarding narrado, da cópia ao primeiro pipeline rodando.

No seu projeto (`.claude/`):

- `.claude/context/` — **comece aqui ao herdar o repo**: preencha `projeto.md`,
  `glossario.md`, `decisoes.md` e `arquitetura.md` com o contexto da SUA cópia.
- `.claude/rules/`, `.claude/guides/`, `.claude/skills/` — espaço para acréscimos
  específicos do seu projeto (começam vazios; as versões do molde estão em `docs/`).

## Regras específicas deste projeto

Regras de **comportamento desta cópia** (ex.: métrica padrão, nomeação de tabelas),
criadas pela skill `criar-rule` e carregadas em toda sessão via `@import` abaixo. Não
confundir com as rules do molde (`docs/rules/`, verificadas pelo CI) — estas aqui são
soft e específicas do projeto. Enquanto vazio, não há regras específicas ainda.

<!-- criar-rule: inserir os @import das regras do projeto ABAIXO desta linha -->

## Primeiro contato?

Se você é analista e nunca viu este padrão, comece pelo
[`docs/GUIA-DO-ANALISTA.md`](docs/GUIA-DO-ANALISTA.md).

**Antes de alterar qualquer coisa, a leitura de `docs/rules/` é OBRIGATÓRIA.**
