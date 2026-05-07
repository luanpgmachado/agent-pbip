---
title: Revisao Dashboard V2 - Correcoes Priorizadas
aliases:
  - Correcoes Dashboard V2
tags:
  - dashboard/desospitalizacao
  - plan/revisao
  - powerbi/pbip
status: em-revisao
data: 2026-05-07
---

# Revisao Dashboard V2 - Correcoes Priorizadas

## Link operacional

- Plan repo: [docs/plans/repaginacao-dashboard-template.md](../../docs/plans/repaginacao-dashboard-template.md)
- HTML atual: [dashboard_template_v2.html](../../dashboard_template_v2.html)
- Apresentacao analisada: [docs/ui/UI V2.pptx](../../docs/ui/UI%20V2.pptx)
- Modelo semantico: [powerbi/pbip/Desospitalizacao_Projeto_2026_03_25.SemanticModel](../../powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel)
- Guia de medidas: [docs/GUIA_MEDIDAS_DASHBOARD_V2.md](../../docs/GUIA_MEDIDAS_DASHBOARD_V2.md)
- Decisao pendente: [[../01-Decisoes/DEC - Acuracia Dashboard V2|DEC - Acuracia Dashboard V2]]

## Estado

- Status: recomendacoes consolidadas; aguardando decisao sobre acuracia antes de mexer na regra.
- Proximo passo: aplicar correcoes seguras de visual/HTML e decidir fonte oficial da acuracia.
- Bloqueios: Power BI Desktop nao estava ativo; MCP validou TMDL local, mas nao executou DAX em conexao offline.

## Evidencias

- Fato observado: `UI V2.pptx` tem 8 slides como imagens raster.
- Fato observado: pacote PPTX nao trouxe comentarios nem notes acessiveis.
- Fato observado via MCP: modelo local tem 16 tabelas, 32 medidas em `_Medidas` e 24 relacionamentos.
- Fato observado via MCP: 0 instancias locais Power BI Desktop no momento da revisao.
- Fato observado via MCP: conexao offline nao suporta `dax_query_operations Validate`.

## Correcoes seguras automaticas

- [ ] Corrigir label do ranking TAT para usar descricao de setor/grupo, nao codigo bruto.
- [ ] Suavizar peso visual de cards criticos para reduzir excesso de vermelho.
- [ ] Melhorar card unico de Planejamento para nao ficar largo/desbalanceado.
- [ ] Criar classe CSS para textos longos em summary cards, removendo estilos inline.
- [ ] Melhorar quebra do card "Top setores de saida UTI".
- [ ] Melhorar quebra do card "CID que mais perde dias".
- [ ] Renomear status TAT ou ajustar regra para deixar claro se mede media TAT ou % acima SLA.

## Decisao manual antes de alterar regra

Ver [[../01-Decisoes/DEC - Acuracia Dashboard V2|DEC - Acuracia Dashboard V2]].

Pergunta objetiva:

- Acuracia oficial do dashboard deve usar `INDICADOR_PERCENTUAL_ACURACIA` ou `FL_ACERTO_TOLERANCIA`?

Motivo:

- Visao Geral mostra `Acuracia Alta 83,4% OK`.
- Aba Acuracia mostra `Acertos 0`, `0,0% acuracia`, `Critico`.
- Isso indica divergencia entre KPI executivo e strip/matriz.

## Backlog recomendado

### Alta

- Acuracia contraditoria entre Visao Geral e aba Acuracia.
- Ranking TAT exibindo codigos como `13.0000000000`.

### Media

- Campo `IE_READMISSAO_8_30_DIAS` existe no modelo, mas nao aparece no JSON Readmissao.
- Vermelho critico domina hierarquia visual.
- Retorno UTI mostra `Eventos totais` igual a `Eventos <= 48h`; precisa nota mais explicita.

### Baixa

- Textos longos em cards de UTI/outliers precisam quebra visual controlada.
- CSS tem camada antiga + nova; consolidar quando houver janela de refactor.

## Validacao final esperada

- [ ] Abrir Power BI Desktop com PBIP ativo.
- [ ] Confirmar `[HTML Dashboard]` usando `dashboard_template_v2.html`.
- [ ] Validar Visao Geral versus abas com mesmo filtro.
- [ ] Testar filtros internos: data, estabelecimento, setor, medico.
- [ ] Expandir matrizes e validar pill de nivel.
- [ ] Conferir se payload nao foi truncado sem aviso executivo.

