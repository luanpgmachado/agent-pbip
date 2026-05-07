# Documentacao Tecnica - Dashboard HTML (PBIP)

## 1. Objetivo

Descreve arquitetura tecnica do dashboard `HTML Content` e manutencao para evoluir metricas, layout, tema e filtros sem quebrar PBIP.

Escopo:
- `dashboard_template.html`
- `_HTML_Base` (Power Query/M)
- `_Medidas` (DAX):
- `JSON Dashboard Compacto`
- `HTML Dashboard`

## 2. Arquitetura Atual

Fluxo render:
1. `dashboard_template.html` contem CSS, HTML, JS da tela.
2. `_HTML_Base` le arquivo, divide em 3 partes.
3. `JSON Dashboard Compacto` serializa dados em JSON.
4. `HTML Dashboard` recompoe HTML base e injeta:
`<script>initDashboard(payloadJson)</script>`
5. Visual `HTML Content` renderiza; JS aplica filtros internos.

Arquivos referencia:
- `C:\Users\luanp\OneDrive\Rep-2026\projjetta\Clientes\STA CASA\agent-pbip\dashboard_template.html`
- `C:\Users\luanp\OneDrive\Rep-2026\projjetta\Clientes\STA CASA\agent-pbip\Desospitalização_Projeto_2026_03_25.SemanticModel\definition\tables\_HTML_Base.tmdl`
- `C:\Users\luanp\OneDrive\Rep-2026\projjetta\Clientes\STA CASA\agent-pbip\Desospitalização_Projeto_2026_03_25.SemanticModel\definition\tables\_Medidas.tmdl`
- `C:\Users\luanp\OneDrive\Rep-2026\projjetta\Clientes\STA CASA\agent-pbip\thema.json`

## 3. Contrato JSON Atual

`JSON Dashboard Compacto` retorna:

```json
{
  "meta": {...},
  "tat": [...],
  "perm": [...],
  "acur": [...],
  "readm": [...],
  "uti": [...]
}
```

Mapeamento frontend:
- `tat`: cards Soma/Media TAT e `% SLA`.
- `perm`: cards permanencia e tabela detalhada.
- `acur`: cards acuracia e erro previsao.
- `readm`: cards readmissao 7d e 30d.
- `uti`: card retorno UTI 48h.
- `meta`: truncamento e total linhas por fato.

## 4. Sessao de Manutencao DASH

### 4.1 Como criar uma nova medida e vincular no DASHBOARD?

1. Crie measure DAX base em `_Medidas` com nome funcional negocio.
2. Se exibida no HTML, adicione campo em `JSON Dashboard Compacto`.
3. Em `dashboard_template.html`, inclua consumo em `refresh()` e bloco visual alvo.
4. Se necessario, crie card/linha HTML para exibir valor.
5. Recarregue no Power BI (`Fechar e aplicar`) e valide com filtros.

Exemplo inclusao DAX JSON:

```DAX
VAR _novoIndicador = SUBSTITUTE(FORMAT([Minha Nova Medida], "0.00"), ",", ".")
...
Q & "novoIndicador" & Q & ":" & _novoIndicador
```

Exemplo consumo JS:

```javascript
var novo = n(row.novoIndicador);
```

### 4.2 Como alterar uma medida existente?

1. Localize measure em `_Medidas.tmdl`.
2. Altere somente regra calculo; preserve nome se frontend depende.
3. Se valor esta no payload JSON, revise conversao numerica:
- sempre `SUBSTITUTE(FORMAT(...), ",", ".")`.
4. Se mudou chave JSON, ajuste JS (`refresh`, `renderCards`, `renderTable`).
5. Valide no Desktop comparando antes/depois com mesmo filtro.

Critico: alterar nome measure sem atualizar JSON e JS quebra card silenciosamente.

### 4.3 Como mudar os objetos visual?

1. Edite `dashboard_template.html`.
2. Estrutura:
- HTML: blocos e containers.
- CSS: estilo e responsividade.
- JS: logica render.
3. Adicionar/remover card:
- ajuste array `cards` em `refresh()`.
- ajuste HTML/CSS se necessario.
4. Alterar tabela:
- ajuste colunas em `<thead>`.
- ajuste linhas em `renderTable(rows)`.
5. Mantenha IDs estaveis com referencia em JS.

Critico: mudar ID sem atualizar `document.getElementById(...)` quebra render.

### 4.4 Como mudar cores e temas?

1. Revise paleta em `thema.json`.
2. Em `dashboard_template.html`, ajuste variaveis CSS em `:root`.
3. Mantenha coerencia:
- `--brand-green`, `--brand-blue`, `--bg`, `--surface`, `--text`, `--border`.
4. Ajuste semaforos: `--ok`, `--warn`, `--bad`.
5. Teste contraste (cards, tabela, badges, hover).

Recomendacao: atualize `:root` primeiro; depois ajuste regras pontuais. Evite hardcode cor fora variaveis.

### 4.5 Como criar logica de filtros?

Filtro atual e interno ao HTML (sem slicer):
- coleta: `getFilters()`.
- aplicacao por linha: `rowPass(row, f)`.
- inicializacao combos: `initFilters()`.
- reprocessamento: `refresh()`.

Novo filtro (ex.: CID):
1. Inclua chave no JSON DAX (`cid` ja existe em `perm`).
2. Adicione `<select id="f-cid">` no HTML.
3. Em `initFilters()`, monte opcoes (`cidSet`), aplique em `fillSelect`.
4. Em `getFilters()`, leia `f-cid`.
5. Em `rowPass()`, inclua:
`if (f.cid !== '__ALL__' && row.cid !== f.cid) return false;`
6. Inclua `f-cid` em listeners `change`.
7. Teste filtro isolado e combinado com datas/estabelecimento/setor/medico.

Critico: array JSON sem chave do filtro = bloco nao responde ao filtro.

### 4.6 Como congelar o HTML em P1/P2/P3 para release?

Objetivo: remover dependencia de `File.Contents("C:\\...\\dashboard_template.html")` em ambiente cliente.

Snippet pronto: `docs/specs/_HTML_Base_release_snippet.m`

1. Abra `_HTML_Base` no Editor Avancado.
2. Substitua bloco `source = let ... in ...` por `docs/specs/_HTML_Base_release_snippet.m`.
3. Confirme query retorna `AsTable` com colunas `part` e `html`.
4. Clique `Concluir` depois `Fechar e Aplicar`.
5. Salve `.pbip`.

Obs:
- Snippet usa `#(lf)` para preservar quebra linha no HTML.
- HTML dividido em 3 blocos (`P1`, `P2`, `P3`) para manutencao string longa.
- Sempre que `dashboard_template.html` mudar, regenere snippet antes publicar.

## 5. Checklist de Publicacao

1. `dashboard_template.html` abre sem erro script.
2. `_HTML_Base` retorna tabela 3 linhas (`part=1,2,3`).
3. `HTML Dashboard` injeta `initDashboard(...)` com JSON valido.
4. Todos cards carregam com filtro default.
5. Tabela responde a filtros combinados.
6. Sem erros no `Fechar e aplicar`.

## 6. Troubleshooting Rapido

Visual vazio apos mudanca:
- Verificar `_HTML_Base` retorna `AsTable` nao texto simples.
- Verificar JSON fecha corretamente (`{}`, `[]`, virgulas).
- Verificar nomes chave DAX batem com JS.

Filtro nao afeta card:
- Verificar array do card contem chaves filtro (`d`, `e`, `s`, `m`).
- Verificar `rowPass()` contem condicao filtro novo.

Valor quebrado (NaN):
- Garantir numero JSON com ponto decimal.
- No JS, usar `n(...)` antes somar/media.