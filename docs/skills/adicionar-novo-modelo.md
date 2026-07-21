# Skill — Adicionar um novo modelo

Procedimento para criar `pipeline/models/<novo>/` respeitando a anatomia de 5 arquivos
(Rule 00) e a disciplina de nomes (Rule 05). Referência viva: `pipeline/models/exemplo_modelo/`.

## Pré-condições
- Nome do modelo em `snake_case` (ex.: `churn_mensal`). Ele será a pasta **e** o nome
  do config (Rule 05): `pipeline/config/<novo>.yaml` ↔ `pipeline/models/<novo>/`.

## Passos

1. **Copie o modelo de referência:**
   ```bash
   cp -r pipeline/models/exemplo_modelo pipeline/models/<novo>
   ```
   Devem existir exatamente 5 arquivos: `prepare_data.py`, `build_model.py`,
   `train.py`, `evaluate_model.py`, `orchestrator.py`. Nem mais, nem menos (Rule 00).

2. **Atualize os imports internos do `orchestrator.py`.** Ele importa os outros 4 pelo
   caminho do pacote:
   ```python
   from models.<novo>.prepare_data import prepare_data
   from models.<novo>.build_model import build_model
   from models.<novo>.train import train
   from models.<novo>.evaluate_model import evaluate_model
   ```

3. **Crie o config com o mesmo nome:**
   ```bash
   cp pipeline/config/exemplo_modelo.yaml pipeline/config/<novo>.yaml
   ```
   Ajuste `name: <novo>`, a `data_source`, o `tracking.experiment_name` e os `params`.
   Nada de valor fixo no `.py` — tudo vem daqui (Rule 07).

4. **Implemente a lógica do modelo** dentro dos 5 arquivos, respeitando o contrato de
   entrada/saída de cada um (ver `docs/guides/models.md`). Regras que doem se
   ignoradas:
   - Só o `orchestrator.py` fala com tracking, via `pipeline/common/tracking.py` (Rule 01).
   - `prepare_data` pede o dado à interface `DataSource`; nunca sabe de onde vem.
   - Lógica que serviria a outros modelos vai para `pipeline/common/`, **não** para um 6º arquivo.

5. **Registre o modelo no entrypoint** que você usa (ou aponte o `--config` para o novo
   YAML). Para rodar:
   ```bash
   uv run python pipeline/entrypoints/run_local.py --config pipeline/config/<novo>.yaml
   ```

6. **Rode as cancelas antes de commitar:**
   ```bash
   python3 tools/check.py
   ```
   Elas verificam a anatomia via testes, a ausência de `import mlflow` fora do
   tracking (Rule 01) e o resto do contrato.

## Checklist de saída
- [ ] `pipeline/models/<novo>/` tem os 5 arquivos, com os nomes exatos.
- [ ] `pipeline/config/<novo>.yaml` existe e `name` bate com a pasta (Rule 05).
- [ ] Nenhum `import mlflow` fora do `orchestrator` → `pipeline/common/tracking.py`.
- [ ] Zero caminho/hiperparâmetro hardcoded (Rule 07).
- [ ] `python3 tools/check.py` verde.
