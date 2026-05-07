# Guia Simplificado das Medidas - Dashboard V2

Apoio para apresentacao do dashboard de Desospitalizacao.

Funcao na governanca: dicionario rapido de cards, metas, flags e formulas simplificadas do `dashboard_template_v2.html`.

Atualizar quando mudar:
- card executivo ou card de aba;
- medida DAX usada pelo dashboard;
- campo do payload `JSON Dashboard Compacto`;
- meta operacional, semaforo ou regra de status;
- interpretacao de negocio apresentada ao cliente.

Nao usar como fonte de schema/linhagem. Usar `docs/References/notebook/NOTEBOK.md`.

## Visao geral

`dashboard_template_v2.html` mostra painel executivo com indicadores assistenciais calculados de cinco bases do modelo Power BI:

| Base no payload | Tema | Uso principal |
|---|---|---|
| `Indicador 02` | TAT de exames | tempo entre prescricao e resultado |
| `Indicador 06` | Permanencia | dias de internacao e comparacao Setor x CID |
| `Indicador 13` | Acuracia da alta | previsao de alta versus alta real |
| `Indicador 14` | Readmissao | retorno hospitalar em 7 e 30 dias |
| `Indicador 15` | Retorno UTI | retorno para UTI em ate 48h |

No Power BI, medida `_Medidas[HTML Dashboard]` junta HTML com payload `_Medidas[JSON Dashboard Compacto]`. JSON entrega linhas dos indicadores para HTML. Tela recalcula cards conforme filtros internos de data, estabelecimento, setor e medico.

## Metas e status visual

Status dos cards calculado no HTML comparando valor atual com meta operacional:

| Indicador | Meta | Regra |
|---|---:|---|
| Media TAT | `<= 24h` | menor e melhor |
| Permanencia media | `<= 7 dias` | menor e melhor |
| Mediana de permanencia | `<= 5 dias` | menor e melhor |
| Readmissao 7 dias | `<= 5%` | menor e melhor |
| Retorno UTI 48h | `<= 10 eventos` | menor e melhor |
| Acuracia Alta | `>= 80%` | maior e melhor |

Leitura do semaforo:

| Status | Como interpretar |
|---|---|
| `OK` | dentro da meta |
| `Atencao` | proximo da meta, mas ja em ponto de alerta |
| `Critico` | fora da meta com desvio relevante |

Indicadores menor-e-melhor: ate meta = `OK`; ate 15% acima = `Atencao`; acima disso = `Critico`.

Indicadores maior-e-melhor: igual ou acima da meta = `OK`; ate 85% da meta = `Atencao`; abaixo = `Critico`.

## Cards executivos

### Media TAT (exames)

Fonte: `Indicador 02`.

Formula simplificada:

```text
Media TAT = media de TAT_HORAS dos exames filtrados
```

Tempo medio em horas entre prescricao e resultado de exame. Menor e melhor. Meta: ate 24 horas.

Observacao:

Modelo Power BI tem medida `Média TAT (h)` considerando exames concluidos com `DT_EVENTO_FINAL` e `TAT_HORAS` preenchidos. No dashboard V2, card recalculado no HTML usando linhas do payload.

### Permanencia media

Fonte: `Indicador 06`.

Formula simplificada:

```text
Permanencia media = media de QT_DIA_PERMANENCIA dos atendimentos filtrados
```

Media de dias de internacao no periodo e filtros selecionados. Menor e melhor. Meta: ate 7 dias.

### Mediana de permanencia

Fonte: `Indicador 06`.

Formula simplificada:

```text
Mediana = valor central de QT_DIA_PERMANENCIA
```

Ponto central da distribuicao de permanencia. Reduz efeito de casos extremos. Menor e melhor. Meta: ate 5 dias.

### Readmissao 7 dias

Fonte: `Indicador 14`.

Formula simplificada:

```text
Readmissao 7 dias (%) =
  quantidade de linhas com IE_READMISSAO_7_DIAS = "S"
  /
  quantidade de linhas com IE_DENOMINADOR_7_DIAS = "S"
  * 100
```

Percentual de altas elegiveis com readmissao em ate 7 dias. Menor e melhor. Meta: ate 5%.

Observacao:

Denominador usa apenas altas maduras/elegiveis para janela de 7 dias.

### Retorno UTI 48h

Fonte: `Indicador 15`.

Formula simplificada:

```text
Retorno UTI 48h = contagem de linhas com IE_READMISSAO_UTI_48H = "S"
```

Quantidade de eventos de retorno para UTI em ate 48h apos saida. Menor e melhor. Meta: ate 10 eventos.

Observacao importante para o cliente:

Card e contagem de eventos, nao taxa percentual — dashboard ainda nao recebe denominador validado de saidas elegiveis da UTI.

### Acuracia Alta

Fonte: `Indicador 13`.

Formula simplificada:

```text
Acuracia Alta (%) = media de INDICADOR_PERCENTUAL_ACURACIA
```

Aderencia da previsao de alta a alta real. Maior e melhor. Meta: minimo 80%.

Decisao oficial `2026-05-07`:

```text
Acuracia executiva =
  media de INDICADOR_PERCENTUAL_ACURACIA
```

Visao Geral, strip da aba Acuracia e matriz usam a mesma leitura percentual. `FL_ACERTO_TOLERANCIA` pode aparecer como apoio operacional, mas nao define o numero executivo principal.

## Abas de detalhe

### Aba Visao Geral

Seis cards executivos em tres grupos:

| Grupo | Cards |
|---|---|
| Eficiencia operacional | Media TAT, Permanencia media, Mediana de permanencia |
| Seguranca / Qualidade | Readmissao 7 dias, Retorno UTI 48h |
| Planejamento | Acuracia Alta |

Cada card exibe:

- valor atual;
- comparacao com periodo anterior, quando disponivel;
- meta operacional;
- status `OK`, `Atencao` ou `Critico`;
- botao `Detalhes`, que navega para aba correspondente.

### Aba Permanencia

Fonte: `Indicador 06`.

Cards da aba:

| Card | Calculo |
|---|---|
| Atendimentos | total de linhas filtradas |
| Permanencia media | media de `QT_DIA_PERMANENCIA` |
| Referencia media | media de `MEDIA_QT_DIA_PERMANENCIA_SETOR_CID` |
| Acima da referencia | contagem de casos em que `QT_DIA_PERMANENCIA > MEDIA_QT_DIA_PERMANENCIA_SETOR_CID` |

Referencia Setor x CID = benchmark esperado para comparar permanencias de pacientes em perfis semelhantes. Caso acima da referencia = ficou mais dias que media esperada do grupo.

### Aba Readmissao

Fonte: `Indicador 14`.

Cards da aba:

| Card | Calculo |
|---|---|
| Volume elegivel (7d) | contagem de `IE_DENOMINADOR_7_DIAS = "S"` |
| Readm. <= 7 dias | contagem de `IE_READMISSAO_7_DIAS = "S"` e percentual sobre elegiveis |
| Dias medios ate readm. | media de `QT_DIAS_ATE_READMISSAO` |
| Readm. 8-30 dias | contagem de `IE_READMISSAO_8_30_DIAS = "S"`, quando campo existe no payload |

Mostra quantos pacientes retornaram apos alta e em quanto tempo. Foco executivo em readmissao 7 dias — janela mais sensivel.

### Aba Retorno UTI

Fonte: `Indicador 15`.

Cards da aba:

| Card | Calculo |
|---|---|
| Eventos totais | total de linhas filtradas |
| Eventos <= 48h | contagem de `IE_READMISSAO_UTI_48H = "S"` |
| Horas medias ate retorno | media de `QT_HORAS_ATE_RETORNO_UTI` |
| Top setores de saida UTI | setores com mais retornos, pela contagem de `DS_SETOR_SAIDA_UTI` |

Identifica retorno precoce a UTI e setores de origem mais associados ao evento.

### Aba Acuracia

Fonte: `Indicador 13`.

Cards da aba:

| Card | Calculo |
|---|---|
| Atendimentos analisados | total de linhas filtradas |
| Acuracia oficial | media de `INDICADOR_PERCENTUAL_ACURACIA` |
| Acertos tolerancia | contagem de `FL_ACERTO_TOLERANCIA` marcado como acerto, apenas apoio operacional |
| Atrasos | contagem de `QT_DIF_DIAS_PREVISTO_REAL > 0` |
| Antecipacoes | contagem de `QT_DIF_DIAS_PREVISTO_REAL < 0` |
| Diferenca media | media de `QT_DIF_DIAS_PREVISTO_REAL` |

Compara data prevista de alta com alta real. Alta depois da previsao = atraso. Alta antes = antecipacao. Acuracia oficial vem do percentual entregue em `INDICADOR_PERCENTUAL_ACURACIA`.

### Aba TAT Exames

Fonte: `Indicador 02`.

Matriz de detalhe:

| Coluna | Calculo |
|---|---|
| Prescricoes | contagem de `NR_PRESCRICAO` |
| TAT medio (h) | media de `TAT_HORAS` |
| Acima SLA 24h | contagem de linhas com `TAT_HORAS > 24` |
| Status | derivado do TAT medio versus SLA |

Localiza setores, CIDs, medicos, pacientes e prescricoes com maior tempo ate resultado.

### Aba Outliers

Fonte: `Indicador 06`.

Regra de entrada:

```text
Outlier = QT_DIA_PERMANENCIA > MEDIA_QT_DIA_PERMANENCIA_SETOR_CID
```

Cards da aba:

| Card | Calculo |
|---|---|
| Casos outlier | quantidade de casos acima da referencia |
| Dias excedentes (total) | soma de `QT_DIA_PERMANENCIA - MEDIA_QT_DIA_PERMANENCIA_SETOR_CID` |
| Setor que mais perde dias | setor com maior soma de dias excedentes |
| CID que mais perde dias | CID com maior soma de dias excedentes |

Mostra maiores desvios de permanencia, em dias, em relacao ao esperado para grupos comparaveis.

## Matrizes hierarquicas

Logica das tabelas de detalhe:

1. Agrupam linhas por dimensoes: setor, CID, medico, paciente, atendimento.
2. Calculam medidas por grupo: contagem, media, soma, contagem condicional.
3. Permitem expandir niveis do resumo ao detalhe.

Agregacoes usadas:

| Tipo | Explicacao |
|---|---|
| `count` | conta linhas do grupo |
| `avg` | calcula media numerica |
| `sum` | soma valores |
| `countIf` | conta linhas que atendem condicao |
| `gt_field` | compara dois campos da mesma linha, ex: permanencia real > referencia |

## Perguntas frequentes para apresentacao

### Por que alguns valores mudam quando filtro setor ou medico?

Dashboard recalcula cards usando apenas linhas que passam pelos filtros internos.

### Por que Retorno UTI aparece como numero e nao percentual?

Dashboard recebe eventos de retorno mas nao tem denominador validado de saidas elegiveis da UTI. Leitura correta = quantidade de eventos.

### O que e referencia Setor x CID?

Media de comparacao calculada na base para pacientes do mesmo setor e CID. Referencia esperada de permanencia.

### O que significa acuracia da alta?

Aderencia entre alta prevista e alta real. No Dashboard V2, leitura executiva oficial = media de `INDICADOR_PERCENTUAL_ACURACIA`.

### Por que o dashboard aceita `1.0000000000` como acerto?

DW pode entregar flag operacional de tolerancia como numero decimal textual. HTML trata `S`, `1` e `1.0000000000` como acerto apenas para o card secundario `Acertos tolerancia`; isso nao altera a acuracia executiva.

### O que significa diferenca positiva ou negativa na acuracia?

`QT_DIF_DIAS_PREVISTO_REAL > 0`: alta depois do previsto — atraso.

`QT_DIF_DIAS_PREVISTO_REAL < 0`: alta antes do previsto — antecipacao.

## Pontos de cuidado ao explicar

- Metas atuais definidas no HTML como parametros operacionais, nao em tabela dedicada de metas.
- Dashboard V2 calcula cards no navegador a partir do payload recebido do Power BI.
- Medidas DAX no modelo servem para analise e apoio; visual V2 prioriza recalculo no HTML para responder filtros internos.
- Se payload for limitado por performance, bloco `meta` do JSON pode indicar truncamento de linhas.
