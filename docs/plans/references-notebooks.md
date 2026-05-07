# Plano - References e Segundo Cerebro dos Notebooks

## Objetivo

Documentar notebooks externos de engenharia usados como referencia para construir indicadores de desospitalizacao no Power BI.

## Checklist

- [x] Mapear notebooks `.py` em `docs/References/notebook/`.
- [x] Registrar mapa `Indicador NN` do dashboard para `PIPELINE_NAME` real.
- [x] Documentar objetivo, fontes, chave natural, logica principal e schema por tabela.
- [x] Marcar diferencas entre nomes dos notebooks e nomes simplificados no PBIP.
- [x] Criar indice `docs/References/REFERENCES.md`.
- [x] Referenciar `REFERENCES.md` e `NOTEBOK.md` em `AGENTS.md` e `CLAUDE.md`.
- [x] Atualizar `PLAN.md` com plano transversal.
- [x] Depreciar `docs/specs/SQL_INDICADORES.md` como dicionario paralelo.

## Validacao

- [x] Confirmar busca textual dos seis indicadores em `docs/References`.
- [x] Confirmar referencias globais em `AGENTS.md`, `CLAUDE.md` e `PLAN.md`.
- [x] Confirmar por escopo do patch que nenhum notebook, TMDL, JSON ou dashboard foi alterado.

## Status

Implementado 2026-05-07, mudanca documental transversal, sem ticket Linear. Atualizacao extra 2026-05-07: `SQL_INDICADORES.md` reduzido a alias legado; `NOTEBOK.md` permanece fonte de schema/linhagem. `git status` nao executavel — diretorio fora de repositorio Git.