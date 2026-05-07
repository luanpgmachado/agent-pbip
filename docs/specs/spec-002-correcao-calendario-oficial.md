# SPEC-002 - Correcao critica do calendario oficial

## 1) Identificacao

- Nome curto: `SPEC-002` - Consolidar `dim_calendario` como calendario oficial unico.
- Origem: auditoria local em `_review/index.html`, gerada em `2026-05-07`.
- Severidade: Critica.
- Status: Implementacao textual aplicada; validacao funcional no Power BI Desktop/Fabric pendente.
- Arquivo de plano: `docs/plans/SPEC-002.md`.

## 2) Problema

Modelo tem dimensao temporal oficial (`dim_calendario`), mas Auto Date/Time ligado e calendarios automaticos ainda presentes.

Evidencias no PBIP:

- `model.tmdl` contem `annotation __PBI_TimeIntelligenceEnabled = 1`.
- `53` arquivos `LocalDateTable_*.tmdl`.
- `1` arquivo `DateTableTemplate_*.tmdl`.
- `53` blocos `variation Variation` apontando para `LocalDateTable_*`.
- `53` referencias `defaultHierarchy` para hierarquias automaticas.
- `53` relacionamentos para `LocalDateTable_*` em `relationships.tmdl`.
- `dim_calendario[dt_data]` com `isUnique`, mas sem `isKey: true`.

## 3) Objetivo

Tornar `dim_calendario` unica dimensao temporal confiavel, removendo dependencias de calendarios automaticos e eliminando risco de filtros/visuais usarem hierarquias de data erradas.

Resultado esperado:

- Unico calendario oficial para analises temporais.
- Auto Date/Time desligado no TMDL e no Power BI Desktop antes do publish.
- Colunas de data dos fatos sem `variation Variation` para `LocalDateTable_*`.
- Relacionamentos temporais explicitos contra `dim_calendario[dt_data]`.

## 4) Escopo

Dentro do escopo:

- Alterar `model.tmdl` para desabilitar Auto Date/Time.
- Marcar `dim_calendario[dt_data]` como chave formal (`isKey: true`) e manter `summarizeBy: none`.
- Remover tabelas `LocalDateTable_*` e `DateTableTemplate_*` do modelo.
- Remover referencias `ref table LocalDateTable_*` e `ref table DateTableTemplate_*` de `model.tmdl`.
- Remover relacionamentos para `LocalDateTable_*` em `relationships.tmdl`.
- Remover blocos `variation Variation` apontando para `defaultHierarchy: LocalDateTable_*` nas tabelas de negocio.
- Revisar colunas de data com ou sem relacionamento explicito com `dim_calendario`.
- Validar filtros temporais do dashboard.

Fora do escopo:

- Refatorar naming geral do modelo.
- Documentar medidas sem `description:`.
- Resolver caminhos locais de origem de dados.
- Remover relacionamentos inativos nao relacionados a estrategia temporal.
- Alterar medidas de negocio sem necessidade causada pela consolidacao temporal.

## 5) Arquivos impactados

- `powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition/model.tmdl`
- `powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition/relationships.tmdl`
- `powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition/tables/dim_calendario.tmdl`
- `powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition/tables/Indicador 02.tmdl`
- `powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition/tables/Indicador 06.tmdl`
- `powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition/tables/Indicador 13.tmdl`
- `powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition/tables/Indicador 14.tmdl`
- `powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition/tables/Indicador 15.tmdl`
- Todos os arquivos `LocalDateTable_*.tmdl` e `DateTableTemplate_*.tmdl` gerados automaticamente.

## 6) Regras de implementacao

1. Inventario antes da remocao:
   - listar cada coluna de data com `variation Variation`;
   - mapear relacionamentos atuais contra `dim_calendario`;
   - classificar cada data como `principal`, `secundaria/inativa`, `atributo sem relacionamento` ou `campo tecnico/formatado`.
2. Nao criar relacionamento para toda coluna de data automaticamente.
3. Manter ativo apenas relacionamento temporal principal por fato.
4. Datas alternativas em medidas: manter relacionamento inativo, exigir `USERELATIONSHIP()`.
5. Campos formatados (`*_FMT`) ou datas tecnicas sem analise temporal: remover somente dependencia de calendario automatico.
6. Remover arquivos `LocalDateTable_*` somente apos remover refs, relationships e variations correspondentes.
7. Desligar Auto Date/Time no Power BI Desktop antes de publicar.

## 7) Estrategia temporal proposta

Relacionamentos principais:

- `'Indicador 02'[DT_PRESCRICAO] -> dim_calendario[dt_data]`
- `'Indicador 06'[DT_ENTRADA] -> dim_calendario[dt_data]`
- `'Indicador 13'[DT_ALTA_REAL] -> dim_calendario[dt_data]`
- `'Indicador 14'[DT_SAIDA_ORIGEM] -> dim_calendario[dt_data]`
- `'Indicador 15'[DT_ENTRADA_RETORNO_UTI] -> dim_calendario[dt_data]`

Relacionamento secundario existente:

- `'Indicador 13'[DT_EVENTO_PREVISAO] -> dim_calendario[dt_data]`, inativo.

Decisao pendente:

- Confirmar se datas de TAT do `Indicador 02` (`DT_EVENTO_FINAL`, `DT_COLETA_DATA`, `DT_LIBERACAO`, etc.) precisam relacionamento inativo + medida dedicada, ou ficam como atributo/coluna de detalhe.

## 8) Criterios de aceite

- `rg "__PBI_TimeIntelligenceEnabled = 1"` sem ocorrencias.
- `rg "LocalDateTable_"` sem ocorrencias em `definition/`.
- `rg "DateTableTemplate_"` sem ocorrencias em `definition/`.
- `rg "defaultHierarchy: LocalDateTable_"` sem ocorrencias.
- `rg "variation Variation"` sem blocos ligados a calendario automatico.
- `dim_calendario[dt_data]` com `isKey: true`, `isUnique` e `summarizeBy: none`.
- `relationships.tmdl` com somente relacionamentos temporais intencionais contra `dim_calendario`.
- PBIP abre no Power BI Desktop/Fabric sem recriar `LocalDateTable_*`.
- Refresh sem erro.
- Filtros por data continuam afetando indicadores esperados no dashboard.
- Medidas com datas alternativas usam `USERELATIONSHIP()` explicitamente.

## 9) Plano de validacao

Validacao textual:

- Executar buscas `rg` dos criterios de aceite.
- Confirmar ausencia de `LocalDateTable_*.tmdl` e `DateTableTemplate_*.tmdl`.
- Revisar `relationships.tmdl` para garantir nenhum relacionamento de negocio nao temporal perdido.

Validacao funcional:

- Abrir `Desospitalização_Projeto_2026_03_25.pbip` no Power BI Desktop/Fabric.
- Desligar Auto Date/Time nas opcoes do Desktop.
- Atualizar modelo.
- Validar pagina `DASHBOARD` com filtro de data.
- Validar cards executivos e tabelas detalhadas de TAT, permanencia, acuracia, readmissao e UTI.
- Publicar somente se Desktop nao regenerar tabelas automaticas.

## 10) Riscos e mitigacoes

- Risco: Power BI Desktop regenerar `LocalDateTable_*` ao abrir PBIP.
  Mitigacao: desligar Auto Date/Time no Desktop antes de salvar/publicar; reexecutar busca textual apos save.

- Risco: remover relacionamento automatico usado implicitamente por visual antigo.
  Mitigacao: validar visuais por pagina; substituir hierarquia automatica por campos de `dim_calendario`.

- Risco: ambiguidade ao relacionar varias datas do mesmo fato.
  Mitigacao: um relacionamento ativo por fato; datas alternativas inativas com `USERELATIONSHIP()`.

- Risco: data tecnica/formatada virar relacionamento indevido.
  Mitigacao: classificar datas antes de criar novos relacionamentos; campos `*_FMT` nao guiam calendario oficial.

## 11) Changelog

- `2026-05-07`: spec criada da issue critica da auditoria `_review/index.html` e validacao textual no PBIP.
- `2026-05-07`: implementacao textual aplicada no PBIP: Auto Date/Time desligado no TMDL, `dim_calendario[dt_data]` marcado como chave, `LocalDateTable_*`/`DateTableTemplate_*`, refs, relationships e variations removidos. Validacao funcional no Desktop/Fabric pendente.