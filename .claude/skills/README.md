# Skills deste projeto

Atenção: há **dois sentidos** de "skill", e eles moram em lugares diferentes.

- **`docs/skills/`** — procedimentos-**documentação** do molde (adicionar modelo, fonte
  de dados, dependência, iniciar projeto). São `.md` que a IA/pessoa **lê**. Não são
  invocáveis.
- **`.claude/skills/` (aqui)** — **Skills de verdade do Claude Code**: capacidades que o
  Claude **descobre e invoca sozinho**. Só funcionam neste diretório, no formato
  `<nome>/SKILL.md` com frontmatter (`name`, `description`). É por isso que elas vivem
  aqui, e não em `docs/` — é uma exigência técnica do Claude Code.

## O que já mora aqui
- **`criar-skill/`** — uma skill que **cria outras skills** no formato correto. Vem com o
  molde para facilitar. Peça algo como "cria uma skill que faz X" e ela conduz.

Adicione aqui as skills **específicas do seu projeto**, sempre no formato
`<nome>/SKILL.md`. Uma skill nova geralmente só é descoberta ao iniciar uma **nova
sessão** do Claude Code.
