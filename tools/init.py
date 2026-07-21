#!/usr/bin/env python3
"""Scaffolder embutido — roda UMA VEZ, logo após copiar o esqueleto (Decisões 0 e 1).

É o que torna a distribuição por cópia viável sem gerador externo: você copia o
esqueleto, roda este script, e o repo vira o seu projeto.

Usa APENAS a stdlib: precisa rodar antes do `uv sync`, quando ainda não há venv.

Uso interativo:
    python3 tools/init.py

Uso não-interativo (CI/testes):
    python3 tools/init.py --name "Previsão de Churn" --databricks no --model churn --yes

O que faz:
  1. Renomeia `pipeline/models/exemplo_modelo/` e `pipeline/config/exemplo_modelo.yaml`
     para o nome do primeiro modelo, atualizando todas as referências.
  2. Substitui os placeholders de nome do projeto (README, pyproject, MLProject).
  3. Aplica o TOGGLE (Decisão 1):
       - Databricks NÃO → remove `platform/`, `pipeline/entrypoints/run_serverless.py`, o extra
         `databricks` do pyproject e as ferramentas/testes que só existem para a
         plataforma. O núcleo NÃO é tocado (invariante central).
       - Databricks SIM → mantém tudo e regenera o `conda.yaml` (Rule 03), deixando os
         placeholders `<PREENCHER: ...>` do bundle para a cópia preencher.
  4. Se AUTODESTRÓI ao final.

POR QUE AUTODESTRUIR (e não deixar um marcador):
  - O script só faz sentido uma vez (Decisão 0: "roda 1x após a cópia"). Depois disso
    ele é código morto num repo que preza por raiz mínima e zero peso desnecessário.
  - Um marcador exigiria um arquivo de estado novo — e não há requisito técnico que o
    obrigue a existir (Rule 04). Ausência do arquivo JÁ é o estado "já executou": é
    autoevidente e impossível de dessincronizar.
  - Rodar duas vezes não pode corromper o projeto. Com autodestruição isso é garantido
    pela física, não pela disciplina: na segunda vez o arquivo não existe. Como rede
    extra, há uma checagem de pré-voo (`ja_inicializado`) para o caso de alguém
    restaurar o script do histórico do git e rodar de novo por engano.
  - O script não se perde: continua no histórico do git do esqueleto, que é a fonte
    canônica (Decisão 5: forward-only).
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

MODELO_ORIGINAL = "exemplo_modelo"
NOME_ESQUELETO = "esqueleto-ciencia-de-dados"
PLACEHOLDER_TITULO = "<!-- PREENCHER: nome do projeto -->"

# Onde o token do modelo pode aparecer. Restrito de propósito: a documentação do molde
# (docs/) e o contexto do projeto (.claude/) falam do esqueleto em geral, com o
# exemplo_modelo como referência canônica, e NÃO devem ser reescritos pelo rename.
PASTAS_COM_MODELO = [
    "pipeline/entrypoints",
    "pipeline/models",
    "pipeline/config",
    "tests",
    "platform",
]
EXTENSOES_TEXTO = {".py", ".yaml", ".yml", ".toml", ".md", ""}

# Arquivos que só existem por causa da plataforma (removidos se toggle = Não).
ARTEFATOS_DE_PLATAFORMA = [
    "platform",
    "pipeline/entrypoints/run_serverless.py",
    "tools/gen_conda.py",
    "tests/test_gen_conda.py",
]


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------


def slugify(texto: str) -> str:
    """'Previsão de Churn' -> 'previsao-de-churn' (nome válido de projeto Python)."""
    normalizado = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in normalizado if not unicodedata.combining(c))
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", sem_acento).strip("-").lower()
    if not slug:
        raise ValueError(f"Nome de projeto inválido: {texto!r}")
    return slug


def snake_case(texto: str) -> str:
    """'Churn Mensal' -> 'churn_mensal' (Rule 05: snake_case para pastas de modelo)."""
    return slugify(texto).replace("-", "_")


def arquivos_de_texto(pastas: list[str]) -> list[Path]:
    encontrados: list[Path] = []
    for nome in pastas:
        base = RAIZ / nome
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file() and p.suffix in EXTENSOES_TEXTO and "__pycache__" not in p.parts:
                encontrados.append(p)
    return encontrados


def substituir_em(caminho: Path, de: str, para: str) -> bool:
    """Substitui texto num arquivo. Devolve True se houve mudança."""
    try:
        conteudo = caminho.read_text(encoding="utf-8")
    except (UnicodeDecodeError, FileNotFoundError):
        return False
    if de not in conteudo:
        return False
    caminho.write_text(conteudo.replace(de, para), encoding="utf-8")
    return True


def ja_inicializado() -> str | None:
    """Detecta um repo que já passou pelo init. Devolve o motivo, ou None."""
    pyproject = RAIZ / "pyproject.toml"
    if pyproject.exists() and f'name = "{NOME_ESQUELETO}"' not in pyproject.read_text(
        encoding="utf-8"
    ):
        return "o pyproject.toml já não tem o nome do esqueleto"
    if not (RAIZ / "pipeline" / "models" / MODELO_ORIGINAL).exists():
        return f"pipeline/models/{MODELO_ORIGINAL}/ já não existe"
    return None


def arvore_git_suja() -> bool:
    """True se ESTA cópia é um repo git próprio com alterações não commitadas.

    Guarda de segurança: o init reescreve e APAGA arquivos. Rodá-lo sobre uma árvore
    suja mistura essa reescrita com trabalho não salvo e dificulta desfazer. Numa
    cópia recém-obtida ('Use this template' + clone) a árvore está limpa, então esta
    guarda não atrapalha o fluxo normal — ela só protege quem já começou a mexer.

    Só bloqueia quando dá para julgar com segurança. Se não há git (ou o comando não
    existe), ou se a raiz do repo não é ESTA pasta (ex.: a cópia foi parar dentro de
    outro repo), a guarda é pulada: aí não há uma árvore nossa a avaliar.
    """
    try:
        topo = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=RAIZ,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
    if Path(topo).resolve() != RAIZ.resolve():
        return False
    sujo = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=RAIZ,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    return bool(sujo)


# ---------------------------------------------------------------------------
# Passos do scaffolding
# ---------------------------------------------------------------------------


def renomear_modelo(novo: str) -> list[str]:
    """Renomeia o modelo de referência e atualiza todas as referências."""
    feitos = []

    # 1. Conteúdo: troca o token em todos os arquivos que o mencionam.
    for arquivo in arquivos_de_texto(PASTAS_COM_MODELO):
        if substituir_em(arquivo, MODELO_ORIGINAL, novo):
            feitos.append(f"atualizado: {arquivo.relative_to(RAIZ)}")

    # 2. Caminhos: renomeia arquivos/pastas cujo nome carrega o token.
    #    reverse=True garante que filhos são renomeados antes dos pais.
    alvos = sorted(
        (p for p in RAIZ.rglob(f"*{MODELO_ORIGINAL}*") if ".git" not in p.parts),
        key=lambda p: len(p.parts),
        reverse=True,
    )
    for antigo in alvos:
        destino = antigo.with_name(antigo.name.replace(MODELO_ORIGINAL, novo))
        antigo.rename(destino)
        feitos.append(f"renomeado: {antigo.relative_to(RAIZ)} -> {destino.relative_to(RAIZ)}")

    return feitos


def aplicar_nome_do_projeto(nome: str, slug: str) -> list[str]:
    """Substitui os placeholders de nome do projeto."""
    feitos = []

    pyproject = RAIZ / "pyproject.toml"
    conteudo = pyproject.read_text(encoding="utf-8")
    conteudo = conteudo.replace(f'name = "{NOME_ESQUELETO}"', f'name = "{slug}"')
    conteudo = re.sub(
        r'^description = ".*"$',
        f'description = "{nome}"',
        conteudo,
        count=1,
        flags=re.MULTILINE,
    )
    pyproject.write_text(conteudo, encoding="utf-8")
    feitos.append("pyproject.toml: nome e descrição do projeto")

    readme = RAIZ / "README.md"
    if readme.exists():
        texto = readme.read_text(encoding="utf-8")
        texto = texto.replace(PLACEHOLDER_TITULO, nome)
        readme.write_text(texto, encoding="utf-8")
        feitos.append("README.md: título")

    mlproject = RAIZ / "platform" / "MLProject"
    if mlproject.exists() and substituir_em(mlproject, NOME_ESQUELETO, slug):
        feitos.append("platform/MLProject: nome")

    return feitos


def remover_extra_databricks() -> list[str]:
    """Tira o extra `databricks` do pyproject (Rule 02: fonte única)."""
    pyproject = RAIZ / "pyproject.toml"
    conteudo = pyproject.read_text(encoding="utf-8")
    # Remove o bloco 'databricks = [ ... ]' inteiro, preservando os demais extras.
    novo = re.sub(r"^databricks = \[\n(?:.*\n)*?\]\n", "", conteudo, flags=re.MULTILINE)
    if novo == conteudo:
        return []
    pyproject.write_text(novo, encoding="utf-8")
    return ["pyproject.toml: extra 'databricks' removido"]


def ajustar_config_tracking(config: Path, usa_databricks: bool, slug: str) -> list[str]:
    """Aponta o tracking do config para o modo certo (Rule 07: tudo vem do config)."""
    if not config.exists():
        return []
    conteudo = config.read_text(encoding="utf-8")

    if usa_databricks:
        conteudo = conteudo.replace("databricks: false", "databricks: true")
        # Convenção de path do workspace — só se aplica no Databricks.
        conteudo = re.sub(
            r"^  experiment_name: .*$",
            f"  experiment_name: /Shared/{slug}",
            conteudo,
            count=1,
            flags=re.MULTILINE,
        )
        config.write_text(conteudo, encoding="utf-8")
        return [f"{config.relative_to(RAIZ)}: tracking em modo Databricks"]

    conteudo = conteudo.replace("databricks: true", "databricks: false")
    config.write_text(conteudo, encoding="utf-8")
    return [f"{config.relative_to(RAIZ)}: tracking local (SQLite)"]


def podar_plataforma() -> list[str]:
    """Toggle = Não: remove a casca inteira. O núcleo não é tocado (Rule 06)."""
    feitos = []
    for alvo in ARTEFATOS_DE_PLATAFORMA:
        caminho = RAIZ / alvo
        if not caminho.exists():
            continue
        if caminho.is_dir():
            shutil.rmtree(caminho)
        else:
            caminho.unlink()
        feitos.append(f"removido: {alvo}")
    return feitos


def regerar_conda() -> list[str]:
    """Toggle = Sim: mantém o manifesto em sync com o pyproject (Rule 03)."""
    gerador = RAIZ / "tools" / "gen_conda.py"
    if not gerador.exists():
        return []
    resultado = subprocess.run(
        [sys.executable, str(gerador)], capture_output=True, text=True, cwd=RAIZ
    )
    if resultado.returncode != 0:
        return [f"AVISO: não consegui regerar o conda.yaml: {resultado.stderr.strip()}"]
    return ["platform/conda.yaml: regerado a partir do pyproject"]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def perguntar(texto: str, default: str | None = None) -> str:
    sufixo = f" [{default}]" if default else ""
    while True:
        resposta = input(f"{texto}{sufixo}: ").strip()
        if resposta:
            return resposta
        if default:
            return default
        print("  (obrigatório)")


def perguntar_sim_nao(texto: str) -> bool:
    while True:
        resposta = input(f"{texto} [s/N]: ").strip().lower()
        if resposta in {"s", "sim", "y", "yes"}:
            return True
        if resposta in {"n", "nao", "não", "no", ""}:
            return False
        print("  Responda 's' ou 'n'.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inicializa uma cópia do esqueleto (roda 1x).",
    )
    parser.add_argument("--name", help="Nome do projeto.")
    parser.add_argument("--databricks", choices=["yes", "no"], help="Usar Databricks?")
    parser.add_argument("--model", help="Nome do primeiro modelo (snake_case).")
    parser.add_argument("--yes", action="store_true", help="Não pede confirmação.")
    args = parser.parse_args(argv)

    nao_interativo = args.name and args.databricks and args.model

    motivo = ja_inicializado()
    if motivo:
        print(f"ERRO: este repo parece já ter sido inicializado ({motivo}).")
        print("O init roda uma única vez. Se precisa mesmo repetir, parta de uma cópia limpa.")
        return 1

    if arvore_git_suja():
        print("ERRO: há alterações não commitadas nesta cópia.")
        print("O init reescreve e APAGA arquivos. Rode-o sobre uma árvore LIMPA, para")
        print("poder desfazer com 'git checkout .' se o resultado não for o esperado.")
        print("Commite (ou descarte) suas mudanças e rode de novo.")
        return 1

    print("=" * 70)
    print("  Inicialização do projeto (roda uma única vez)")
    print("=" * 70)

    nome = args.name or perguntar("Nome do projeto")
    usa_databricks = (
        args.databricks == "yes" if args.databricks else perguntar_sim_nao("Vai usar Databricks?")
    )
    modelo = args.model or perguntar("Nome do primeiro modelo", default="meu_modelo")

    slug = slugify(nome)
    modelo_snake = snake_case(modelo)

    print()
    print(f"  projeto    : {nome}  (slug: {slug})")
    print(f"  databricks : {'SIM' if usa_databricks else 'NÃO'}")
    print(f"  modelo     : {modelo_snake}")
    if not usa_databricks:
        print("               -> platform/ e run_serverless.py serão REMOVIDOS")
    print()

    if not (args.yes or nao_interativo) and not perguntar_sim_nao("Confirma?"):
        print("Cancelado. Nada foi alterado.")
        return 1

    feitos: list[str] = []
    feitos += renomear_modelo(modelo_snake)
    feitos += aplicar_nome_do_projeto(nome, slug)

    if usa_databricks:
        feitos += regerar_conda()
    else:
        feitos += podar_plataforma()
        feitos += remover_extra_databricks()

    feitos += ajustar_config_tracking(
        RAIZ / "pipeline" / "config" / f"{modelo_snake}.yaml", usa_databricks, slug
    )

    # Autodestruição: ver justificativa na docstring do módulo.
    # O teste do init morre junto: ele exercita um script que deixou de existir e,
    # se ficasse, quebraria a suíte do projeto novo logo no primeiro `uv run pytest`.
    teste_do_init = RAIZ / "tests" / "test_init.py"
    if teste_do_init.exists():
        teste_do_init.unlink()
        feitos.append("removido: tests/test_init.py (testava o scaffolder)")

    proprio = Path(__file__).resolve()
    tools = proprio.parent
    proprio.unlink()
    feitos.append("removido: tools/init.py (autodestruição — só roda uma vez)")
    if not any(tools.iterdir()):
        tools.rmdir()
        feitos.append("removido: tools/ (ficou vazia)")

    print("-" * 70)
    print("O que foi feito:")
    for item in feitos:
        print(f"  - {item}")

    print()
    print("-" * 70)
    print("Próximos passos:")
    print("  1. uv sync")
    print(f"  2. edite pipeline/config/{modelo_snake}.yaml (fonte de dados, params) — Rule 07")
    print("  3. uv run pytest")
    print(
        f"  4. uv run python pipeline/entrypoints/run_local.py "
        f"--config pipeline/config/{modelo_snake}.yaml"
    )
    if usa_databricks:
        print("  5. preencha os <PREENCHER: ...> em platform/databricks.yml e resources/")
        print("     e valide com: databricks bundle validate -t dev")
    print("  * leia docs/rules/ antes de alterar qualquer coisa")
    print("  * preencha os <!-- PREENCHER: ... --> restantes no README.md")
    print("-" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
