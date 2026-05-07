`docs/References/` — external reference files for dashboard desospitalizacao indicators. Not primary PBIP sources. Origin: notebooks, SQLs, DW exports, business rule/schema docs.

## Como usar

- Use `docs/References/notebook/NOTEBOK.md` como segundo cerebro dos notebooks de engenharia.
- Use os arquivos `.py` em `docs/References/notebook/` como referencia de construcao das tabelas, nao como alvo de alteracao do PBIP.
- Preserve nomes reais de tabelas, colunas, `PIPELINE_NAME`, `PK_NATURAL` e trechos SQL quando documentar regras de indicador.
- Quando um indicador do dashboard estiver nomeado como `Indicador NN`, consulte o mapa em `NOTEBOK.md` para encontrar o nome tecnico real do notebook.
- `docs/specs/SQL_INDICADORES.md` e apenas alias legado. Nao manter schemas paralelos ali.

## Tipos de arquivo esperados

- Notebooks exportados como `.py`.
- Queries SQL de referencia.
- Dicionarios ou contratos auxiliares de engenharia.
- Evidencias de validacao de fonte, quando ajudarem a explicar regra de indicador.

## Regra de manutencao

Ao adicionar nova referencia: atualizar este indice ou criar secao em `docs/References/notebook/NOTEBOK.md` quando material explicar tabela, schema ou regra de indicador.