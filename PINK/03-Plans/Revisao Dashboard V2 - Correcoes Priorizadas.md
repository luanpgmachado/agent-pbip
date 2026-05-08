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
- Apresentacao analisada: [docs/ui/homologação v1.pptx](../../docs/ui/homologação%20v1.pptx)
- Modelo semantico: [powerbi/pbip/Desospitalizacao_Projeto_2026_03_25.SemanticModel](../../powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel)
- Guia de medidas: [docs/GUIA_MEDIDAS_DASHBOARD_V2.md](../../docs/GUIA_MEDIDAS_DASHBOARD_V2.md)
- Decisao pendente: [[../01-Decisoes/DEC - Acuracia Dashboard V2|DEC - Acuracia Dashboard V2]]

## Estado

- Status: recomendacoes consolidadas; acuracia executada com fonte oficial definida.
- Proximo passo: validacao visual/funcional final no Power BI Desktop.
- Bloqueios: link publicado exige login Power BI; validacao via browser parou na tela `Entrar | Microsoft Power BI` sem inserir credenciais.

## Evidencias

- Fato observado: `homologação v1.pptx` e a ultima versao visual de referencia para homologacao.
- Fato observado: pacote PPTX nao trouxe comentarios nem notes acessiveis.
- Fato observado via MCP: modelo local tem 16 tabelas, 32 medidas em `_Medidas` e 24 relacionamentos.
- Fato observado: arquivo PBIP esta acessivel aberto e pronto para ser acessado via MCP.
- Fato observado via MCP em 2026-05-07: 1 instancia Power BI Desktop ativa na porta `49754`, janela `Desospitalização_Projeto_2026_03_25`.
- Fato observado via MCP em 2026-05-07: DAX `INFO.MEASURES()` retornou 32 medidas.
- Fato observado via MCP em 2026-05-07: medida `[HTML Dashboard]` validou e executou prefixo HTML com sucesso.
- Fato observado via prints de homologacao: cards executivos ainda estavam altos/largos, status TAT sobrepunha texto e payload/DIAG ainda apareciam no rodape.
- Fato observado via browser em 2026-05-07: relatorio publicado redirecionou para SSO Power BI; sem credenciais, nao foi possivel inspecionar a pagina renderizada publicada.

## Correcoes seguras automaticas

- [x] Corrigir label do ranking TAT para usar descricao de setor/grupo, nao codigo bruto.
- [x] Suavizar peso visual de cards criticos para reduzir excesso de vermelho.
- [x] Melhorar card unico de Planejamento para nao ficar largo/desbalanceado.
- [x] Criar classe CSS para textos longos em summary cards, removendo estilos inline.
- [x] Melhorar quebra do card "Top setores de saida UTI".
- [x] Melhorar quebra do card "CID que mais perde dias".
- [x] Renomear status TAT ou ajustar regra para deixar claro se mede media TAT ou % acima SLA.
- [x] Ocultar linha tecnica `payload` e bloco `Diagnóstico técnico` do rodape na visao de homologacao.
- [x] Compactar largura/altura dos KPI cards para reduzir ocupacao visual.
- [x] Corrigir estouro visual do pill de status no ranking TAT.
- [x] Refatorar Visao Geral para grid 2 colunas sem faixas vazias: Eficiencia, Seguranca, Planejamento e ranking TAT na primeira dobra; heatmap abaixo em largura cheia.
- [x] Reverter agrupamento visual e deixar somente os 6 KPI cards em faixa horizontal, usando a aba Acuracia como referencia de densidade.

## Decisao executada

Ver [[../01-Decisoes/DEC - Acuracia Dashboard V2|DEC - Acuracia Dashboard V2]].

Decisao:

- Acuracia oficial do dashboard usa `INDICADOR_PERCENTUAL_ACURACIA`.
- `FL_ACERTO_TOLERANCIA` fica como apoio operacional, nao KPI executivo.

Motivo:

- Divergencia entre KPI executivo e strip/matriz foi removida na execucao anterior.

## Backlog recomendado

### Alta

- Acuracia contraditoria entre Visao Geral e aba Acuracia. Resolvido.
- Ranking TAT exibindo codigos como `13.0000000000`. Resolvido.

### Media

- Campo `IE_READMISSAO_8_30_DIAS` existe no modelo, mas nao aparece no JSON Readmissao.
- Vermelho critico domina hierarquia visual.
- Retorno UTI mostra `Eventos totais` igual a `Eventos <= 48h`; precisa nota mais explicita.

### Baixa

- Textos longos em cards de UTI/outliers precisam quebra visual controlada.
- CSS tem camada antiga + nova; consolidar quando houver janela de refactor.

## Validacao final esperada

- [x] Abrir Power BI Desktop com PBIP ativo.
- [x] Confirmar `[HTML Dashboard]` usando `dashboard_template_v2.html`.
- [ ] Validar Visao Geral versus abas com mesmo filtro.
- [ ] Testar filtros internos: data, estabelecimento, setor, medico.
- [ ] Expandir matrizes e validar pill de nivel.
- [ ] Conferir se payload nao foi truncado sem aviso executivo.
