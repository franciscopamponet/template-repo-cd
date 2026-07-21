# Rule 06 — Plataforma é opcional

**Faça:** manter o núcleo funcionando com `platform/` **inexistente**. Se o toggle for
Não, o `init.py` poda `platform/` e o repo continua rodando.
**Não faça:** importar qualquer coisa de `platform/` a partir do núcleo (`pipeline/config/`,
`pipeline/data/`, `pipeline/models/`, `pipeline/common/`, `pipeline/entrypoints/`). Nenhum caminho de código do núcleo pode
quebrar por falta de `platform/`.
