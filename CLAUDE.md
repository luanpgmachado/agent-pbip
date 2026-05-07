# CLAUDE.md

Orientações ao Claude Code (claude.ai/code) neste repositório.

## Visão Geral do Projeto

Dashboard Power BI de **Desospitalização** para Santa Casa. Monitora 6 indicadores clínicos. Formato: `.pbip` (PBIP = Power BI Project, formato texto para controle de versão).

**Sem sistema de build.** Edite `.tmdl` / `.json` direto; Power BI Desktop ou Fabric lê ao abrir.

## Papel dos Arquivos

| Arquivo/Pasta | Finalidade |
|---|---|
| `*.pbip` | Manifesto — lista artefatos do relatório |
| `*.Report/definition/` | Relatório: páginas, visuais, temas |
| `*.SemanticModel/definition/` | Modelo: tabelas, medidas, relacionamentos |
| `*.SemanticModel/definition/tables/*.tmdl` | Um TMDL por tabela |
| `*.SemanticModel/definition/relationships.tmdl` | 24 relacionamentos |
| `thema.json` | Cores tema personalizado (ProHM Lake - Verde) |
| `Indicador NN.xlsx` | Dados fonte por indicador (Power Query M) |
| `docs/specs/SQL_INDICADORES.md` | Legado/depreciado; usar `NOTEBOK.md` para schema/linhagem atual |
| `docs/specs/<ESPECIFICACOES>` | Spec funcional/técnica evergreen |
| `docs/specs/prompt2_frontend.md` | Spec UI/UX histórica; validar contra plan atual antes de usar |
| `docs/References/REFERENCES.md` | Índice de referências externas usadas na engenharia dos indicadores |
| `docs/References/notebook/NOTEBOK.md` | Segundo cérebro: linhagem, fontes, chaves naturais, schemas, mapa `Indicador NN` -> tabela real |
| `docs/GUIA_MEDIDAS_DASHBOARD_V2.md` | Dicionário rápido de cards/medidas/metas |
| `docs/DEVOPS_RESUMO_DASHBOARD_CONSTRUIDO.md` | Handoff/release notes DEVOPS; não usar como fonte de verdade |

Queries SQL fonte ficam em:
`C:\Users\luanp\OneDrive\Rep-2026\projjetta\Clientes\STA CASA\workspace_colab\proj-prohm-stcasa\docs\sql_indicador_*.sql`

Referências externas copiadas: `docs/References/`. Para entender montagem de tabelas, comece por `docs/References/notebook/NOTEBOK.md`.

## Arquitetura do Modelo Semântico

**Esquema estrela, Tabular 1600 (Fabric/Premium).**

**Tabelas fato (carregadas):**
- `Indicador 02` — TAT de exames. Granularidade: 1 linha/prescrição. Métricas: `tat_horas`, `tat_resultado_horas`, `tat_coleta_horas`
- `Indicador 06` — Permanência (LOS). Granularidade: 1 linha/atendimento. Métricas: `qt_dia_permanencia`, `media_permanencia`, `mediana_permanencia`

**Mapa de notebooks:** ver `docs/References/notebook/NOTEBOK.md` para `Indicador 02/06/12/13/14/15` e dimensões auxiliares.

**Tabelas fato (pendentes):** Indicador 12, 13, 15

**Dimensões:**
- `dim_estabelecimento` — unidades/estabelecimentos
- `dim_pessoa` — médicos/colaboradores
- `dim_setor_atendimento` — setores hospitalares
- `dim_calendario` — dimensão de data (**não ativada nos relacionamentos**)

**Tabelas de data:** 22 tabelas `LocalDateTable_*` geradas automaticamente. `dim_calendario` existe, relacionamentos pendentes.

**Relacionamentos:** 24 total. Um inativo: `Indicador 02 ↔ Indicador 06` em `NR_PRONTUARIO`.

## Convenções de Nomenclatura

Prefixos de colunas:
- `CD_` — código/chave
- `DT_` — data/hora
- `NR_` — identificador numérico
- `QT_` — quantidade/métrica

Locale: `pt-BR` (culturas, formatos de data, nomes de medidas).

## Resumo da Especificação do Dashboard

5 seções (veja `docs/specs/prompt2_frontend.md`, validar contra `docs/plans/DEV-225.md`):
1. Cards de KPI
2. Gargalos
3. Pacientes críticos
4. Acurácia de alta
5. Readmissão

Filtros: período, estabelecimento, setor, especialidade, médico, CID, tipo internação, status paciente.

Cores: Verde = OK, Amarelo = Alerta, Vermelho = Crítico, Azul = Neutro.

Visuais: HTML Content visual (`htmlContent443BE3AD55E043BF878BED274D3A6855`), Advance Card, visuais PBI customizados.

## Status Atual (2026-04-20)

- Modelo: Indicadores 02 e 06 carregados, dimensões prontas, calendário não vinculado
- Pendente: Importar Indicadores 12, 13, 15; criar medidas DAX; construir frontend
- Ver `docs/plans/DEV-225.md`, `docs/plans/DEV-226.md`, `docs/References/notebook/NOTEBOK.md`, `docs/GUIA_MEDIDAS_DASHBOARD_V2.md` para estado atual.

## Trabalhando com TMDL

TMDL é texto puro — edite direto. Padrões:

```tmdl
// Adicionar medida a uma tabela
measure 'Nome Medida' = DAX_EXPRESSION
    formatString: "#,##0.00"
    displayFolder: "KPIs"

// Adicionar relacionamento (em relationships.tmdl)
relationship 'TableA'[KeyCol] -> 'TableB'[KeyCol]
    crossFilteringBehavior: bothDirections
```

Ao adicionar relacionamentos com `dim_calendario`, desative `LocalDateTable_*` existentes primeiro para evitar ambiguidade.