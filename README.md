# <!-- PREENCHER: nome do projeto -->

> **Template.** Este README é herdado do esqueleto canônico de projetos de Ciência de
> Dados do núcleo de dados da PoliJúnior. Os trechos marcados com
> `<!-- PREENCHER: ... -->` devem ser completados por cada projeto-cópia.

<!-- PREENCHER: uma frase dizendo o que este projeto faz. -->

## 👋 Chegou agora? Comece aqui

Se você é analista e nunca viu este padrão, leia o
**[Guia do Analista](docs/GUIA-DO-ANALISTA.md)** — ele te leva, narrado e sem pressupor
nada, da cópia do repositório até o primeiro pipeline rodando.

## O que é

Este projeto nasceu como **cópia independente** do esqueleto canônico. A documentação
está separada pela natureza: o **manual do molde** (como o esqueleto é composto e como
se mexe nele) mora em [`docs/`](docs/); o **contexto deste projeto** (negócio, dados,
domínio), preenchido ao longo do tempo, mora em [`.claude/`](.claude/). O ponto de
entrada único, para IA ou pessoa, é o [`CLAUDE.md`](CLAUDE.md).

## Como começar (a partir do esqueleto)

1. **Copie** o esqueleto para um novo diretório (cópia independente, sem vínculo com o
   esqueleto original).
2. **Rode o scaffolder uma única vez** (usa só a stdlib — roda ANTES do `uv sync`):
   ```bash
   python3 tools/init.py
   ```
   Ele pergunta o toggle Databricks (S/N), poda `platform/` se Não, define o modo dos
   `pipeline/entrypoints/` e nomeia o projeto. Ao terminar, se autodestrói.
3. **Instale as dependências:**
   ```bash
   uv sync
   ```
4. Comece a trabalhar dentro da estrutura pronta. Passo a passo completo na skill
   [`iniciar-projeto-novo-a-partir-do-esqueleto`](.claude/skills/iniciar-projeto-novo-a-partir-do-esqueleto/SKILL.md).

## Como rodar

O pipeline é dirigido pelo config do modelo (Rule 07). Execução local:

```bash
uv run python pipeline/entrypoints/run_local.py --config pipeline/config/<modelo>.yaml
# saída: run_id: ... / métricas: {'accuracy': ..., 'f1': ...}
```

Antes de commitar, rode as cancelas (mesmo conjunto do CI):

```bash
python3 tools/check.py     # ruff + pytest + raiz mínima + manifesto + isolamentos
```

<!-- PREENCHER: se este projeto tem um comando/entrypoint próprio além do acima, descreva-o. -->

## Onde ficam as regras

**A leitura de [`docs/rules/`](docs/rules/) é obrigatória antes de qualquer alteração.**

Documentação do **molde** (em [`docs/`](docs/)):

- Contexto e arquitetura: [`docs/context/`](docs/context/)
- Rules (o que pode/não pode): [`docs/rules/`](docs/rules/)
- Guias por etapa: [`docs/guides/`](docs/guides/)
- Decisões de arquitetura: [`docs/context/decisoes.md`](docs/context/decisoes.md)
- Skills invocáveis (adicionar modelo, fonte, dependência, iniciar projeto…): [`.claude/skills/`](.claude/skills/)

Contexto **deste projeto** (em [`.claude/`](.claude/), a preencher): problema de
negócio, dados, glossário do domínio e decisões da cópia.

> `.claude/` é uma pasta oculta — use `ls -a` para enxergá-la.

## Estrutura

Ver [`docs/context/arquitetura.md`](docs/context/arquitetura.md) para a estrutura-alvo
completa e os invariantes.

---

<!-- PREENCHER: seção de contato/responsáveis do projeto, se aplicável. -->
