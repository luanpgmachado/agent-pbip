# PLAN

**Indice leve** Now/Next/Later. Aponta para:
- **Specs** (requisitos): `docs/specs/`
- **Plans** (execucao): `docs/plans/`

Fluxo: `spec -> plan -> implementar -> validar -> arquivar`.

## Workflow

- Regras/padroes: `AGENTS.md` (secao "Workflow (Spec -> Plan)").
- Specs (o que/por que): `docs/specs/`
- Plans (como/quando): `docs/plans/`

## Now

- `contexto-obsidian`: organizar camada humana Obsidian sem poluir specs/plans operacionais.
  - Plan: `docs/plans/contexto-obsidian.md`
  - Vault: `PINK/Dashboard Desospitalizacao - Hub.md`
  - Status: vault `PINK/` estruturado; `obsidian` CLI segue indisponivel no PATH, entao edicoes sao Markdown direto no vault.

- `DEV-225`: ligar visuais estaticos do `dashboard_template.html` ao `initDashboard` via JSON/DAX.
  - Specs legado/contrato: `docs/specs/prompt2_frontend.md`, `docs/specs/prompt3_modelagem.md`, `docs/specs/dashboard_tecnico_manutencao.md`
  - Schema/linhagem: `docs/References/notebook/NOTEBOK.md` (`docs/specs/SQL_INDICADORES.md` depreciado)
  - Guia medidas/cards: `docs/GUIA_MEDIDAS_DASHBOARD_V2.md`
  - Plan: `docs/plans/DEV-225.md`
  - Status: contrato JSON compacto ativo (`meta` + arrays `Indicador 02/06/13/14/15`), medidas `JSON*` decompostas, `HTML Dashboard` injeta `initDashboard(payload)`, cards calculados no HTML, `dashboard_template_v2.html` em uso.
  - `2026-05-07`: flags `FL_ACERTO_*` aceitam `S`, `1` e `1.0000000000`; cards V2 compactados; guia criado; contexto limpo para `NOTEBOK.md` como fonte de schema.
  - `2026-05-07`: decisao `PINK/01-Decisoes/DEC - Acuracia Dashboard V2.md` executada; Dashboard V2 usa `INDICADOR_PERCENTUAL_ACURACIA` como acuracia oficial na Visao Geral, strip e matriz; `FL_ACERTO_TOLERANCIA` fica apenas como apoio operacional.

- `DEV-226`: analisar aderencia PBIP ao `prompt1_modelagem.md` e corrigir lacunas.
  - Spec: `docs/specs/prompt1_modelagem.md`
  - Plan: `docs/plans/DEV-226.md`
  - Status: testes pendentes (sessao sem MCP, id `019db521-8b0b-7a50-844a-a850994cd011`) executados `2026-04-22`; erro PBIP reproduzido e corrigido no TMDL (`Indicador 14[CD_SETOR_ATENDIMENTO_RETORNO]` normaliza `''` para `null` antes de cast `Int64`); `ConnectFolder` voltou; schema `Indicador 12` atualizado `2026-04-23` para `NR_ATENDIMENTO/NM_PACIENTE/DS_SETOR_ATENDIMENTO/CD_CID/NM_RESPONSAVEL_PENDENCIA/DS_AREA_PENDENCIA/DS_STATUS_PENDENCIA` com propagacao para `relationships`, DAX e specs; conexoes M dos Indicadores 02/06/12/13/14/15 migradas `2026-04-23` de Excel local para DW PostgreSQL (`192.168.6.2:5432`, database `prohmdw`, schema `public`); falta reabrir no Desktop/Fabric e repetir validacao final.

- `SPEC-001`: template de especificacao em perguntas para melhorias visuais.
  - Spec: `docs/specs/spec-001-melhorias-visual.md`
  - Plan: `docs/plans/SPEC-001.md`
  - Status: template-base criado `2026-05-06`, pronto para preenchimento.
- `SPEC-002`: correcao critica do calendario oficial unico.
  - Spec: `docs/specs/spec-002-correcao-calendario-oficial.md`
  - Plan: `docs/plans/SPEC-002.md`
  - Status: implementacao textual aplicada `2026-05-07`: Auto Date/Time desligado no `model.tmdl`, `dim_calendario[dt_data]` marcado `isKey: true`, `53` relationships/variations de `LocalDateTable_*` removidos, `54` arquivos auto removidos; validacao textual passou; falta abrir no Desktop/Fabric e validar refresh/filtros.
- `SPEC-003`: documentar/aplicar chaves explicitas nas dimensoes.
  - Spec: `docs/specs/spec-003-chaves-explicitas-dimensoes.md`
  - Plan: `docs/plans/SPEC-003.md`
  - Status: spec criada `2026-05-07` a partir de `_review/index.html`; implementacao pendente.
- `SPEC-004`: parametrizar fontes locais, reduzir dependencia de caminhos absolutos.
  - Spec: `docs/specs/spec-004-parametrizar-fontes-locais.md`
  - Plan: `docs/plans/SPEC-004.md`
  - Status: spec criada `2026-05-07` a partir de `_review/index.html`; implementacao pendente.
- `SPEC-005`: adicionar `description:` formal nas medidas.
  - Spec: `docs/specs/spec-005-descricoes-medidas-tmdl.md`
  - Plan: `docs/plans/SPEC-005.md`
  - Status: spec criada `2026-05-07` a partir de `_review/index.html`; implementacao pendente.
- `SPEC-006`: adicionar descricoes de papel e granularidade nas tabelas.
  - Spec: `docs/specs/spec-006-descricoes-tabelas-granularidade.md`
  - Plan: `docs/plans/SPEC-006.md`
  - Status: spec criada `2026-05-07` a partir de `_review/index.html`; implementacao pendente.
- `references-notebooks`: referencias externas e segundo cerebro dos notebooks de engenharia.
  - Referencias: `docs/References/REFERENCES.md`, `docs/References/notebook/NOTEBOK.md`
  - Plan: `docs/plans/references-notebooks.md`
  - Status: fonte atual de schema/linhagem. `docs/specs/SQL_INDICADORES.md` virou alias legado `2026-05-07`.

## Next

- Reabrir PBIP no Desktop/Fabric, repetir validacao funcional DEV-226 (filtros cruzados, datas, payloads no `DASHBOARD`).
- Reabrir PBIP pos-`SPEC-002`, confirmar Auto Date/Time desligado, atualizar modelo, validar filtros temporais sem recriar `LocalDateTable_*`.
- Implementar `SPEC-003` a `SPEC-006` em ondas pequenas: chaves de dimensoes, fontes locais, descricoes de medidas e tabelas.
- Validar tela compacta DEV-225 (filtros HTML + cards + tabela), ajustar `maxRows` se lento.
- Planejar evolucao do `drawerDetalhe` (nesta release segue mock).

## Later

- Padronizar naming de containers e `render*()` para novos indicadores/secoes.
