# Plano - SPEC-002 (Correcao critica do calendario oficial)

## Objetivo

Caminho seguro para consolidar `dim_calendario` como calendario oficial unico e remover Auto Date/Time/`LocalDateTable_*` do modelo PBIP.

## Checklist

- [x] Verificar issue critica no review HTML.
- [x] Confirmar evidencias no PBIP/TMDL local.
- [x] Criar spec operacional em `docs/specs/spec-002-correcao-calendario-oficial.md`.
- [x] Inventariar colunas de data com `variation Variation`.
- [x] Classificar datas por papel: principal, secundaria/inativa, atributo ou tecnica.
- [x] Ajustar `dim_calendario[dt_data]` com `isKey: true`.
- [x] Desligar Auto Date/Time no TMDL.
- [x] Remover refs, relationships, variations e arquivos `LocalDateTable_*`/`DateTableTemplate_*`.
- [ ] Validar PBIP no Power BI Desktop/Fabric sem recriacao de calendario automatico.

## Evidencias iniciais

- `model.tmdl`: `annotation __PBI_TimeIntelligenceEnabled = 1`.
- `tables/`: `53` arquivos `LocalDateTable_*.tmdl`.
- `tables/`: `1` arquivo `DateTableTemplate_*.tmdl`.
- `tables/`: `53` referencias `defaultHierarchy: LocalDateTable_*`.
- `relationships.tmdl`: `53` relacionamentos para `LocalDateTable_*`.
- `dim_calendario[dt_data]`: tem `isUnique`, sem `isKey: true`.

## Status

Implementacao textual aplicada em `2026-05-07`. Removidos `53` relacionamentos para `LocalDateTable_*`, `53` blocos `variation Variation`, `54` arquivos automaticos (`53` `LocalDateTable_*` + `1` `DateTableTemplate_*`). Validacao textual passou; validacao funcional no Power BI Desktop/Fabric pendente.

## Inventario e classificacao

Relacionamentos principais oficiais mantidos:

- `'Indicador 02'[DT_PRESCRICAO] -> dim_calendario[dt_data]`
- `'Indicador 06'[DT_ENTRADA] -> dim_calendario[dt_data]`
- `'Indicador 13'[DT_ALTA_REAL] -> dim_calendario[dt_data]`
- `'Indicador 14'[DT_SAIDA_ORIGEM] -> dim_calendario[dt_data]`
- `'Indicador 15'[DT_ENTRADA_RETORNO_UTI] -> dim_calendario[dt_data]`

Relacionamento secundario/inativo mantido:

- `'Indicador 13'[DT_EVENTO_PREVISAO] -> dim_calendario[dt_data]` com `isActive: false`

Colunas com `variation Variation` removida:

| Tabela | Coluna | Classificacao |
|---|---|---|
| Indicador 02 | DT_LIBERACAO | atributo TAT sem relacionamento |
| Indicador 02 | DT_LIBERACAO_MEDICO | atributo TAT sem relacionamento |
| Indicador 02 | DT_ENTRADA | atributo assistencial sem relacionamento |
| Indicador 02 | DT_NASCIMENTO | atributo demografico sem relacionamento |
| Indicador 02 | DT_MESTRUACAO | atributo clinico sem relacionamento |
| Indicador 02 | DT_ULTIMA_DOSE | atributo clinico sem relacionamento |
| Indicador 02 | DT_VALIDADE_CARTEIRA | atributo administrativo sem relacionamento |
| Indicador 02 | DT_RESULTADO | atributo TAT sem relacionamento |
| Indicador 02 | DT_COLETA_DATA | atributo TAT sem relacionamento |
| Indicador 02 | DT_RESULTADO_ER | atributo TAT sem relacionamento |
| Indicador 02 | DT_LIBERACAO_ER | atributo TAT sem relacionamento |
| Indicador 02 | DT_PRESCRICAO_FMT | campo formatado/tecnico |
| Indicador 02 | DT_RESULTADO_PP_FMT | campo formatado/tecnico |
| Indicador 02 | DT_RESULTADO_ER_FMT | campo formatado/tecnico |
| Indicador 02 | DT_COLETA_FMT | campo formatado/tecnico |
| Indicador 02 | DT_RESULTADO_REAL | atributo TAT sem relacionamento |
| Indicador 02 | DT_RESULTADO_FMT | campo formatado/tecnico |
| Indicador 02 | DT_COLETA_REAL | atributo TAT sem relacionamento |
| Indicador 02 | DT_EVENTO_FINAL | atributo TAT sem relacionamento |
| Indicador 02 | DT_EVENTO_FINAL_FMT | campo formatado/tecnico |
| Indicador 02 | DT_RESULTADO_IMAGEM | atributo TAT sem relacionamento |
| Indicador 02 | DT_EXAME_IMAGEM | atributo TAT sem relacionamento |
| Indicador 02 | DT_LIBERACAO_IMAGEM | atributo TAT sem relacionamento |
| Indicador 02 | DT_APROVACAO_IMAGEM | atributo TAT sem relacionamento |
| Indicador 02 | DT_RESULTADO_IMAGEM_FMT | campo formatado/tecnico |
| Indicador 02 | DT_EXAME_IMAGEM_FMT | campo formatado/tecnico |
| Indicador 02 | DT_RESULTADO_LIBERACAO_ER | atributo TAT sem relacionamento |
| Indicador 02 | DT_LIBERACAO_ER_FMT | campo formatado/tecnico |
| Indicador 02 | DT_RESULTADO_LIBERACAO_ER_FMT | campo formatado/tecnico |
| Indicador 06 | DT_ENTRADA_UNIDADE | atributo detalhe sem relacionamento |
| Indicador 06 | DT_NASCIMENTO | atributo demografico sem relacionamento |
| Indicador 06 | DT_INICIO_HIGIENIZACAO | atributo operacional sem relacionamento |
| Indicador 06 | DT_HIGIENIZACAO | atributo operacional sem relacionamento |
| Indicador 06 | DT_PREVISTO_ALTA | atributo assistencial sem relacionamento |
| Indicador 06 | DT_ALTA_MEDICO | atributo assistencial sem relacionamento |
| Indicador 06 | dt_carga | campo tecnico |
| Indicador 12 | dt_carga | campo tecnico |
| Indicador 13 | DT_ALTA | atributo detalhe sem relacionamento |
| Indicador 13 | DT_SAIDA_REAL | atributo detalhe sem relacionamento |
| Indicador 13 | DT_PREVISTA_ALTA | atributo detalhe sem relacionamento |
| Indicador 13 | DT_EVENTO_PREVISAO | secundaria/inativa oficial mantida em `dim_calendario` |
| Indicador 13 | DT_ALTA_REAL | principal oficial mantida em `dim_calendario` |
| Indicador 13 | dt_carga | campo tecnico |
| Indicador 14 | DT_REFERENCIA | atributo detalhe sem relacionamento |
| Indicador 14 | DT_COMPETENCIA_ORIGEM | atributo detalhe sem relacionamento |
| Indicador 14 | DT_ENTRADA_ORIGEM | atributo detalhe sem relacionamento |
| Indicador 14 | DT_ENTRADA_RETORNO | atributo detalhe sem relacionamento |
| Indicador 14 | DT_SAIDA_BASE_RETORNO | atributo detalhe sem relacionamento |
| Indicador 14 | dt_carga | campo tecnico |
| Indicador 15 | DT_REFERENCIA | atributo detalhe sem relacionamento |
| Indicador 15 | DT_SAIDA_UTI | atributo detalhe sem relacionamento |
| Indicador 15 | DT_ENTRADA_RETORNO_UTI | principal oficial mantida em `dim_calendario` |
| Indicador 15 | dt_carga | campo tecnico |

## Evidencias de validacao textual

- `rg "__PBI_TimeIntelligenceEnabled = 1" powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition` sem ocorrencias.
- `rg "LocalDateTable_" powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition` sem ocorrencias.
- `rg "DateTableTemplate_" powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition` sem ocorrencias.
- `rg "defaultHierarchy: LocalDateTable_" powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition` sem ocorrencias.
- `rg "variation Variation" powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition` sem ocorrencias.
- `dim_calendario[dt_data]` contem `isUnique`, `isKey: true`, `summarizeBy: none`.
- Backups em `powerbi/pbip/bkp-pbip/` preservam estado antigo; nao fazem parte do PBIP ativo corrigido.

## Proximo passo

Abrir `Desospitalização_Projeto_2026_03_25.pbip` no Power BI Desktop/Fabric, confirmar Auto Date/Time desligado nas opcoes do arquivo, atualizar modelo, validar filtros temporais do dashboard.