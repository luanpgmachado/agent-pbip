---
title: DEC - Acuracia Dashboard V2
aliases:
  - Decisao Acuracia Dashboard V2
tags:
  - decisao/dashboard
  - dashboard/desospitalizacao
  - powerbi/dax
status: decidido
data: 2026-05-07
---

# DEC - Acuracia Dashboard V2

## Decisao

- Data: 2026-05-07
- Decisor(es): Luan
- Decisao: Usar `INDICADOR_PERCENTUAL_ACURACIA` como fonte oficial da acuracia executiva no Dashboard V2.

## Contexto

- Problema: a Visao Geral e a aba Acuracia usam leituras diferentes para o mesmo indicador executivo.
- Fato observado: Visao Geral exibe `Acuracia Alta 83,4% OK`.
- Fato observado: aba Acuracia exibe `Acertos 0`, `0,0% acuracia`, status `Critico`.
- Fato tecnico: `computeKpis()` calcula acuracia por media de `INDICADOR_PERCENTUAL_ACURACIA`.
- Fato tecnico: `renderAcurStrip()` e `MATRIX_CONFIG.acur` contam `FL_ACERTO_TOLERANCIA`.

## Alternativas consideradas

- Usar `INDICADOR_PERCENTUAL_ACURACIA` como fonte oficial para KPI, strip e matriz.
- Usar `FL_ACERTO_TOLERANCIA` como fonte oficial e revisar o KPI da Visao Geral.
- Manter as duas metricas, mas renomear claramente: "Acuracia percentual" e "Acertos por tolerancia".

## Recomendacao

Usar uma fonte oficial unica no dashboard executivo.

Preferencia tecnica: `INDICADOR_PERCENTUAL_ACURACIA`, porque ja sustenta a Visao Geral e a medida `_Medidas[Acuracia Alta (%)]`. Se a regra de negocio oficial for tolerancia, corrigir tambem a Visao Geral para nao mostrar `83,4% OK` quando a aba operacional indica `0,0%`.

## Impacto operacional

- Arquivos do repo afetados:
  - [dashboard_template_v2.html](../../dashboard_template_v2.html)
  - [powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition/tables/_Medidas.tmdl](../../powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition/tables/_Medidas.tmdl)
  - [docs/GUIA_MEDIDAS_DASHBOARD_V2.md](../../docs/GUIA_MEDIDAS_DASHBOARD_V2.md)
- Spec/plan relacionado:
  - [docs/plans/repaginacao-dashboard-template.md](../../docs/plans/repaginacao-dashboard-template.md)
- Validacao necessaria:
  - Power BI Desktop ativo.
  - Comparar Visao Geral e aba Acuracia com mesmo filtro.
  - Validar medida `_Medidas[Acuracia Alta (%)]` contra payload JSON.

## Execucao

- `2026-05-07`: implementado em `dashboard_template_v2.html`.
- Visao Geral, strip da aba Acuracia e matriz passaram a usar `INDICADOR_PERCENTUAL_ACURACIA` como leitura principal.
- `FL_ACERTO_TOLERANCIA` permanece visivel apenas como apoio operacional (`Acertos tolerancia`), sem definir o KPI executivo.
- Documentacao sincronizada em `docs/GUIA_MEDIDAS_DASHBOARD_V2.md`, `docs/plans/repaginacao-dashboard-template.md` e `PLAN.md`.
