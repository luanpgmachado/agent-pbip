# Plano Operacional — Dashboard de Desospitalização Eficiente

Status: legado. Use como spec historica UI/UX DEV-225; validar contra `docs/plans/DEV-225.md`, `docs/specs/dashboard_tecnico_manutencao.md` e `docs/GUIA_MEDIDAS_DASHBOARD_V2.md` antes de executar.

## 1. Objetivo
- Entregar dashboard de desospitalização orientado a decisão rápida, identificação de gargalos em até 5 segundos.
- Reduzir ambiguidade operacional para execução por agente de IA sem inferências críticas.
- Suportar intervenção imediata em casos críticos sem perda de contexto gerencial.

## 2. Contexto
- Desospitalização impacta diretamente giro de leitos e sustentabilidade financeira hospitalar.
- Dashboard deve priorizar ação operacional, não exibição de dados.
- Narrativa analítica em três níveis: gestão (macro), diagnóstico de gargalos (analítico) e intervenção (micro).
- Premissas técnicas:
  - Uso de `HTML Content` para componentes visuais customizados.
  - Uso do `thema.json` como fonte obrigatória de cores.
  - Regras de negócio devem evitar distorções estatísticas (ex.: "média da média").

## 3. Escopo
### Inclui
- Dashboard em dobras (KPIs, gargalos, outliers, acurácia e readmissão/UTI).
- Drawer lateral para análise 360º do paciente.
- Filtros globais e secundários.
- Regras de negócio críticas por indicador.
- Checklist de entrega com critérios verificáveis.

### Não inclui
- Definição de arquitetura de infraestrutura (gateway, rede, segurança, deploy).
- Modelagem física de banco e ETL detalhado.
- Cálculo de denominadores globais usando tabela pré-filtrada de outliers.

## 4. Estrutura da Solução
### 4.1 Primeira dobra — KPIs de gestão
- Exibir 6 cards com:
  - valor principal;
  - variação (`Δ`) versus período anterior;
  - meta;
  - status semafórico (verde/amarelo/vermelho).
- KPIs:
  - Média e Mediana de Permanência;
  - Taxa de Readmissão (7 e 30 dias);
  - Retorno UTI (48h);
  - Acurácia da Previsão de Alta.

### 4.2 Segunda dobra — Diagnóstico de gargalos
- Bloco esquerdo: eficiência de exames (ranking horizontal por TAT).
  - Abas: Laboratório, Imagem, Laudos.
  - Métricas obrigatórias: Volume, Tempo Médio, `% SLA`.
- Bloco direito: heatmap de permanência por Setor e CID.
  - Destacar Pacientes Ativos versus normalidade histórica.

### 4.3 Terceira dobra — Ação imediata
- Tabela de outliers de permanência (`permanência > média/mediana Setor+CID`).
- Sinalização obrigatória:
  - linha vermelha para criticidade extrema;
  - badges de pendências assistenciais concatenadas.
- Restrição obrigatória:
  - base de outliers é pré-filtrada e não compõe médias globais hospitalares.

### 4.4 Drawer lateral (drill-down)
- Ao clicar em paciente crítico, exibir:
  - histórico clínico e tempo de internação;
  - estimativa real vs. previsão;
  - histórico de readmissões;
  - pendências de exames.

### 4.5 Navegação e filtros
- Barra lateral com estado visual ativo/inativo.
- Filtros globais: Estabelecimento, Setor, Médico, Especialidade.
- Filtros secundários: CID, Status do Paciente, Faixa de Permanência.

### 4.6 Dobras analíticas complementares
- Indicador 13: acurácia de previsão por médico/setor.
- Indicadores 14/15: readmissão (7/30d) e retorno UTI 48h.

## 5. Requisitos Obrigatórios
- UX/UI:
  - interface clara com fundo claro (`off-white`/cinza claro);
  - evitar "painel de aeroporto" (excesso de estímulo simultâneo);
  - hierarquia tipográfica com números grandes apenas em KPIs principais;
  - ícones obrigatoriamente em `SVG`; `PNG` proibido.
- Layout:
  - grid e espaçamentos consistentes em todo dashboard;
  - alinhamento rigoroso para leitura rápida.
- Estilo visual:
  - aderência estrita ao `thema.json`;
  - cores vibrantes apenas para alertas.
- Interatividade:
  - todo visual deve permitir filtragem cruzada (clicável).

## 6. Regras de Negócio
### 6.1 Regras prioritárias
- Hierarquia de CID:
  1. Diagnóstico de Alta
  2. Referência
  3. Outros
- Regra de decisão rápida:
  - KPI principal identificável em até 5 segundos.

### 6.2 Regras por indicador
| Indicador | Regra de negócio obrigatória | Fonte/prioridade técnica |
|---|---|---|
| 02 - TAT Exames | `T0 = MIN(dt_prescricao)` por `nr_prescricao`; `dt_evento_final` (T2) por prioridade: `dt_resultado_imagem` > `dt_resultado_er` > `dt_coleta_data` (após T0) | Campos: `nr_prescricao`, `nr_atendimento`, `dt_prescricao`, `dt_resultado_er`, `dt_resultado_imagem`, `dt_evento_final`, `origem_evento_tat`, `tat_horas` |
| 06 - Permanência | `qt_dia_permanencia` calculada contra `SYSDATE`; CID principal por prioridade (Alta > Referência > Outros) | Campos: `nr_atendimento`, `nr_seq_interno`, `ie_ordem`, `dt_entrada`, `dt_alta_medico`, `qt_dia_permanencia`, `cd_setor_atendimento`, `cd_cid`, `media_qt_dia_permanencia_setor_cid`, `mediana_qt_dia_permanencia_setor_cid` |
| 12 - Outliers | `flag_outlier='S'` quando `qt_dia_permanencia` > média/mediana do grupo setor+CID; pendências consolidadas por atendimento | Campos: `nr_atendimento`, `nm_paciente`, `ds_setor_atendimento`, `cd_cid`, `qt_dia_permanencia`, `media_setor_cid`, `mediana_setor_cid`, `dias_acima_media`, `dias_acima_mediana`, `flag_outlier`, `qt_pendencias`, `ds_principais_pendencias`, `nm_responsavel_pendencia`, `ds_area_pendencia`, `ds_status_pendencia` |
| 13 - Acurácia | Diferença em dias `qt_dif_dias_previsto_real` entre `dt_prevista_alta` (última válida) e alta real (`dt_saida_real` fallback `dt_alta`); excluir cancelados | Campos: `nr_atendimento`, `dt_evento_previsao`, `dt_prevista_alta`, `dt_saida_real`, `dt_alta`, `qt_dif_dias_previsto_real`, `fl_acerto_exato`, `fl_acerto_tolerancia`, `indicador_percentual_acuracia` |
| 14 - Readmissão | Retorno = 1ª nova internação do mesmo paciente em 0–30d após `dt_saida_origem`; excluir óbito/transferência adm no denominador | Campos: `nr_atendimento_origem`, `dt_saida_origem`, `dt_entrada_retorno`, `qt_dias_ate_readmissao`, `ie_readmissao_7_dias`, `ie_readmissao_30_dias_total`, `ie_denominador_7_dias`, `ie_denominador_30_dias` |
| 15 - Retorno UTI | Padrão UTI -> não UTI -> UTI com `qt_horas_ate_retorno_uti` < 48h (UTI via `setor_atendimento.cd_classif_setor='4'`); descartar segmentos técnicos (entrada=saída) | Campos: `nr_atendimento`, `dt_saida_uti`, `dt_entrada_retorno_uti`, `qt_horas_ate_retorno_uti`, `ie_readmissao_uti_48h`, `cd_setor_atendimento`, `cd_setor_saida_uti` |

## 7. Fluxo de Execução
1. Implementar layout base com dobras e grid consistente.
2. Construir cards de KPI com `HTML Content` e semaforização.
3. Implementar bloco de gargalos (ranking TAT + heatmap Setor/CID).
4. Implementar tabela de outliers e badges de pendência.
5. Implementar drawer lateral com visão 360º do paciente.
6. Configurar filtros globais/secundários e navegação lateral.
7. Aplicar regras de negócio por indicador no back-end/medidas.
8. Validar integridade estatística (exclusões e bases pré-filtradas).
9. Revisar conformidade visual com `thema.json` e UX de 5 segundos.

## 8. Formato de Saída Esperado
- Entrega deve conter:
  - página(s) com dobras implementadas;
  - medidas e regras de negócio explicitadas por indicador;
  - componentes `HTML Content` usados (cards/badges);
  - checklist final preenchido (conforme seção 9).
- Organização mínima:
  - `Frontend`: telas, componentes, filtros, interações;
  - `Métricas`: definição de cada indicador e regras aplicadas;
  - `Validação`: evidências de testes funcionais e regras críticas.

## 9. Critérios de Aceite
- KPI principal localizável e compreensível em até 5 segundos.
- 6 cards de gestão exibem valor, `Δ`, meta e status semafórico.
- Ranking de TAT e heatmap Setor/CID funcionais com filtros.
- Tabela de outliers sinaliza criticidade e pendências de forma visível.
- Drawer lateral apresenta visão clínica completa do paciente crítico.
- Readmissão exclui óbitos/transferências administrativas corretamente.
- Retorno UTI descarta segmentos técnicos (tempo zero).
- Ícones 100% `SVG`.
- Layout respeita `thema.json` e mantém consistência de grid/espaçamento.
- Nenhuma métrica global usa indevidamente base pré-filtrada de outliers.

## 10. Exemplo
### Entrada (trecho narrativo)
- "Dashboard limpo, moderno, com foco em decisão rápida e análise de gargalos."

### Saída esperada (trecho operacional)
- "Dashboard deve usar fundo claro e hierarquia visual com destaque apenas para KPIs primários. Deve apresentar 3 níveis de leitura: gestão, gargalo e ação imediata. KPI principal identificável em até 5 segundos. Obrigatório exibir ranking de TAT por tipo de exame e heatmap Setor/CID com alerta de sobrecarga histórica."
