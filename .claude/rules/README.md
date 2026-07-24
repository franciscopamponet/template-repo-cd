# Rules deste projeto

Aqui ficam as **regras específicas deste projeto** — convenções de comportamento que
nascem ao longo do trabalho (ex.: "métrica principal é recall", "toda tabela de staging
leva prefixo `stg_`", "nunca commitar dado com PII").

Não confundir com as **rules do molde** ([`docs/rules/`](../../docs/rules/)): aquelas são
estruturais, inegociáveis e verificadas pelo CI (cancelas). Estas aqui são **soft** —
guiam a IA e o time, sem robô conferindo. (As rules do molde são mantidas pelo dono do
repo como atualização do esqueleto, não pelo analista.)

## Como criar uma regra (o jeito certo)

Não basta largar um `.md` aqui — o Claude **não lê esta pasta sozinho**. A regra só passa
a valer quando é "ligada na tomada" via `@import` no `CLAUDE.md`.

Use a skill **`criar-rule`** (peça: *"cria uma regra de projeto que…"*). Ela:
1. cria `.claude/rules/<nome>.md` no formato certo (curto: enunciado + Por quê / Faça / Não faça);
2. insere `@.claude/rules/<nome>.md` na seção "Regras específicas deste projeto" do `CLAUDE.md`;
3. a regra passa a ser lida em **toda sessão** (a partir da próxima).

## Dica
Mantenha cada regra **curta e de alto valor** — tudo que entra via `@import` é carregado
em toda sessão, então muitas regras (ou regras longas) incham o contexto.
