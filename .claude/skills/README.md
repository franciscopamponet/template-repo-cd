# Skills

**Todas** as skills do repo moram aqui — não existe mais skill em `docs/`. Skills do
Claude Code só funcionam neste diretório (`.claude/skills/`), no formato
`<nome>/SKILL.md` com frontmatter (`name`, `description`). O Claude as **descobre e
invoca sozinho** quando a situação bate com o `description` (ver decisão 10).

## O que mora aqui

**Skills do molde** (vêm com o esqueleto, valem em qualquer cópia):
- `iniciar-projeto-novo-a-partir-do-esqueleto/` — do zero ao primeiro pipeline (copiar → init → uv sync → rodar).
- `adicionar-novo-modelo/` — criar `pipeline/models/<nome>/` na anatomia de 5 arquivos.
- `adicionar-nova-fonte-de-dados/` — implementar um novo `DataSource` sem tocar no núcleo.
- `adicionar-dependencia/` — pyproject → uv lock → regerar conda → CI.
- `criar-skill/` — cria OUTRAS skills no formato correto.
- `criar-rule/` — cria regras de projeto (`.claude/rules/`) e as liga no `CLAUDE.md`.

**Skills específicas do seu projeto:** adicione-as aqui, sempre como `<nome>/SKILL.md`.
Use `criar-skill` para gerar no formato certo.

> Uma skill nova geralmente só é descoberta ao iniciar uma **nova sessão** do Claude Code.
