# Plano — Repaginar dashboard_template.html (storytelling executivo)

## Contexto

`dashboard_template.html` (1577 linhas) = HTML standalone embarcado em Power BI via measure `[HTML Dashboard]`. Payload `D` tem 5 fatos (Indicador 02, 06, 13, 14, 15) + meta. Lógica filtros/tabs/KPIs/heatmap/ranking/matrizes hierárquicas funciona. Mas:

- DIAG aparece como banner principal — cara de debug
- 6 KPIs sem agrupamento, sem microcopy, sem destaque crítico
- Sem resumo executivo no topo — usuário ignora gargalos principais
- Permanência/Readmissão/UTI/Acurácia/Outliers = só matriz crua
- Matriz mostra "Setor" no header da 1ª coluna mas níveis filhos viram CID/Médico/Paciente — ambíguo
- Sem badges de status, sem pills de nível
- Acentos pt-BR ausentes (Visão/Permanência/Acurácia)
- Readmissão sem numerador/denominador visíveis
- Retorno UTI sem horas médias / top setores
- Acurácia sem split acertos/atrasos/antecipações
- Outliers sem coluna dias excedentes

Repaginar visual, preservar lógica negócio. Entregável = cópia `dashboard_template_v2.html`.

## Arquivo alvo

- Criar: `dashboard_template_v2.html` (cópia editada do `dashboard_template.html`)
- Não tocar: `dashboard_template.html` original

## Restrições obrigatórias

- Preservar `initDashboard(cfg)`, `D`, `TABLES`, `SCHEMA`, `METAS`, `MATRIX_CONFIG`
- Preservar nomes campos payload (TAT_HORAS, QT_DIA_PERMANENCIA, IE_READMISSAO_7_DIAS, etc)
- **Não alterar IDs, atributos `data-*`, nomes de funções públicas** usadas pelo Power BI (`initDashboard`, `refresh`, `D`, `TABLES`, `SCHEMA`, `MATRIX_CONFIG`)
- HTML/CSS/JS puro, sem framework, sem CDN, sem libs externas
- Filtros/tabs/expand-collapse/Detalhes intactos
- Lógica SLA 24h, status meta, prevRange — não alterar
- Acessibilidade: contraste, foco, badges com texto+cor
- **`mxComputeAgg` permanece seguro**: somente `count`/`avg`/`sum`/`countIf`. Status/Risco/Tipo erro vão por **caminho de medida derivada separado** (`mxComputeDerived(records, derivedSpec)`), nunca dentro de `mxComputeAgg`.

## Mudanças por seção

### 1. Tokens CSS + base
Adicionar no `:root`: `--space-1..6`, `--radius-sm/md/lg`, `--shadow-soft`, `--ok-strong`, `--warn-strong`, `--bad-strong`, tipografia escalonada (`--fs-xs..xl`). Manter cores ProHM Lake. Contraste título: `--brand-blue` em headers de bloco — já existe, manter.

### 2. Topbar
Manter funcional. Apenas: corrigir título → "Desospitalização", subtítulo → "Visão Executiva — Plano Operacional". Espaçamento entre filtros.

### 3. Tabs
Renomear labels visuais (`data-tab` intocado): "Visão Geral", "Permanência", "Readmissão", "Retorno UTI", "Acurácia", "TAT Exames", "Outliers".

### 4. Resumo executivo (NOVO — Visão Geral)
Novo `.exec-summary` no topo da aba overview, antes do KPI grid:
- Headline dinâmica gerada por `buildExecHeadline(kpis)`: lista até 3 indicadores em status `bad`/`warn`
- **Texto fiel à métrica**, derivado de `defs[i].label` + status. Mensagens fixas:
  - `"Média TAT acima da meta"` (quando `mediaTat` bad/warn)
  - `"Permanência média acima da meta"` / `"Mediana de permanência acima da meta"`
  - `"Readmissão 7 dias acima da meta"`
  - `"Retorno UTI 48h acima da meta"`
  - `"Acurácia abaixo da meta"` (dir=high)
- Concatenação: `"Pontos de atenção: <m1>, <m2>, <m3>."` (no máx 3)
- Se tudo OK: `"Todos os indicadores dentro das metas operacionais."`
- **Não usar frases que sugiram regra linha a linha** (nada de "casos acima…")
- Visual: faixa horizontal, ícone de severidade global (• cor mais alta entre os KPIs) + texto

### 5. KPIs reagrupados
`.kpi-grid` reescrito: 3 grupos visuais:
- **Eficiência operacional**: Média TAT · Permanência média · Mediana permanência
- **Segurança / Qualidade**: Readmissão 7d · Retorno UTI 48h
- **Planejamento**: Acurácia Alta

Cada KPI ganha:
- microcopy (`hint`) "Quanto menor, melhor" / "Quanto maior, melhor" derivado de `meta.dir`
- badge textual: `OK` / `Atenção` / `Crítico` (não só cor)
- delta vs período anterior já existe — manter
- KPIs `bad` recebem `.kpi--emph` (borda mais forte, fundo `var(--bad-bg)` sutil no header)
- botão `Detalhes` preservado

Função `renderKpis(k, kPrev)` reescrita para emitir grupos com `<section class="kpi-group"><header>…</header><div class="kpi-grid">…</div></section>`.

### 6. DIAG colapsável
Tirar do topo. Mover para rodapé como `<details class="diag"><summary>Diagnóstico técnico</summary>…</details>`. Texto preservado, conteúdo populado igual no `refresh()`.

### 7. TAT (overview block + tabela)
- Ranking: cabeçalho com 3 colunas claras (TAT médio · volume · % > SLA 24h)
- Cada linha do ranking ganha pill de status: `Dentro SLA` (ok), `Atenção` (warn), `Crítico` (bad)
- Barra horizontal mais alta (6px), cor segundo `tatClass`
- Na aba TAT (matriz): adicionar coluna `Status` derivada de TAT médio (ok/warn/bad)
- Não alterar threshold 24h

### 8. Permanência (heatmap + matriz)
- Heatmap: legenda mais clara — texto: "% casos acima da média de referência (Setor × CID)"
- Tooltip header "% acima → maior = mais casos acima do benchmark do grupo"
- Matriz Permanência: adicionar coluna `Status` via **caminho derivado separado** (`mxComputeDerived`), não dentro de `mxComputeAgg`:
  - status calculado pós-grupo, lendo agregações já computadas (`perm_media`, `benchmark`)
  - <=1.0× benchmark → `Normal` (pill ok)
  - <=1.3× → `Elevado` (pill warn)
  - >1.3× → `Crítico` (pill bad)
- Mesmo padrão na matriz TAT (Status pill por linha agregada vs SLA 24h)

### 9. Readmissão — faixa-resumo + matriz
Antes da matriz, `.summary-strip` com cards — **apenas campos confirmados**:
- Readm. ≤ 7 dias = `countIf(IE_READMISSAO_7_DIAS='S')`
- Volume elegível (denominador 7d) = `countIf(IE_DENOMINADOR_7_DIAS='S')`
- Taxa = readm7d / denominador (já calculada em `computeKpis.readm7`)
- Dias médios até readm = `avg(QT_DIAS_ATE_READMISSAO)` (campo já usado em `MATRIX_CONFIG.readm`)
- **Não inferir total de readmissões com `IE_READMISSAO_8_30_DIAS`** — só usar se confirmado existir no payload (checar com `r.IE_READMISSAO_8_30_DIAS !== undefined` em runtime); se não, não exibir card
- Cada card: valor + microcopy + badge quando aplicável

Matriz mantém medidas atuais + coluna **derivada** `Risco` (caminho separado, não no `mxComputeAgg`): badge vermelha quando agregação `Readm. 7d > 0` na linha.

### 10. Retorno UTI — destaque crítico
Antes da matriz, `.summary-strip` priorizando:
- Eventos totais
- **Eventos em ≤48h = `countIf(IE_READMISSAO_UTI_48H='S')`** (destaque executivo)
- **Horas médias até retorno = `avg(QT_HORAS_ATE_RETORNO_UTI)`** (destaque executivo)
- **Top 3 setores de saída UTI** (`DS_SETOR_SAIDA_UTI`) por eventos — destaque executivo
- **Aviso textual obrigatório**: `"Contagem de eventos — sem denominador disponível, não calcular taxa"`
- Médico/especialidade **não** no resumo executivo — disponíveis no drilldown (`MATRIX_CONFIG.uti.dimensions`)

Linhas com retorno em 48h ganham badge vermelha forte na coluna `Retorno 48h` da matriz.

### 11. Acurácia — split visual
Antes da matriz, `.summary-strip`:
- Atendimentos analisados = total
- Acurácia oficial = `avg(INDICADOR_PERCENTUAL_ACURACIA)` — mesma leitura da Visão Geral
- Acertos tolerância = `countIf(FL_ACERTO_TOLERANCIA in ('S','1', 1, 1.0000000000))`, apenas apoio operacional
- Atrasos = `countIf(QT_DIF_DIAS_PREVISTO_REAL > 0)` (alta veio depois do previsto)
- Antecipações = `countIf(QT_DIF_DIAS_PREVISTO_REAL < 0)`
- Diferença média (dias) = `avg(QT_DIF_DIAS_PREVISTO_REAL)`

Matriz Acurácia mostra `Acurácia %` como medida principal e mantém `Acertos tol.` como apoio. Coluna `Tipo erro` deriva da acurácia percentual agregada e da diferença média — via `mxComputeDerived`.

Decisão `2026-05-07`: `INDICADOR_PERCENTUAL_ACURACIA` é fonte oficial da acurácia executiva. Não usar `FL_ACERTO_TOLERANCIA` para o número principal.

### 12. Outliers — lista priorizada
Antes da matriz, `.summary-strip`:
- Casos outlier (já filtrados pelo `preFilter:'outliers'`)
- Setor que mais perde dias (top 1 por soma `dias - benchmark`)
- CID que mais perde dias (top 1)
- Total dias excedentes = `sum(QT_DIA_PERMANENCIA - MEDIA_QT_DIA_PERMANENCIA_SETOR_CID)` quando ambos existem

Matriz Outliers: adicionar `Dias excedentes` (sum). Extensão segura `mxComputeAgg`: `{agg:'sum', expr:'a_minus_b', fieldA, fieldB}`.

### 13. Matrizes hierárquicas — pill de nível (OBRIGATÓRIO)
Mudança mínima no `mxBuildRows` e header:
- **Header da 1ª coluna fixo em `"Hierarquia"`** (não mais `dims[0].label`)
- Cada linha exibe pill com `dim.label` correspondente ao nível: `<span class="lv-pill">[Setor]</span> Clínica Médica`
- Pill dinâmica: `dims[level].label` — qualquer ordem de dimensões em `MATRIX_CONFIG`
- CSS `.lv-pill` discreto (cinza, fonte 9px, padding 1×6, radius 3px, uppercase)
- Indentação por nível mantida (`indent = 8 + level * 16`)
- Funciona nas 6 matrizes (TAT/Perm/Readm/UTI/Acur/Outliers) — `MATRIX_CONFIG` tem `dim.label`
- **Não pode quebrar expand/collapse**: `_mxNodeId`, `data-parent`, `aria-expanded`, `mxInitToggles`, `mxExpand`, `mxCollapse` — preservar idênticos. Pill só altera template do `<td class="mx-dim">`, nada mais.

### 14. Tabelas/matrizes — visual
- Linhas mais altas (padding 6×10)
- Hover mais claro
- Alinhamento numérico tabular já existe — manter
- Cabeçalho com border-bottom 2px e contraste maior
- Status pill nas colunas finais (ver 8/9/10)

### 15. Badges — padronização
CSS `.pill` unificado com variantes: `.pill--ok`, `.pill--warn`, `.pill--bad`, `.pill--neutral`. Texto + cor sempre. Manter `.badge` legacy se necessário para retrocompatibilidade visual interna.

Vocabulário fixo:
- TAT: `Dentro SLA` / `Atenção` / `Acima SLA` / `Crítico`
- Permanência: `Normal` / `Elevado` / `Crítico`
- Geral: `OK` / `Atenção` / `Crítico`

### 16. Acentuação pt-BR
Substituições só em strings visuais (não nas chaves JS, não nos `data-tab`):
- "Visao Geral" → "Visão Geral"
- "Permanencia" → "Permanência"
- "Readmissao" → "Readmissão"
- "Acuracia" → "Acurácia"
- "Medico" → "Médico"
- "Critico" → "Crítico"
- "Atencao" → "Atenção"
- "Eficiencia" → "Eficiência"
- "Diagnostico" → "Diagnóstico"
- e todos derivados de header/labels

### 17. Responsividade
Manter breakpoints existentes (1100px, 640px). KPI grid em 3 grupos colapsa: dentro de cada grupo, `repeat(auto-fit, minmax(160px,1fr))`. Summary-strip = `repeat(auto-fit, minmax(150px,1fr))`.

## Funções novas (nomes propostos)

- `buildExecHeadline(kpis)` — string fiel à métrica (ver seção 4)
- `renderExecSummary(kpis)` — render bloco
- `renderReadmStrip(rows)` / `renderUtiStrip(rows)` / `renderAcurStrip(rows)` / `renderOutliersStrip(rows)` — cards summary
- `mxComputeDerived(records, derivedSpec, baseAggs)` — caminho separado para Status/Risco/Tipo erro. Recebe agregações já computadas e devolve string/pill. **Não toca `mxComputeAgg`.**
- `pill(text, kind)` — helper render badge
- Para Outliers, `mxComputeAgg` ganha apenas `agg:'sum'` com expressão simples sobre dois campos via spec dedicada (`{agg:'sum', expr:'a_minus_b', fieldA, fieldB}`) — extensão segura, mesmo contrato numérico

## Funções modificadas

- `renderKpis` — agrupar em 3 sections, microcopy, badge texto
- `renderTatRanking` — adicionar status pill por linha
- `renderHeatmap` — texto da legenda
- `renderMatrix` — header `Hierarquia`, pill `[Nivel]` por linha; suporte a `derivedColumns` (lista de colunas computadas via `mxComputeDerived` após agregações base)
- `refresh` — chamar novos `render…Strip` por aba; mover DIAG para `<details>`
- `initDashboard` — assinatura preservada

## O que NÃO calcular (campo ausente)

- Taxa Retorno UTI 48h — sem denominador no payload, manter contagem só
- Tipo erro acurácia exato (CIDs/causa raiz) — só split numérico previsto/real
- Total readmissões 8–30 dias — só se `IE_READMISSAO_8_30_DIAS` estiver presente no payload em runtime

## Arquivos críticos referenciados

- [dashboard_template.html](../../dashboard_template.html) — fonte
- [docs/References/notebook/NOTEBOK.md](../References/notebook/NOTEBOK.md) — confirmar nomes/campos/schema
- [docs/specs/SQL_INDICADORES.md](../specs/SQL_INDICADORES.md) — alias legado, nao usar como fonte nova
- [docs/specs/prompt2_frontend.md](../specs/prompt2_frontend.md) — spec UI

## Verificação

1. Abrir `dashboard_template_v2.html` no Chrome (sem payload) → ver banner "Aguardando dados", shell renderiza sem erro JS (DevTools console limpo)
2. Injetar payload manual de teste no `D` (ou colar bloco de exemplo da medida) → todas as 7 abas renderizam
3. Cada matriz: clicar `+` em nó raiz, verificar pill `[Setor]` no nível 0, `[CID]` no 1, `[Médico]` no 2, etc
4. Filtros (data/estab/setor/médico) → reaplicam todos os strips
5. Diff visual com slides PPTX (Visão Geral, Permanência expandida, Readmissão, UTI, Acurácia, TAT, Outliers)
6. Power BI Desktop: trocar caminho do template no measure `[HTML Dashboard]` para `dashboard_template_v2.html`, atualizar, validar abas
7. Conferir cabeçalho 1ª coluna de toda matriz = "Hierarquia"
8. DIAG só aparece ao expandir `<details>`

## Resumo final pós-implementação (a entregar ao usuário)

Pós-implementação, entregar 4 listas:
1. **Mudanças visuais** (CSS, layout, pills, acentos)
2. **Cálculos novos** (strips, status derivado, dias excedentes)
3. **Campos do payload usados** (lista por aba)
4. **Limitações por ausência de campo** (taxa Retorno UTI, IE_READMISSAO_8_30_DIAS condicional, etc)

## Lista final do que será alterado e por quê

**Visual puro (sem cálculo novo):**
- Resumo executivo (compõe KPIs já calculados)
- Reagrupamento dos 6 KPIs em 3 secções
- Microcopy "menor/maior é melhor"
- DIAG colapsável
- Pill de nível nas matrizes
- Header "Hierarquia"
- Acentuação pt-BR
- Tokens CSS, espaçamento, hover, contraste
- Padronização de badges com texto

**Envolve cálculo novo:**
- Headline dinâmica (deriva dos status existentes)
- Strip Readmissão (numerador/denominador 7d, taxa, média de dias)
- Strip Retorno UTI (eventos 48h, horas médias, top setores de saída)
- Strip Acurácia (acurácia oficial via `INDICADOR_PERCENTUAL_ACURACIA`; acertos tolerância só como apoio; atrasos/antecipações via `QT_DIF_DIAS_PREVISTO_REAL`)
- Strip Outliers (dias excedentes = `dias - benchmark`)
- Coluna Status nas matrizes Permanência / TAT (via `mxComputeDerived`)
- Coluna Tipo erro na matriz Acurácia (via `mxComputeDerived`)
- Coluna Risco na matriz Readmissão (via `mxComputeDerived`)
- Medida `Dias excedentes` na matriz Outliers (extensão `agg:'sum'` + `expr:'a_minus_b'`)

**Preparado mas dependente de campo ausente:**
- Taxa Retorno UTI 48h — sem denominador, fica como contagem
- Total readmissões 8–30 dias — depende de `IE_READMISSAO_8_30_DIAS` presente no payload
