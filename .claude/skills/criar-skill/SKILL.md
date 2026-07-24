---
name: criar-skill
description: Use quando o usuário quiser criar uma NOVA Skill do Claude Code neste projeto (uma capacidade invocável, não apenas um documento). Cria a skill em .claude/skills/<nome>/SKILL.md já no formato correto, com frontmatter válido, para que o Claude a descubra e possa invocá-la.
---

# Criar uma nova Skill do Claude Code

Esta skill cria OUTRA skill, no formato que o Claude Code reconhece. Use-a sempre que
alguém pedir algo como "cria uma skill que faz X" ou "quero uma nova skill".

## Entenda o formato (obrigatório)

Uma Skill do Claude Code só é reconhecida se estiver EXATAMENTE assim:

```
.claude/skills/<nome-da-skill>/
└── SKILL.md
```

- É uma **pasta** com o nome da skill em **kebab-case** (só minúsculas, números e hífen).
- Dentro dela, um arquivo chamado exatamente **`SKILL.md`**.
- O `SKILL.md` começa com **frontmatter** YAML com dois campos:
  - `name` — igual ao nome da pasta.
  - `description` — QUANDO usar a skill. É este campo que faz o Claude invocá-la sozinho.

Arquivo solto (`.claude/skills/algo.md`) ou sem frontmatter **não** conta como skill —
é só documentação.

## Passos

1. **Descubra com o usuário** (pergunte se não estiver claro):
   - o **nome** da skill em kebab-case (ex.: `limpar-base`);
   - **quando** ela deve ser usada — o gatilho, que vira o `description`;
   - **o que** ela faz — o passo a passo, que vira o corpo.

2. **Crie o arquivo** `.claude/skills/<nome>/SKILL.md` usando este molde:

   ```markdown
   ---
   name: <nome-da-skill>
   description: Use quando <situação/gatilho claro, com palavras do usuário>. <O que a skill faz, em 1 frase.>
   ---

   # <Título legível da skill>

   <Uma ou duas linhas: o que essa skill resolve.>

   ## Passos
   1. ...
   2. ...

   ## Checklist de saída
   - [ ] ...
   ```

3. **Capriche no `description`** — é o campo mais importante. Ele deve deixar clara a
   SITUAÇÃO em que a skill serve, com as palavras que o usuário usaria. Descrição vaga =
   o Claude não sabe quando invocar.
   - Bom: "Use quando o usuário quer adicionar uma dependência (pyproject → lock → conda)."
   - Ruim: "Gerencia dependências."

4. **Confira o formato** com o checklist abaixo.

5. **Avise o usuário** que uma skill nova costuma só ser descoberta ao **iniciar uma
   nova sessão** do Claude Code — na sessão atual ela pode ainda não aparecer.

## Checklist de saída
- [ ] Existe a pasta `.claude/skills/<nome>/` (nome em kebab-case).
- [ ] Dentro dela, um arquivo `SKILL.md` (nome exato, com essa capitalização).
- [ ] O frontmatter tem `name` (= nome da pasta) e `description`.
- [ ] O `description` diz QUANDO usar, com palavras do usuário.
- [ ] O corpo tem um passo a passo claro (e, de preferência, um checklist).
- [ ] Avisei sobre reiniciar a sessão para a skill ser descoberta.

## Observação
Skills do Claude Code SÓ funcionam em `.claude/skills/`. Por isso elas vivem aqui, e não
em `docs/skills/` (onde ficam os procedimentos-**documentação** do molde). São coisas
diferentes: `docs/skills/` = texto que se lê; `.claude/skills/` = capacidade que o Claude
invoca.
