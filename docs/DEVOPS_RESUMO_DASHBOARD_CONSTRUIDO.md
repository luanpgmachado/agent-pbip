# Resumo Executivo e Tasks DEVOPS - Dashboard Desospitalizacao

Funcao na governanca: handoff/release notes para DEVOPS. Nao fonte de verdade de schema, DAX ou contrato. Para manutencao ativa, usar:
- Schema/linhagem: `docs/References/notebook/NOTEBOK.md`
- Contrato HTML/payload: `docs/specs/dashboard_tecnico_manutencao.md`
- Medidas/cards V2: `docs/GUIA_MEDIDAS_DASHBOARD_V2.md`
- Execucao/historico fino: `docs/plans/DEV-225.md` e `docs/plans/DEV-226.md`

## 1) Resumo executivo (o que foi construido)

Base de entrega:
- Projeto PBIP com dashboard HTML unico, dinamico, filtravel, alimentado por payload JSON gerado em DAX.
- Modelo semantico com fatos dos Indicadores 02, 06, 12, 13, 14 e 15, com ajustes de relacionamento, tipagem e estrategia de data.
- Front-end `dashboard_template.html` conectado ao payload compacto (`meta` + arrays por indicador), sem dependencia de cards mockados.

Arquitetura implementada:
1. `dashboard_template.html` contem layout, estilo e logica JS.
2. `_HTML_Base` injeta HTML no modelo (estrategia em partes para release).
3. Medidas DAX `JSON*` serializam dados por indicador.
4. `JSON Dashboard Compacto` agrega payload final.
5. `HTML Dashboard` injeta `initDashboard(payload)` no visual HTML Content.

Capacidades entregues:
- Filtros internos no HTML: data inicial/final, estabelecimento, setor e medico.
- Cards executivos e operacionais recalculados no cliente a partir dos dados filtrados.
- Abas de detalhe: Permanencia, Readmissao, Retorno UTI, Acuracia, TAT Exames e Outliers.
- Heatmap Setor x CID revisado para percentual de casos acima da media do grupo.
- Payload com metadados de controle (`maxRows`, totais reais, truncamento por indicador).

## 2) Regras de negocio e calculo por indicador

### Indicador 02 - TAT Exames
- Grao base: prescricao/exame.
- Elegibilidade no dashboard: `DT_PRESCRICAO`, `DT_EVENTO_FINAL` e `TAT_HORAS` nao nulos.
- Regras:
  - `Total Exames`: contagem de exames concluidos elegiveis.
  - `Media TAT (h)`: media de `TAT_HORAS` na base elegivel.
  - `Mediana TAT (h)`: mediana de `TAT_HORAS` na base elegivel.
  - `% Exames Acima SLA`: exames com `TAT_HORAS > 24` / `Total Exames`.
- Segmentacao de dominio para gargalo: `CD_DOMINIO` (LABORATORIO/IMAGEM).

### Indicador 06 - Permanencia
- Grao base: atendimento.
- Regras:
  - `Total Atendimentos`: contagem de linhas do indicador.
  - `Media Permanencia (dias)`: media de `QT_DIA_PERMANENCIA`.
  - `Mediana Permanencia (dias)`: mediana de `QT_DIA_PERMANENCIA`.
  - `Pacientes Fora da Curva`: `QT_DIA_PERMANENCIA > MEDIA_QT_DIA_PERMANENCIA_SETOR_CID`.
  - `% Fora da Curva`: fora da curva / total de atendimentos.
  - `Desvio Medio Permanencia (dias)`: media de `(QT_DIA_PERMANENCIA - MEDIA_QT_DIA_PERMANENCIA_SETOR_CID)`.
- Benchmark setor+CID vem do SQL, reaproveitado no PBI.

### Indicador 12 - Outliers e Pendencias
- Grao base: 1 linha por `NR_ATENDIMENTO` outlier (fato operacional derivado do Indicador 06).
- Regras no dashboard:
  - Contagem de pacientes fora da curva consolidada por atendimento.
  - Desvio medio operacional usando `DIAS_ACIMA_MEDIA`.
- Logica base de outlier e pendencias vem do SQL (nao recalculada em DAX linha a linha).

### Indicador 13 - Acuracia da Previsao de Alta
- Grao base: atendimento.
- Campos-base: `QT_DIF_DIAS_PREVISTO_REAL`, `FL_ACERTO_EXATO`, `FL_ACERTO_TOLERANCIA`, `INDICADOR_PERCENTUAL_ACURACIA`.
- Regras:
  - `Acuracia Alta Exata`: `%` de linhas com `FL_ACERTO_EXATO = "1"`.
  - `Acuracia Alta Tolerancia`: `%` de linhas com `FL_ACERTO_TOLERANCIA = "1"`.
  - `Acuracia Alta (%)`: media por atendimento de `INDICADOR_PERCENTUAL_ACURACIA`, convertida para escala percentual.
  - `Erro Medio/Mediano`: agregado absoluto de `QT_DIF_DIAS_PREVISTO_REAL`.
- Escolha da previsao oficial e diferenca base herdadas do SQL.

### Indicador 14 - Readmissao 7/30 dias
- Grao base: internacao de origem elegivel (nao grao de retorno).
- Regras:
  - `Taxa Readmissao 7 Dias` = `count(IE_READMISSAO_7_DIAS="S") / count(IE_DENOMINADOR_7_DIAS="S")`.
  - `Taxa Readmissao 30 Dias` = `count(IE_READMISSAO_30_DIAS_TOTAL="S") / count(IE_DENOMINADOR_30_DIAS="S")`.
- Numeradores/denominadores e janelas 7/30 prontos do SQL.

### Indicador 15 - Retorno UTI 48h
- Grao base: evento de retorno UTI < 48h.
- Regras:
  - `Retorno UTI 48h`: contagem de `IE_READMISSAO_UTI_48H = "S"`.
  - `Media Horas Retorno UTI`: media de `QT_HORAS_ATE_RETORNO_UTI` para eventos com flag `S`.
- Cadeia de evento UTI e janela de 48h tratadas no SQL.

## 3) Tasks para lancamento no DEVOPS (ja executadas)

Formato sugerido: 1 task por item abaixo.

| Titulo da task | Descricao breve | Evidencias principais |
|---|---|---|
| Modelagem: migrar fatos para DW PostgreSQL | Migracao das conexoes M dos Indicadores 02/06/12/13/14/15 de Excel local para DW (`prohmdw`, schema `public`). | `docs/plans/DEV-226.md`, `powerbi/pbip/.../tables/Indicador 02.tmdl`, `Indicador 06.tmdl`, `Indicador 12.tmdl`, `Indicador 13.tmdl`, `Indicador 14.tmdl`, `Indicador 15.tmdl` |
| Modelagem: corrigir tipagem e robustez do Indicador 14 | Correcao de abertura PBIP com normalizacao de `CD_SETOR_ATENDIMENTO_RETORNO` antes de cast `Int64` (tratamento de string vazia/null). | `docs/plans/DEV-226.md`, `powerbi/pbip/.../tables/Indicador 14.tmdl` |
| Modelagem: ajustar relacionamentos criticos dos indicadores | Ajustes de relacionamento e estrategia de data (Indicador 12 por atendimento; Indicador 13 com data principal + secundaria inativa; Indicador 15 por data de retorno UTI). | `docs/plans/DEV-226.md`, `powerbi/pbip/.../definition/relationships.tmdl` |
| Modelagem: atualizar schema do Indicador 12 | Renomeacao de colunas do Indicador 12 para contrato final e propagacao em relacionamentos, DAX e specs. | `docs/plans/DEV-226.md`, `docs/References/notebook/NOTEBOK.md`, `powerbi/pbip/.../tables/Indicador 12.tmdl` |
| DAX KPI: implementar medidas executivas TAT/Permanencia | Criacao/ajuste de `Total Exames`, `Media TAT`, `Mediana TAT`, `% Exames Acima SLA`, `Media/Mediana Permanencia`, `% Fora da Curva`. | `powerbi/pbip/.../tables/_Medidas.tmdl` |
| DAX KPI: implementar medidas de Acuracia, Readmissao e UTI | Implementacao de medidas de acuracia (exata/tolerancia/erro), taxas de readmissao 7/30 e retorno UTI 48h. | `powerbi/pbip/.../tables/_Medidas.tmdl` |
| DAX JSON: estruturar payload por indicador | Refatoracao para medidas independentes (`JSON Meta Dashboard`, `JSON TAT Exames`, `JSON Permanencia`, `JSON Acuracia Alta`, `JSON Readmissao`, `JSON Retorno UTI`) e agregador `JSON Dashboard Compacto`. | `docs/specs/prompt3_modelagem.md`, `powerbi/pbip/.../tables/_Medidas.tmdl` |
| DAX JSON: incluir metadados de governanca do payload | Inclusao de `meta.maxRows`, totais por indicador e flags de truncamento para controle de performance e rastreabilidade. | `powerbi/pbip/.../tables/_Medidas.tmdl` |
| Frontend: reescrever dashboard HTML compacto e dinamico | Pagina unica `dashboard` com consumo do payload JSON, sem dependencia de mock para blocos principais. | `dashboard_template.html`, `docs/plans/DEV-225.md` |
| Frontend: habilitar filtros internos e recalculo dos cards | Filtros por periodo/estabelecimento/setor/medico aplicados sobre arrays dos indicadores, refletindo em cards e tabelas. | `dashboard_template.html` |
| Frontend: implementar detalhes por aba e badges analiticos | Tabelas de detalhe para TAT, permanencia, readmissao, UTI, acuracia e outliers; enrich de campos derivados de risco/severidade. | `dashboard_template.html`, `powerbi/pbip/.../tables/_Medidas.tmdl` |
| Frontend: ajustar heatmap de permanencia | Mudanca de metrica para `% casos acima da media` por setor+CID, com semaforo e tratamento de baixa amostra. | `dashboard_template.html`, `docs/plans/DEV-225.md` |
| Hardening: corrigir inconsistencias de TAT e render defensivo | Alinhamento de criterio de conclusao TAT em medidas executivas + ajuste defensivo de render da aba TAT para reduzir tela em branco. | `docs/plans/DEV-225.md`, `powerbi/pbip/.../tables/_Medidas.tmdl`, `dashboard_template.html` |
| Documentacao tecnica: manutencao e release do dashboard | Criacao do guia tecnico de manutencao DASH e snippet de release `_HTML_Base` (P1/P2/P3). | `docs/specs/dashboard_tecnico_manutencao.md`, `docs/specs/_HTML_Base_release_snippet.m` |

## 4) Escopo atual consolidado (resumo para abertura no DEVOPS)

- Status: dashboard funcional com payload DAX + render HTML dinamico.
- Indicadores cobertos: 02, 06, 13, 14, 15 (apoio operacional do 12).
- Governanca de payload: ativa (`meta`, truncamento, limite por tabela).
- Pendente: validacao final em Power BI Desktop/Fabric apos refresh completo do ambiente cliente.