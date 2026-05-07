<!--
  TEMPLATE · /pbi-modelo-review · relatorio.md
  Versão markdown do relatório (versionável Git, lê em qualquer editor)

  Como usar:
  1. Substituir placeholders {{VAR}} pelos valores reais
  2. Repetir bloco {{ISSUE_BLOCK}} pra cada issue (manter a estrutura)
  3. Salvar como _review/relatorio.md na raiz do projeto Power BI

  Esse markdown é o "irmão" do index.html — mesmo conteúdo, mesma ordem, sem visual.
  Pra commit em Git, code review, leitura no editor.
-->

# Auditoria · Desospitalização_Projeto_2026_03_25.pbip

> **Score: 89/100 — Precisa Atenção**
> Gerado por Codex + `/pbi-modelo-review` em 07 mai 2026 · 13:42

**Modelo:** 67 tabelas · 32 medidas · 77 relacionamentos · 441 KB TMDL

---

## Veredicto

Base de negócio existe: dimensões compartilhadas, medidas organizadas, calendário próprio. Mas modelo carrega herança pesada de Auto Date/Time e dependências locais. Hoje funciona; amanhã, em outra máquina ou manutenção maior, cobra juros altos.

| Métrica | Valor |
|---|---|
| Issues totais | **8** |
| Críticos | **1** |
| Tempo estimado de correção | **4 dias** |

---

## Severidade

| Nível | Quantidade | Quando resolver |
|---|---|---|
| ▲ **Crítico** | 1 | Resolve primeiro — quebram refresh em produção, comprometem performance ou geram resultado errado |
| ● **Médio** | 4 | Próxima sprint — anti-patterns que pioram conforme modelo cresce |
| ○ **Leve** | 3 | Quando der tempo — boas práticas, padronização, naming |

---

## Distribuição por categoria

| Categoria | Issues |
|---|---|
| Documentação | 4 |
| Performance | 1 |
| Relacionamentos | 1 |
| Modelagem | 1 |
| Naming | 1 |

<!--
  Formato esperado de DISTRIBUTION_TABLE:
  | Categoria | Issues |
  |---|---|
  | Performance | 14 |
  | Relacionamentos | 11 |
  | ...
-->

---

## Issues priorizados

Issues abaixo **ordenados por severidade** (crítico → médio → leve) e **agrupados por categoria** (concentração = prioridade de refator).

### [CRÍTICO] · [MODELAGEM] · Calendário oficial existe, mas 53 LocalDateTable_* ainda dominam o modelo

**Onde:** `powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition/model.tmdl:9; tables/dim_calendario.tmdl:3; tables/Indicador 02.tmdl:81`

**Por que importa:**
Modelo tem `dim_calendario`, mas mantém `__PBI_TimeIntelligenceEnabled = 1`, 53 `LocalDateTable_*`, 1 `DateTableTemplate_*` e 104 referências `defaultHierarchy` apontando para calendários automáticos. Pior dos dois mundos: paga custo do calendário errado mantendo o certo. Resultado: explosão de relacionamentos de data, time-intelligence inconsistente, alto risco de visual cair em hierarquia automática sem ninguém perceber.

**Como corrigir:**
Eleja `dim_calendario` como única dimensão temporal. Marque `dim_calendario[dt_data]` como chave, remova blocos `variation Variation` apontando para `LocalDateTable_*`, religue datas dos fatos exclusivamente na `dim_calendario`, desligue Auto Date/Time no Desktop antes do próximo publish.
```tmdl
table dim_calendario
    dataCategory: Time

    column dt_data
        isKey: true
        summarizeBy: none

// Nas colunas de data dos fatos:
// remover variation Variation + defaultHierarchy LocalDateTable_*
```

---

### [MÉDIO] · [DOCUMENTAÇÃO] · Dimensões sem chave explícita (`isKey: true`)

**Onde:** `tables/dim_calendario.tmdl:1; tables/dim_cid.tmdl:1; tables/dim_estabelecimento.tmdl:1; tables/dim_pessoa.tmdl:1; tables/dim_setor_atendimento.tmdl:1`

**Por que importa:**
5 dimensões sem chave formal no TMDL. Enfraquece semântica, deixa leitura ambígua pra quem herdar e, no caso da `dim_calendario`, explica por que Power BI continuou se apoiando nas tabelas automáticas.

**Como corrigir:**
Marque chave de cada dimensão: `dt_data`, `CD_CID`, `cd_estabelecimento`, `Pessoa___Codigo`, `cd_setor_atendimento`. Faça antes de qualquer limpeza de relacionamentos para motor entender coluna certa em cada dimensão.
```tmdl
column dt_data
    isKey: true

column cd_estabelecimento
    isKey: true
```

---

### [MÉDIO] · [DOCUMENTAÇÃO] · Fontes dependem de caminhos locais e pastas de usuário

**Onde:** `tables/dim_cid.tmdl:32; tables/dim_estabelecimento.tmdl:33; tables/dim_pessoa.tmdl:57; tables/dim_setor_atendimento.tmdl:58; tables/_HTML_Base.tmdl:26`

**Por que importa:**
Refresh depende de `D:\Myrepository\...`, `C:\Users\luanp\Downloads\...` e HTML carregado por caminho absoluto dentro do OneDrive local. Outra máquina, outro login ou outro ambiente de publicação: quebra na largada. Tipo de incidente que vira suporte evitável.

**Como corrigir:**
Parametrize caminho base, mova artefatos compartilhados para origem centralizada, substitua dependências locais por dataset, dataflow ou link compartilhado quando possível. Para HTML base, prefira arquivo em fonte controlada ou parametrização explícita.
```tmdl
expression CaminhoBase = "" meta [
    IsParameterQuery=true,
    Type="Text",
    IsParameterQueryRequired=true
]
```

---

### [MÉDIO] · [PERFORMANCE] · Auto Date/Time segue ligado e infla o modelo sem entregar valor

**Onde:** `powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition/model.tmdl:9`

**Por que importa:**
Dos 67 objetos tabulares, 54 existem só pra sustentar calendário automático (`53 LocalDateTable_*` + `1 DateTableTemplate_*`). Consome espaço mental, aumenta relacionamentos, complica manutenção de data. Muito peso pra pouca utilidade.

**Como corrigir:**
Depois de consolidar tudo na `dim_calendario`, desligue Auto Date/Time nas opções do Power BI Desktop e remova referências automáticas. Meta: uma única trilha temporal clara e barata de manter.
```tmdl
annotation __PBI_TimeIntelligenceEnabled = 0
```

---

### [MÉDIO] · [NAMING] · Convenções de naming misturadas entre modelo semântico e origem técnica

**Onde:** `tables/dim_estabelecimento.tmdl:4; tables/dim_pessoa.tmdl:4; tables/Indicador 02.tmdl:4; tables/_Medidas.tmdl:6`

**Por que importa:**
Modelo mistura `cd_estabelecimento`, `Pessoa___Codigo`, `CD_ESTABELECIMENTO`, `Indicador 02` e medidas de negócio em Title Case. Não quebra refresh, mas cobra caro em busca, onboarding e reuso: cada analista novo precisa adivinhar qual dialeto vale em cada tabela.

**Como corrigir:**
Defina duas camadas: técnica de ingestão e semântica de consumo. Novos objetos já padronize. Existentes: refatore por ondas pequenas, começando pelas dimensões e campos mais usados nos visuais.
```txt
Dimensão: dim_estabelecimento
Chave: cd_estabelecimento
Atributo: nm_estabelecimento
Medida: Média Permanência (dias)
```

---

### [LEVE] · [DOCUMENTAÇÃO] · 32 medidas seguem sem `description:` formal no TMDL

**Onde:** `tables/_Medidas.tmdl:6`

**Por que importa:**
Comentários `///` ajudam quem lê o arquivo, mas não substituem `description:` consumida por catálogo, lineage e handoff. Medidas mais importantes ficam mudas pra quem usa o modelo fora do editor.

**Como corrigir:**
Adicionar `description:` nas 32 medidas, priorizando expostas em cards, KPIs e JSONs do dashboard. Uma frase clara por medida já eleva bastante a legibilidade operacional.
```tmdl
measure 'Total Exames' = COUNTROWS('Indicador 02')
    description: "Total de exames concluídos com data de evento final e TAT válido no contexto filtrado."
```

---

### [LEVE] · [DOCUMENTAÇÃO] · Tabelas de negócio seguem sem descrição de papel e granularidade

**Onde:** `tables/dim_calendario.tmdl:1; tables/dim_cid.tmdl:1; tables/dim_estabelecimento.tmdl:1; tables/dim_pessoa.tmdl:1; tables/dim_setor_atendimento.tmdl:1; tables/Indicador 02.tmdl:1`

**Por que importa:**
Tabelas principais do domínio não explicam origem, papel nem granularidade. Quem chega depois precisa abrir coluna por coluna pra entender se está olhando fato assistencial, dimensão conformada ou artefato utilitário.

**Como corrigir:**
Adicionar `description:` nas tabelas de negócio com 1–2 frases: origem, granularidade e uso esperado. Diferença enorme em handoff e revisão futura.
```tmdl
table 'Indicador 06'
    description: "Fato de permanência por atendimento. Granularidade por registro assistencial com datas de entrada, alta e métricas derivadas de permanência."
```

---

### [LEVE] · [RELACIONAMENTOS] · Dois relacionamentos inativos não aparecem em nenhuma medida via `USERELATIONSHIP()`

**Onde:** `powerbi/pbip/Desospitalização_Projeto_2026_03_25.SemanticModel/definition/relationships.tmdl:94; relationships.tmdl:123`

**Por que importa:**
Relacionamentos `Indicador 02[NR_PRONTUARIO] -> Indicador 06[NR_PRONTUARIO]` e `Indicador 13[DT_EVENTO_PREVISAO] -> dim_calendario[dt_data]` inativos, sem nenhuma medida usando `USERELATIONSHIP()`. Lixo conceitual no modelo: ninguém sabe se é legado esquecido ou requisito inacabado.

**Como corrigir:**
Sem uso planejado: remova. Intenção futura: documente motivo no TMDL e crie medida correspondente com `USERELATIONSHIP()` pra deixar escolha explícita.
```dax
measure 'Alta por Data Prevista' =
    CALCULATE(
        [Total Atendimentos],
        USERELATIONSHIP('Indicador 13'[DT_EVENTO_PREVISAO], dim_calendario[dt_data])
    )
```

---

<!--
  Formato esperado de cada ISSUE_BLOCK:

  ### [SEVERIDADE] · [CATEGORIA] · {Título do issue}

  **Onde:** `path/do/arquivo.tmdl[:linha]`

  **Por que importa:**
  {Texto explicando por que isso é problema, adaptado ao contexto real do projeto.}

  **Como corrigir:**
  {Passo prático.}

  ```{tmdl|dax}
  // Snippet sugerido (opcional)
  ```

  ---

  Repetir o bloco pra cada issue.
-->

---

## Como rodar de novo

Pra re-auditar (depois de correções ou pra acompanhar evolução):

```
Codex  # na pasta raiz do projeto Power BI
> /pbi-modelo-review
```

Skill **sobrescreve** este relatório a cada execução. Pra acompanhar evolução, commite cada versão no Git e use `git diff _review/relatorio.md` pra ver o que mudou entre auditorias.

---

## Sobre essa skill

Auditoria gerada por **`/pbi-modelo-review`** — skill open-source da **Xperiun**, parte do toolkit Codex para Power BI.

- Operação 100% local · zero rede · zero XMLA · LGPD-compatível
- Lê apenas arquivos `.tmdl` (texto puro do PBIP)
- Não modifica nada em `SemanticModel/` ou `Report/` — somente leitura

Saiba mais: **[pages.xperiun.com](https://pages.xperiun.com)**

---

*XPERIUN · O Sistema Operacional dos Incomparáveis*