# tests/

## Para que serve
Os testes são uma **rede de segurança automática**. Em vez de conferir tudo na mão a
cada mudança, você roda um comando e eles verificam sozinhos, em segundos, uma pergunta:
**"o esqueleto ainda funciona e ainda segue as próprias regras?"**

Se uma mudança quebrou alguma coisa, os testes avisam **na hora** — antes de virar
problema no projeto de verdade.

## O que eles provam
- O **pipeline roda** de ponta a ponta (treina e gera métricas).
- O **`tools/init.py` funciona**: copiar o esqueleto → montar o projeto sem quebrar,
  nos dois toggles (com e sem Databricks).
- As **regras de arquitetura** foram respeitadas (o núcleo não importa de `platform/`,
  o manifesto está em sync, etc.).

## Como rodar
```bash
uv run pytest            # só os testes
python3 tools/check.py   # os testes + ruff + as 4 cancelas (o mesmo conjunto do CI)
```

**Quando rodar:** não é um ritual de "toda sessão". Você roda quando **mexeu no código
e vai commitar** — não ao abrir o projeto nem só para ler/explorar. E mesmo assim não é
obrigatório: o **CI** roda tudo isso sozinho a cada push no GitHub e barra o merge se
algo quebrou. Rodar local é só para pegar o erro **mais cedo**, em segundos, em vez de
esperar o CI falhar depois do push.

## O que tem aqui
- `conftest.py` — dado sintético + config de teste, reaproveitados pelos outros.
- `test_core.py` — o núcleo compartilhado (config, splits, fábrica de fonte de dados).
- `test_exemplo_modelo.py` — o pipeline do modelo de referência, ponta a ponta.
- `test_gen_conda.py` — o gerador do `conda.yaml` e a checagem de sync.
- `test_init.py` — o scaffolder (`init.py`), rodando de verdade em cópias temporárias.
- `test_invariante_plataforma.py` — prova que o núcleo roda sem a pasta `platform/`.
- `test_smoke.py` — checagem mínima de fumaça (o pacote importa).

> **Cancelas ≠ testes:** as "cancelas" são os `tools/check_*.py` (regras de arquitetura);
> os testes são a suíte pytest (o código funciona). O `tools/check.py` e o CI rodam as
> duas coisas juntas.
