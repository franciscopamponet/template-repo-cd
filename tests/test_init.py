"""Testes do scaffolder `tools/init.py` (Decisões 0 e 1).

Rodam o init de verdade, em modo não-interativo, numa cópia temporária do repo —
exatamente o fluxo real: copiar o esqueleto e rodar o script.

CUIDADO (e por que existe o PYTHONPATH abaixo): o projeto está instalado em modo
editável apontando para o repo ORIGINAL. Sem forçar o PYTHONPATH para a cópia, um
`import models...` resolveria para o repo original e o teste passaria por engano.
Os testes provam, via `__file__`, que o código exercitado é o da cópia.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

IGNORAR = shutil.ignore_patterns(
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "*.db",
    "mlruns",
    "mlartifacts",
    "dist",
    # Dados gerados (não o código em pipeline/data/sources, que precisa vir na cópia).
    "raw",
    "processed",
    "interim",
    "external",
    "*.parquet",
)


def _rodar(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    """Roda um comando na cópia, com o PYTHONPATH ancorado nela.

    O núcleo mora sob pipeline/ (src-layout), então é ele que entra no path para os
    imports de primeiro nível (from common..., from models...); a raiz entra para o
    `import tools`.
    """
    pythonpath = os.pathsep.join([str(cwd / "pipeline"), str(cwd)])
    env = {**os.environ, "PYTHONPATH": pythonpath}
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)


@pytest.fixture
def copia_do_esqueleto(tmp_path):
    """Copia o esqueleto para um diretório temporário, como faria um projeto novo."""
    destino = tmp_path / "projeto_novo"
    shutil.copytree(Path.cwd(), destino, ignore=IGNORAR)
    return destino


def _init(copia: Path, *, databricks: str, nome="Previsão de Churn", modelo="churn"):
    resultado = _rodar(
        [
            sys.executable,
            "tools/init.py",
            "--name",
            nome,
            "--databricks",
            databricks,
            "--model",
            modelo,
            "--yes",
        ],
        cwd=copia,
    )
    assert resultado.returncode == 0, f"init falhou:\n{resultado.stdout}\n{resultado.stderr}"
    return resultado


# ---------------------------------------------------------------------------
# Comportamento comum aos dois caminhos
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("databricks", ["yes", "no"])
def test_init_renomeia_modelo_e_config(copia_do_esqueleto, databricks):
    _init(copia_do_esqueleto, databricks=databricks)

    assert not (copia_do_esqueleto / "pipeline" / "models" / "exemplo_modelo").exists()
    assert not (copia_do_esqueleto / "pipeline" / "config" / "exemplo_modelo.yaml").exists()

    modelo = copia_do_esqueleto / "pipeline" / "models" / "churn"
    assert modelo.is_dir()
    # Rule 00: a anatomia sobrevive ao rename.
    assert {p.name for p in modelo.iterdir() if p.is_file()} == {
        "prepare_data.py",
        "build_model.py",
        "train.py",
        "evaluate_model.py",
        "orchestrator.py",
    }
    assert (copia_do_esqueleto / "pipeline" / "config" / "churn.yaml").exists()


@pytest.mark.parametrize("databricks", ["yes", "no"])
def test_init_atualiza_referencias_ao_modelo(copia_do_esqueleto, databricks):
    _init(copia_do_esqueleto, databricks=databricks)

    entrypoint = (copia_do_esqueleto / "pipeline" / "entrypoints" / "run_local.py").read_text(
        encoding="utf-8"
    )
    assert "models.churn.orchestrator" in entrypoint
    assert "exemplo_modelo" not in entrypoint

    orchestrator = (
        copia_do_esqueleto / "pipeline" / "models" / "churn" / "orchestrator.py"
    ).read_text(encoding="utf-8")
    assert "exemplo_modelo" not in orchestrator


@pytest.mark.parametrize("databricks", ["yes", "no"])
def test_init_aplica_nome_do_projeto(copia_do_esqueleto, databricks):
    _init(copia_do_esqueleto, databricks=databricks)

    pyproject = (copia_do_esqueleto / "pyproject.toml").read_text(encoding="utf-8")
    assert 'name = "previsao-de-churn"' in pyproject
    assert "esqueleto-ciencia-de-dados" not in pyproject

    readme = (copia_do_esqueleto / "README.md").read_text(encoding="utf-8")
    assert "Previsão de Churn" in readme
    assert "<!-- PREENCHER: nome do projeto -->" not in readme


@pytest.mark.parametrize("databricks", ["yes", "no"])
def test_init_se_autodestroi(copia_do_esqueleto, databricks):
    _init(copia_do_esqueleto, databricks=databricks)
    assert not (copia_do_esqueleto / "tools" / "init.py").exists()
    # O teste do scaffolder some junto: sem o script, ele quebraria a suíte do
    # projeto novo logo no primeiro `uv run pytest`.
    assert not (copia_do_esqueleto / "tests" / "test_init.py").exists()


@pytest.mark.parametrize("databricks", ["yes", "no"])
def test_suite_do_projeto_novo_passa(copia_do_esqueleto, databricks):
    """A prova de que o init entrega um repo coerente: a suíte do projeto novo passa.

    É o primeiro comando que a pessoa roda depois do init. Se algum teste ficou órfão
    (apontando para um arquivo que o init removeu), ele quebra aqui.
    """
    _init(copia_do_esqueleto, databricks=databricks)

    resultado = _rodar(
        [sys.executable, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider"],
        cwd=copia_do_esqueleto,
    )
    assert resultado.returncode == 0, (
        f"a suíte do projeto novo falhou:\n{resultado.stdout[-3000:]}\n{resultado.stderr[-2000:]}"
    )


@pytest.mark.parametrize("databricks", ["yes", "no"])
def test_init_nao_toca_a_doc_do_molde(copia_do_esqueleto, databricks):
    """docs/ descreve o molde (com exemplo_modelo como referência); o rename não o toca."""
    antes = (Path.cwd() / "docs" / "context" / "arquitetura.md").read_text(encoding="utf-8")
    _init(copia_do_esqueleto, databricks=databricks)
    depois = (copia_do_esqueleto / "docs" / "context" / "arquitetura.md").read_text(
        encoding="utf-8"
    )
    assert antes == depois
    assert (copia_do_esqueleto / "docs" / "rules").is_dir()
    # E o contexto do projeto (.claude/) continua presente para a cópia preencher.
    assert (copia_do_esqueleto / ".claude" / "context" / "projeto.md").exists()


def test_init_rejeita_segunda_execucao(copia_do_esqueleto):
    """Rodar duas vezes não pode corromper o projeto (guarda de pré-voo)."""
    _init(copia_do_esqueleto, databricks="no")

    # Sem Databricks, gen_conda.py é removido e init.py se autodestrói — mas as cancelas
    # (check_*.py) sobrevivem: o CI é o mesmo com ou sem Databricks (ver check_manifest.py).
    tools = copia_do_esqueleto / "tools"
    assert not (tools / "gen_conda.py").exists()
    assert not (tools / "init.py").exists()
    assert (tools / "check_root.py").exists()

    # Simula alguém restaurando o script do histórico do git e rodando de novo.
    shutil.copy(Path.cwd() / "tools" / "init.py", tools / "init.py")
    segunda = _rodar(
        [
            sys.executable,
            "tools/init.py",
            "--name",
            "Outro",
            "--databricks",
            "yes",
            "--model",
            "outro",
            "--yes",
        ],
        cwd=copia_do_esqueleto,
    )
    assert segunda.returncode == 1
    assert "já ter sido inicializado" in segunda.stdout
    # E o projeto continua íntegro: o modelo do primeiro init segue lá.
    assert (copia_do_esqueleto / "pipeline" / "models" / "churn").is_dir()
    assert not (copia_do_esqueleto / "pipeline" / "models" / "outro").exists()


def _git(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    base = ["git", "-c", "user.email=t@t.com", "-c", "user.name=teste"]
    return _rodar(base + cmd, cwd=cwd)


def test_init_aborta_com_arvore_git_suja(copia_do_esqueleto):
    """Guarda de segurança: o init recusa rodar sobre uma árvore git suja.

    O init APAGA/reescreve arquivos; sobre trabalho não commitado, isso seria difícil
    de desfazer. Numa cópia recém-clonada a árvore está limpa e a guarda não dispara.
    """
    copia = copia_do_esqueleto
    assert _git(["init", "-q"], cwd=copia).returncode == 0
    assert _git(["add", "-A"], cwd=copia).returncode == 0
    assert _git(["commit", "-qm", "cópia inicial"], cwd=copia).returncode == 0

    # Suja a árvore com um arquivo não rastreado.
    (copia / "trabalho_em_andamento.txt").write_text("wip", encoding="utf-8")

    resultado = _rodar(
        [
            sys.executable,
            "tools/init.py",
            "--name",
            "X",
            "--databricks",
            "no",
            "--model",
            "x",
            "--yes",
        ],
        cwd=copia,
    )
    assert resultado.returncode == 1
    assert "não commitadas" in resultado.stdout
    # Nada foi mutilado: o modelo de exemplo continua intacto.
    assert (copia / "pipeline" / "models" / "exemplo_modelo").is_dir()

    # Com a árvore limpa de novo, o init roda normalmente.
    assert _git(["add", "-A"], cwd=copia).returncode == 0
    assert _git(["commit", "-qm", "wip"], cwd=copia).returncode == 0
    ok = _rodar(
        [
            sys.executable,
            "tools/init.py",
            "--name",
            "X",
            "--databricks",
            "no",
            "--model",
            "x",
            "--yes",
        ],
        cwd=copia,
    )
    assert ok.returncode == 0, f"init falhou com árvore limpa:\n{ok.stdout}\n{ok.stderr}"


# ---------------------------------------------------------------------------
# Toggle = NÃO
# ---------------------------------------------------------------------------


def test_sem_databricks_poda_a_plataforma(copia_do_esqueleto):
    _init(copia_do_esqueleto, databricks="no")

    assert not (copia_do_esqueleto / "platform").exists()
    assert not (copia_do_esqueleto / "pipeline" / "entrypoints" / "run_serverless.py").exists()
    assert not (copia_do_esqueleto / "tools" / "gen_conda.py").exists()
    assert not (copia_do_esqueleto / "tests" / "test_gen_conda.py").exists()

    # O núcleo NÃO é tocado (invariante central).
    assert (copia_do_esqueleto / "pipeline" / "entrypoints" / "run_local.py").exists()
    assert (copia_do_esqueleto / "pipeline" / "common" / "tracking.py").exists()
    assert (copia_do_esqueleto / "pipeline" / "models" / "churn").is_dir()


def test_sem_databricks_remove_o_extra_do_pyproject(copia_do_esqueleto):
    _init(copia_do_esqueleto, databricks="no")

    pyproject = (copia_do_esqueleto / "pyproject.toml").read_text(encoding="utf-8")
    assert "databricks-sdk" not in pyproject
    assert "databricks-connect" not in pyproject
    # O extra 'spark' sobrevive: é independente do toggle.
    assert "pyspark" in pyproject


def test_sem_databricks_config_fica_local(copia_do_esqueleto):
    _init(copia_do_esqueleto, databricks="no")

    config = (copia_do_esqueleto / "pipeline" / "config" / "churn.yaml").read_text(encoding="utf-8")
    assert "databricks: false" in config
    assert "sqlite:///" in config


def test_sem_databricks_o_pipeline_roda_ponta_a_ponta(copia_do_esqueleto):
    """A prova real do invariante: sem platform/, o pipeline treina e loga."""
    copia = copia_do_esqueleto
    _init(copia, databricks="no")
    assert not (copia / "platform").exists()

    # Gera o dado que o config de exemplo espera (data/ é gitignored).
    gerar_dado = _rodar(
        [
            sys.executable,
            "-c",
            "import numpy as np, pandas as pd, pathlib;"
            "rng = np.random.default_rng(0); n = 300;"
            "x1, x2, x3 = rng.normal(size=n), rng.normal(size=n), rng.normal(size=n);"
            "y = ((x1 + x2) > 0).astype(int);"
            "pathlib.Path('pipeline/data/raw').mkdir(parents=True, exist_ok=True);"
            "pd.DataFrame({'x1': x1, 'x2': x2, 'x3': x3, 'y': y})"
            ".to_parquet('pipeline/data/raw/exemplo.parquet', index=False)",
        ],
        cwd=copia,
    )
    assert gerar_dado.returncode == 0, gerar_dado.stderr

    # Prova que o código exercitado é o da CÓPIA, não o do repo original.
    procedencia = _rodar(
        [sys.executable, "-c", "import models.churn.orchestrator as o; print(o.__file__)"],
        cwd=copia,
    )
    assert procedencia.returncode == 0, procedencia.stderr
    assert str(copia) in procedencia.stdout, "importou do repo original, não da cópia"

    resultado = _rodar(
        [
            sys.executable,
            "pipeline/entrypoints/run_local.py",
            "--config",
            "pipeline/config/churn.yaml",
        ],
        cwd=copia,
    )
    assert resultado.returncode == 0, f"pipeline falhou:\n{resultado.stdout}\n{resultado.stderr}"
    assert "run_id:" in resultado.stdout
    assert "accuracy" in resultado.stdout


# ---------------------------------------------------------------------------
# Toggle = SIM
# ---------------------------------------------------------------------------


def test_com_databricks_mantem_a_plataforma(copia_do_esqueleto):
    _init(copia_do_esqueleto, databricks="yes")

    assert (copia_do_esqueleto / "platform" / "databricks.yml").exists()
    assert (copia_do_esqueleto / "platform" / "MLProject").exists()
    assert (copia_do_esqueleto / "pipeline" / "entrypoints" / "run_serverless.py").exists()
    assert (copia_do_esqueleto / "tools" / "gen_conda.py").exists()

    pyproject = (copia_do_esqueleto / "pyproject.toml").read_text(encoding="utf-8")
    assert "databricks-sdk" in pyproject


def test_com_databricks_rege_o_conda_em_sync(copia_do_esqueleto):
    """Rule 03: o manifesto acompanha o novo nome do projeto."""
    _init(copia_do_esqueleto, databricks="yes")

    conda = (copia_do_esqueleto / "platform" / "conda.yaml").read_text(encoding="utf-8")
    assert "name: previsao-de-churn" in conda
    assert "ARQUIVO GERADO — NÃO EDITE" in conda

    check = _rodar([sys.executable, "tools/gen_conda.py", "--check"], cwd=copia_do_esqueleto)
    assert check.returncode == 0, f"conda.yaml fora de sync:\n{check.stdout}"


def test_com_databricks_config_e_bundle(copia_do_esqueleto):
    _init(copia_do_esqueleto, databricks="yes")

    config = (copia_do_esqueleto / "pipeline" / "config" / "churn.yaml").read_text(encoding="utf-8")
    assert "databricks: true" in config
    assert "/Shared/previsao-de-churn" in config

    # Os placeholders do bundle continuam pendentes, de propósito.
    bundle = (copia_do_esqueleto / "platform" / "databricks.yml").read_text(encoding="utf-8")
    assert "<PREENCHER:" in bundle

    # O job foi renomeado junto com o modelo.
    assert (copia_do_esqueleto / "platform" / "resources" / "treino_churn.yml").exists()
