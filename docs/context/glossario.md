# Glossário

**Esqueleto (boilerplate)** — este repositório: o molde canônico a partir do qual todo
projeto real nasce. Não é um projeto real.

**Cópia** — a instância independente do esqueleto que vira um projeto real. Não há
vínculo vivo com o esqueleto após a cópia (ver evolução forward-only).

**Toggle** — a pergunta "Databricks? S/N" feita pelo `tools/init.py`. Liga/desliga a
casca `platform/` inteira. É o único ponto onde a plataforma entra no projeto.

**Núcleo** — o pipeline neutro `config → prepare → build → train → evaluate →
orchestrator`. Idêntico com ou sem Databricks. Nunca importa de `platform/`.

**Plataforma** — a camada opcional (`platform/`) com os artefatos específicos de
Databricks (`databricks.yml`, `resources/`, `MLProject`, `conda.yaml`). Só sobrevive
se o toggle for SIM.

**Anatomia de 5 arquivos** — o contrato inegociável de todo modelo em
`pipeline/models/<nome>/`: `prepare_data.py`, `build_model.py`, `train.py`,
`evaluate_model.py`, `orchestrator.py`. Nem mais, nem menos.

**Mini-cérebro nativo** — o princípio de que toda a inteligência de execução
(contexto, rules, guias, skills) mora versionada dentro do repo, em `.claude/`. Nada
depende de conhecimento externo.

**DataSource** — o `Protocol` de interface de dados neutra definido em `pipeline/common/`. As
implementações concretas (`SparkTableSource`, `ParquetSource`, `SQLSource`) moram em
`pipeline/data/sources/` e são escolhidas via config. O pipeline pede o dado à interface e
nunca sabe de onde ele vem.

**MLflow** — a ferramenta de tracking de experimentos. Obrigatória sempre. O toggle
decide apenas ONDE ela guarda os dados (local vs. Databricks), nunca SE existe. Só o
`orchestrator.py` fala com ela, via `pipeline/common/tracking.py`.

**Raiz mínima** — o princípio de que a raiz do repo só contém o que tecnicamente não
funciona em outro lugar. Tudo o mais mora em subpastas.

**Forward-only** — o modelo de evolução: o esqueleto só evolui pra frente; projetos
já nascidos ficam congelados na versão de nascimento.
