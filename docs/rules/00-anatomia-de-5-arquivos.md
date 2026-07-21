# Rule 00 — Anatomia de 5 arquivos é contrato inegociável

Todo modelo mora em `pipeline/models/<nome>/` e tem **exatamente** estes 5 arquivos:

- `prepare_data.py`
- `build_model.py`
- `train.py`
- `evaluate_model.py`
- `orchestrator.py`

**Faça:** manter os 5, com esses nomes exatos, em todo modelo.
**Não faça:** adicionar um 6º arquivo na pasta do modelo, renomear, fundir ou omitir
qualquer um dos 5. Lógica extra vai para `pipeline/common/`, não para dentro de `pipeline/models/<nome>/`.
