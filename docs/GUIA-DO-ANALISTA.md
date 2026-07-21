# Guia do Analista — do zero ao primeiro pipeline rodando

Bem-vindo. Se você é analista de dados do núcleo e nunca viu este padrão, este é o
documento certo. A meta é honesta e específica: você sair da cópia do repositório até o
seu primeiro pipeline rodando **sem precisar perguntar nada a ninguém**. Ele é a versão
*narrada* — o passo a passo enxuto, em forma de checklist, está na skill
[`iniciar-projeto-novo-a-partir-do-esqueleto.md`](skills/iniciar-projeto-novo-a-partir-do-esqueleto.md).
Aqui a gente explica o *porquê* de cada passo.

> Nota sobre onde as coisas moram: o **manual do molde** (o padrão em si) fica em
> `docs/`; o **contexto deste projeto** (preenchido ao longo do tempo) fica em `.claude/`
> (pasta oculta — use `ls -a`). A regra: se descreve o padrão, é `docs/`; se descreve
> este projeto, é `.claude/`. Ver a decisão 8 em `docs/context/decisoes.md`.

---

## 1. O fluxo em 30 segundos

```
   ┌─────────────────────┐
   │  1. COPIE            │  "Use this template" no GitHub → um repo NOVO, seu.
   │     o esqueleto      │     (nunca rode nada dentro do repo-modelo original)
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │  2. python3          │  responde 3 perguntas: nome, Databricks? S/N, 1º modelo.
   │     tools/init.py    │     ele nomeia o projeto e liga/desliga a plataforma.
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │  3. uv sync          │  instala as dependências — só AGORA (o init pode ter
   │                     │     mexido no pyproject).
   └──────────┬──────────┘
              │
              ▼
   ┌──────────────────────────────────┐
   │  4. preencha                      │  conte à IA o que ESTE projeto é
   │  .claude/context/projeto.md       │     (negócio, dados, glossário).
   └──────────┬───────────────────────┘
              │
              ▼
   ┌─────────────────────┐
   │  5. rode o pipeline  │  uv run python pipeline/entrypoints/run_local.py
   │                     │            --config pipeline/config/<modelo>.yaml
   └─────────────────────┘
```

Cinco passos. O resto deste guia é cada um deles, explicado.

---

## 2. O que é este repo

Este repositório é um **esqueleto** (boilerplate) padrão para projetos de Ciência de
Dados do núcleo. Ele não é um projeto real — é o **molde** a partir do qual todo projeto
real do núcleo nasce. A ideia é que qualquer projeto de DS aqui tenha a mesma anatomia:
os mesmos lugares para config, para os modelos, para a lógica compartilhada. Você chega
num projeto que nunca viu e já sabe onde tudo mora, porque é sempre igual.

Cada projeto real é uma **cópia independente** deste esqueleto. Não existe um repo-mãe
hospedando vários projetos, nem um gerador externo: você copia, e a cópia é sua, com
vida própria. E tudo que uma IA precisa para te ajudar já **viaja dentro do repo**,
separado pela natureza: o manual do padrão (as regras, os guias de cada camada, os
procedimentos) está em `docs/`; o contexto do seu projeto (negócio, dados, domínio),
que você preenche ao longo do tempo, está em `.claude/`. Nada depende da cabeça de uma
pessoa ou de um documento perdido num Drive. Se está no repo, a IA (e você) encontra.

---

## 3. Passo 0 — Obtenha a SUA cópia

> ### ⚠️ NUNCA rode o `init` dentro do repo-modelo original
>
> O `init` **apaga pastas e reescreve arquivos** — é assim que ele transforma o molde
> no seu projeto. Rodá-lo dentro do esqueleto-modelo **mutila o padrão para todo o
> núcleo**: o próximo colega que for copiar encontraria um molde já quebrado. O init só
> deve rodar na sua cópia pessoal.

O jeito certo de obter a sua cópia:

- **No GitHub, use o botão "Use this template" → "Create a new repository".** Isso cria
  um repositório **novo e separado**, que é seu, com o conteúdo do esqueleto mas sem
  amarração com ele. Depois é só clonar esse repo novo para a sua máquina.
- Alternativa manual: clone o esqueleto, apague o `.git` dele e faça `git init` para
  começar um histórico próprio. O resultado tem que ser, de novo, **um repositório
  separado e seu**.

Em qualquer caminho, o teste é simples: se você fizer `git remote -v`, o `origin` tem
que apontar para **o seu repo**, não para o esqueleto-modelo. Confirmou? Pode seguir.

---

## 4. Passo 1 — Rode o init (`python3 tools/init.py`)

O `init` é um **script de terminal comum** — não é a IA, não é o Claude. Ele imprime
perguntas na tela e espera você **digitar a resposta** e apertar Enter. Roda com o
Python do sistema (`python3`), de propósito: ele precisa funcionar **antes** de você
instalar qualquer dependência.

```bash
python3 tools/init.py
```

Ele vai te fazer três perguntas:

1. **Nome do projeto** — o nome "de gente" (ex.: `Previsão de Churn`). Vira o nome e a
   descrição no `pyproject.toml`, o título do `README.md`, e por aí vai.
2. **Databricks? (S/N)** — o *toggle*. É a decisão mais importante do init (detalhe
   abaixo).
3. **Nome do primeiro modelo** — em `snake_case` (ex.: `churn`). O init renomeia o
   modelo de exemplo (`pipeline/models/exemplo_modelo/` e `pipeline/config/exemplo_modelo.yaml`) para esse
   nome, atualizando todas as referências. Assim você já começa com um modelo real seu,
   no lugar do exemplo.

### O toggle, em uma frase

**Databricks = Não** apaga a pasta `platform/` e o entrypoint serverless (mais o extra
`databricks` do `pyproject` e o gerador de `conda.yaml`); **Databricks = Sim** mantém
tudo isso. Nos **dois** casos, o **núcleo do pipeline é idêntico** — a plataforma é uma
casca opcional por fora, nunca uma dependência de dentro. Escolha "Não" se você vai
rodar localmente; "Sim" se o projeto vai para o Databricks.

Uma coisa que sobrevive ao toggle em qualquer caso: as **cancelas** do CI (os
verificadores em `tools/check_*.py`). O CI é o mesmo com ou sem Databricks — ver a
decisão 7 em [`docs/context/decisoes.md`](context/decisoes.md).

### O init não te surpreende

Antes de apagar ou reescrever qualquer coisa, o init:

- **mostra o resumo do que vai fazer** — o nome do projeto, o toggle escolhido, o nome
  do modelo e, se for "Não", o aviso explícito de que `platform/` e o
  `run_serverless.py` **serão removidos** — e então **pede confirmação** (`Confirma?`).
  Se você responder que não, ele encerra sem tocar em nada;
- **aborta se a sua árvore git estiver suja** (alterações não commitadas). Como o init
  reescreve e apaga arquivos, ele exige uma árvore **limpa** — assim, se o resultado não
  for o que você esperava, um `git checkout .` desfaz tudo. Numa cópia recém-clonada a
  árvore já está limpa, então isso não te atrapalha; a trava existe para proteger quem
  já começou a mexer;
- **recusa rodar duas vezes**: depois do init, o script já fez seu trabalho e se
  autodestrói; uma segunda execução é barrada por uma checagem de pré-voo.

Quando termina, o init imprime a lista do que fez e os próximos passos.

---

## 5. Passo 2 — `uv sync`

```bash
uv sync
```

Isso instala as dependências do projeto num ambiente virtual. A pergunta natural é: por
que só agora, e não antes do init?

Porque **o init pode ter mudado a lista de dependências**. Se você escolheu "Databricks
= Não", ele removeu o extra `databricks` do `pyproject.toml`. Se você instalasse
**antes** do init, instalaria a lista errada — com pacotes que o seu projeto não vai
usar. Rodar o `uv sync` depois garante que você instala exatamente o que o seu projeto,
já configurado, precisa. (É também por isso que o init roda com `python3` puro, sem
depender de nada instalado.)

---

## 6. Passo 3 — Preencha o contexto do projeto em `.claude/context/`

Abra [`.claude/context/projeto.md`](../.claude/context/projeto.md) (e, conforme o projeto
cresce, os vizinhos `glossario.md`, `decisoes.md` e `arquitetura.md`). Eles vêm com
espaços em branco marcados `<!-- PREENCHER -->`. É aqui que você conta o que **este**
projeto é: o problema de negócio, de onde vêm os dados, quem são os stakeholders e o
glossário do domínio (aqueles termos que só quem é de dentro entende).

Por que isso importa tanto? Porque, até você preencher, a IA sabe operar o **padrão** —
ela conhece a anatomia, as regras, como mexer em cada camada — mas não sabe **nada do
seu projeto**. Ela não sabe o que é "churn" no seu contexto, nem qual tabela é a fonte
da verdade, nem que a métrica que importa é o recall. Preencher esse arquivo é o passo
que transforma a cópia genérica no **seu** projeto, também aos olhos da IA. Vale cinco
minutos e economiza muitas idas e vindas depois.

---

## 7. Passo 4 — Trabalhe

### Rodar o pipeline localmente

Todo pipeline é dirigido pelo config do modelo. Para rodar o modelo que o init criou:

```bash
uv run python pipeline/entrypoints/run_local.py --config pipeline/config/<modelo>.yaml
```

(troque `<modelo>` pelo nome que você deu no init). A saída traz o `run_id` do MLflow e
as métricas do modelo — algo como `run_id: ...` seguido de
`métricas: {'accuracy': ..., 'f1': ...}`. Se você ainda não tem o dado que o config
aponta, gere/aponte um primeiro; o config de exemplo espera um Parquet em
`pipeline/data/raw/`.

### Onde as coisas moram

- **`pipeline/config/`** — os parâmetros. Um YAML por modelo (`pipeline/config/<modelo>.yaml`), com o
  mesmo nome da pasta do modelo. Caminho de dados, tabela, hiperparâmetros, nome do
  experimento: tudo vem daqui, nunca fica fixo no código. Mexeu em parâmetro? É aqui.
- **`pipeline/models/<modelo>/`** — o modelo em si, sempre com **exatamente cinco arquivos** (a
  "anatomia de 5 arquivos"), cada um com um papel:
  - `prepare_data.py` — pede o dado à interface e devolve treino/teste prontos (nunca
    sabe de *onde* o dado vem);
  - `build_model.py` — constrói o modelo, ainda sem treinar;
  - `train.py` — treina;
  - `evaluate_model.py` — calcula as métricas;
  - `orchestrator.py` — a espinha dorsal: amarra os quatro acima e é o **único** que
    fala com o MLflow.
- **`pipeline/common/`** — o que é compartilhado entre modelos: a interface de dados
  (`DataSource`), o wrapper de tracking do MLflow, utilitários de split. Se uma lógica
  serve a mais de um modelo, o lugar dela é aqui — nunca um sexto arquivo dentro de
  `pipeline/models/<modelo>/`.

### Precisa ir além do modelo inicial?

Para as tarefas mais comuns, já existe um procedimento pronto em `docs/skills/` — não
reinvente:

- **Adicionar um novo modelo** → [`adicionar-novo-modelo.md`](skills/adicionar-novo-modelo.md)
- **Adicionar uma nova fonte de dados** (sem tocar no núcleo) → [`adicionar-nova-fonte-de-dados.md`](skills/adicionar-nova-fonte-de-dados.md)
- **Adicionar uma dependência** (pyproject → lock → conda → CI) → [`adicionar-dependencia.md`](skills/adicionar-dependencia.md)

---

## 8. Onde a IA (e você) se orientam

A porta de entrada é o **[`CLAUDE.md`](../CLAUDE.md)** na raiz. Qualquer IA que clona o
repo o lê primeiro e descobre sozinha que existe um padrão a seguir. Ele separa as duas
metades — o **molde** em `docs/` e o **seu projeto** em `.claude/` — e aponta para:

- **`docs/rules/`** — o que você **pode e não pode** fazer. Comportamento inegociável.
  Leitura obrigatória antes de mexer em qualquer coisa.
- **`docs/guides/`** — como mexer em **cada camada** (config, data, models, common,
  entrypoints, platform). Quando for editar uma camada, leia o guia dela antes.
- **`docs/context/`** — o que é o esqueleto, sua arquitetura e as decisões já tomadas
  (em `decisoes.md`) e por quê.
- **`.claude/context/`** — o contexto do SEU projeto, que você preenche.

### Um recado final, para você não tropeçar

Boa parte das regras deste repo não é só conselho — é **verificada automaticamente pelo
CI**. Se você criar um arquivo solto na raiz, ou fizer algum arquivo `import mlflow`
fora do `orchestrator`/`pipeline/common/tracking.py`, ou o núcleo importar de `platform/`, **o CI
barra o seu merge**. Não é implicância: cada uma dessas travas existe por um motivo que
está escrito em `docs/rules/`. Se uma cancela te parar, leia a regra correspondente —
a mensagem de erro te diz qual é. E, para checar tudo localmente **antes** de commitar,
rode:

```bash
python3 tools/check.py
```

Ele roda o mesmo conjunto do CI (lint, testes e todas as cancelas) e te diz, em um
resumo, se está tudo verde. Verde aqui, verde no CI.

Bom trabalho — e bem-vindo ao padrão. 🎯
