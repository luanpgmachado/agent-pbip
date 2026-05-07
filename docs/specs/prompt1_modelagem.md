Status: legado. Use como spec historica de modelagem DEV-226; validar contra `docs/plans/DEV-226.md` e `docs/References/notebook/NOTEBOK.md` antes de executar.

Responsável por MODELAGEM de dados em Power BI aberto: Desospitalização_Projeto_2026_03_25.

## Contexto inicial

Modelo possui:

### Tabelas fato
- indicador 2
- indicador 6
- indicador 12 
- indicador 13 
- indicador 15

### Dimensões
- Dim estabelecimento
- Dim setor atendimento
- Dim pessoa
- Dim calendário
- Dim Cid

### Relacionamentos
- Relacionamentos entre indicadores existem, mas precisam validação
- Investigar por que indicador 12 não está sendo relacionado


## Sua missão

NÃO criar visual ainda.

Trabalho:

1. Entender modelo atual
2. Validar dados
3. Ajustar relacionamentos (se necessário)
4. Definir estratégia de datas (se necessário)
5. Criar medidas DAX necessárias se não existirem

---

---

## ⚠️ PADRÃO OBRIGATÓRIO — MEDIDAS PARA HTML INTERATIVO

Criar medidas DAX diretamente no modelo Power BI via MCP.

Todas medidas retornam **strings JSON válidas** para uso no visual HTML interativo.

### Regras técnicas obrigatórias para TODAS medidas:

- Não definir dataType
- Usar GROUPBY + SUMX(CURRENTGROUP()) para agregações
- Envolver toda FORMATT() numérico em SUBSTITUTE(..., ",", ".") para garantir ponto decimal (locale PT-BR)
- Usar "" aspas duplas para escapar strings no DAX
- Nunca usar aspas simples
- Validar cada medida com EVALUATE ROW() confirmando output começa com {{ e é JSON válido

---

## Etapa 1 — Análise do modelo

Para cada tabela fato:

### Identifique:
- grão da tabela
- chave principal
- colunas de data
- colunas numéricas (métricas)
- colunas de dimensão (joins)

### Monte mentalmente:
- o que já está pronto no SQL
- o que NÃO precisa ser recriado em DAX

---

## Etapa 2 — Entendimento dos indicadores

### Indicador 2 (TAT)
- grão: 1 linha por prescrição
- métricas já prontas:
  - tat_horas
  - tat_resultado_horas
  - tat_coleta_horas
- já possui fallback de evento (resultado vs coleta)

👉 NÃO recalcular TAT em DAX

Deve:
- criar agregações (soma, média)
- validar duplicidade após joins
- Separar LABORATORIO vs IMAGEM com coluna `CD_DOMINIO`

---

### Indicador 6 (Permanência)
- possui:
  - qt_dia_permanencia
  - média e mediana por setor/CID (via janela SQL)

👉 Cuidado:
Médias do SQL podem quebrar com filtros no Power BI.

Avaliar:
- manter como coluna
OU
- recriar como medida DAX dinâmica

---

### Indicador 12 (Outliers e pendências)
- construído em cima do indicador 6
- grão: 1 linha por NR_ATENDIMENTO outlier
- possui:
  - qt_dia_permanencia (mesma lógica do indicador 6)
  - média e mediana por setor/CID
  - dias acima da média e da mediana
  - flag_outlier
  - qt_pendencias e principais pendências consolidadas
  - responsável, área e status da principal pendência

👉 NÃO recalcular em DAX lógica base de permanência/outlier que já vem do SQL

👉 Cuidado:
Indicador nasce filtrado para outliers e consolidado por atendimento.
Se relacionamento por NR_ATENDIMENTO falhar, filtros e cruzamentos com restante do modelo quebram.

Avaliar:
- manter flag, excessos e pendências como fato operacional pronto
OU
- recriar apenas medidas DAX agregadas para contagem, soma de excessos e ranking de outliers respeitando filtros

Deve:
- validar se grão final continua 1 linha por atendimento
- reaproveitar referência Setor + CID do indicador 6 sem duplicar regra base
- verificar relacionamento com calendário, setor, CID e paciente por meio do atendimento

---

### Indicador 13 (Acurácia da previsão de alta)
- grão: 1 linha por NR_ATENDIMENTO
- possui:
  - dt_prevista_alta escolhida a partir do histórico oficial
  - dt_evento_previsao
  - dt_alta_real
  - qt_dif_dias_previsto_real
  - fl_acerto_exato
  - fl_acerto_tolerancia
  - indicador_percentual_acuracia (0 ou 100 por linha)

👉 NÃO recalcular em DAX escolha da previsão oficial nem diferença base entre alta prevista e alta real

👉 Cuidado:
Pode haver múltiplas previsões para mesmo atendimento.
SQL já prioriza última previsão até alta real e usa fallback técnico quando necessário.

Avaliar:
- manter flags e diferença em dias como base analítica pronta
OU
- criar apenas medidas DAX agregadas para acurácia exata, acurácia com tolerância, erro médio e erro mediano

Deve:
- validar relacionamento principal por NR_ATENDIMENTO
- relacionar médico, setor e paciente sem duplicar atendimento
- usar dt_alta_real como desfecho principal e dt_evento_previsao como data analítica secundária

---

### Indicador 14 (Readmissão hospitalar 7 e 30 dias)
- grão: 1 linha por internação índice elegível
- possui:
  - nr_atendimento_origem como chave analítica
  - possível nr_atendimento_retorno (somente o primeiro retorno)
  - qt_dias_ate_readmissao e qt_horas_ate_readmissao
  - flags de denominador 7 dias e 30 dias
  - flags de numerador para 7 dias, 8 a 30 dias e 30 dias total
  - faixa de readmissão consolidada

👉 NÃO recalcular em DAX identificação do primeiro retorno nem flags de janela 7/30 dias

👉 Cuidado:
Indicador não nasce no grão do retorno, e sim da internação de origem.
Se houver duplicidade por paciente ou por retorno, taxa fica incorreta.

Avaliar:
- manter denominadores e numeradores prontos no fato
OU
- criar medidas DAX apenas para compor taxas e cortes analíticos respeitando flags do SQL

Deve:
- validar relacionamento por atendimento de origem e por paciente
- definir se análise temporal principal usa dt_competencia_origem ou dt_saida_origem
- preservar filtros parametrizados de transferência administrativa e óbito no denominador

---

### Indicador 15 (Readmissão UTI 48h)
- grão: 1 linha por evento de retorno à UTI em menos de 48h
- possui:
  - nr_atendimento
  - nr_prescricao âncora (quando encontrada)
  - dt_saida_uti
  - dt_entrada_retorno_uti
  - qt_horas_ate_retorno_uti
  - ie_readmissao_uti_48h
  - setor de saída e setor de retorno
  - médico, especialidade e paciente associados ao evento

👉 NÃO recalcular em DAX cadeia UTI -> setor não UTI -> retorno UTI nem janela de 48h

👉 Cuidado:
SQL já faz segmentação de movimentos e descarta movimentos técnicos inválidos.
Misturar movimentos unitários com eventos consolidados gera dupla contagem.

Avaliar:
- manter fato somente com eventos confirmados de retorno UTI < 48h
OU
- criar medidas DAX agregadas para contagem de eventos, tempo médio, mínimo e máximo de retorno

Deve:
- validar se calendário principal será dt_entrada_retorno_uti ou dt_saida_uti
- relacionar setor, médico, especialidade e paciente sem expandir grão do evento
- conferir se classificação de UTI continua coerente com `CD_CLASSIF_SETOR = '4'`

---
## Etapa 3 — Relacionamentos

Validar:
- cardinalidade
- direção de filtro
- consistência de chaves

Corrigir se necessário.

---

## Etapa 4 — Estratégia de calendário

Definir qual data cada fato usa:

### Indicador 2:
Escolher entre:
- dt_prescricao
- dt_resultado_real
- dt_evento_final

### Indicador 6:
Escolher entre:
- dt_entrada
- dt_entrada_unidade
- dt_alta_medico
- dt_previsto_alta

### Indicador 13:
Escolher entre:
- dt_alta_real
- dt_prevista_alta
- dt_evento_previsao

### Indicador 14:
Escolher entre:
- dt_competencia_origem
- dt_saida_origem
- dt_entrada_retorno
- dt_referencia

### Indicador 15:
Escolher entre:
- dt_saida_uti
- dt_entrada_retorno_uti
- dt_referencia

Se necessário:
- usar relacionamento inativo
- usar USERELATIONSHIP()

---

## Etapa 5 — Medidas DAX

Criar medidas para:

### Executivas
- soma TAT (h)
- media TAT (h)
- média permanência
- mediana permanência
- readmissão 7 dias
- readmissão 30 dias
- retorno UTI 48h
- acurácia da alta

### Operacionais
- pacientes fora da curva
- desvio permanência
- % exames acima SLA
- erro médio previsão alta
- erro mediano previsão alta

---

## Regras importantes

- NÃO duplicar lógica que já vem do SQL
- Preferir medidas ao invés de colunas
- Garantir funcionamento com filtros
- Nomear medidas de forma clara
- Separar medidas base e finais

---

## Entregável esperado

Deixar pronto:

- modelo consistente
- relacionamentos validados
- estratégia de calendário definida
- medidas DAX criadas
