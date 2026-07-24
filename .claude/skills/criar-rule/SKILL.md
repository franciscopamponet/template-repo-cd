---
name: criar-rule
description: Use quando o usuário quiser criar uma REGRA específica deste projeto (uma convenção de comportamento — ex.: "métrica padrão é recall", "toda tabela de staging leva prefixo stg_", "nunca commitar dado com PII"). Cria a regra em .claude/rules/<nome>.md e a OPERACIONALIZA inserindo um @import no CLAUDE.md, para ser lida em toda sessão.
---

# Criar uma regra específica do projeto

Esta skill cria uma **regra de projeto** (comportamental, soft) e já a **liga na tomada**:
cria o arquivo em `.claude/rules/` e insere o `@import` no `CLAUDE.md`, para o Claude ler
a regra em toda sessão.

## Escopo — leia antes

Esta skill cuida **só de regras de PROJETO** (`.claude/rules/`). Ela **NÃO** cria nem
edita regras de **arquitetura** (`docs/rules/`, com cancelas no CI) — essas são do molde,
mantidas pelo dono do repositório como atualização do esqueleto, **nunca pelo analista**.
Se o pedido for uma regra estrutural (ex.: "nada no núcleo pode importar de platform"),
avise que isso é mudança de molde e não é o papel desta skill.

Sinais de que é regra de PROJETO (caso desta skill): fala de negócio, domínio, convenção
de nomes de dados, métrica, processo. Ex.: "usar recall como métrica principal".

## Passos

1. **Levante com o usuário:**
   - **nome** da regra em kebab-case (ex.: `metrica-principal`);
   - o **enunciado** (o que sempre/nunca fazer);
   - o **porquê** (a razão — ajuda a IA a aplicar com bom senso).

2. **Crie** `.claude/rules/<nome>.md` com este molde (curto — ele é lido em toda sessão):

   ```markdown
   # Regra do projeto — <título>

   <Enunciado claro: o que sempre/nunca fazer.>

   **Por quê:** <a razão.>
   **Faça:** <o comportamento correto.>
   **Não faça:** <o que evitar.>
   ```

3. **Operacionalize no `CLAUDE.md`** — abra o `CLAUDE.md` da raiz, ache a linha marcadora
   na seção "Regras específicas deste projeto":

   ```
   <!-- criar-rule: inserir os @import das regras do projeto ABAIXO desta linha -->
   ```

   e insira, **logo abaixo dela**, uma linha:

   ```
   @.claude/rules/<nome>.md
   ```

   Não duplique: se já existir um `@import` para esse arquivo, não adicione de novo.

4. **Confira** com o checklist abaixo.

5. **Avise o usuário** que a regra passa a valer na **próxima sessão** do Claude (o
   `@import` é lido quando o `CLAUDE.md` é carregado, no início da sessão).

## Boas práticas
- **Uma regra curta por arquivo.** Tudo em `@import` entra no contexto de toda sessão;
  regras longas ou muitas regras incham o contexto. Prefira poucas, claras e de alto valor.
- Se a regra ficar obsoleta, remova o arquivo **e** a linha `@import` correspondente.

## Checklist de saída
- [ ] Existe `.claude/rules/<nome>.md` (kebab-case), curto e com "Por quê / Faça / Não faça".
- [ ] O `CLAUDE.md` tem `@.claude/rules/<nome>.md` logo abaixo do marcador, sem duplicar.
- [ ] Não toquei em `docs/rules/` (isso é molde, não é o escopo desta skill).
- [ ] Avisei que vale a partir da próxima sessão.
