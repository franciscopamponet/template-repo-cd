# notebooks/

Aqui ficam os **notebooks** (`.ipynb`) do projeto — o trabalho de investigação e
preparação de dados: **análises exploratórias, tratamento de bases e merges**.

## Para que serve
- **Análise exploratória (EDA):** entender a base, ver distribuições, achar problemas.
- **Tratamento e limpeza** de dados.
- **Merges e junções** de bases antes de virarem entrada do pipeline.

O dado bruto que você analisa mora em [`../data/raw/`](../data/raw/) (gitignored) —
aponte os notebooks para lá.

## Boas práticas
- **Notebook é rascunho, não produção.** Quando uma lógica de preparação amadurece e
  vira parte do pipeline de verdade, mova-a para
  `pipeline/models/<modelo>/prepare_data.py` (ou para `pipeline/common/` se for
  reutilizável entre modelos). O notebook explora; o pipeline executa de forma
  reprodutível (anatomia de 5 arquivos — Rule 00).
- **Limpe as saídas pesadas** das células antes de commitar, para manter o diff leve.
  (`.ipynb_checkpoints/` já é ignorado pelo git.)
