# Plano - SPEC-004 (Parametrizar fontes locais)

## Objetivo

Reduzir dependencia caminhos absolutos locais nas fontes M do PBIP.

## Checklist

- [x] Extrair issue de Documentacao da auditoria `_review/index.html`.
- [x] Criar spec operacional em `docs/specs/spec-004-parametrizar-fontes-locais.md`.
- [x] Inventariar caminhos absolutos em `definition/tables`.
- [x] Definir parametro(s) ou fonte centralizada por origem.
- [x] Ajustar dimensoes e `_HTML_Base`.
- [ ] Documentar configuracao necessaria para refresh.
- [ ] Validar refresh no Power BI Desktop/Fabric.

## Evidencias iniciais

- Issue: `Fontes dependem de caminhos locais e pastas de usuario`.
- Severidade: Media.
- Caminhos citados: `D:\Myrepository\...`, `C:\Users\luanp\Downloads\...`, HTML em OneDrive local.

## Parametros ativos

| Parametro | Arquivo TMDL | Valor padrao | Uso |
|---|---|---|---|
| `ServidorDW` | `tables/ServidorDW.tmdl` | `192.168.6.2:5432` | Host:porta PostgreSQL |
| `SchemaDW` | `tables/SchemaDW.tmdl` | `public` | Schema no banco `prohmdw` |
| `CaminhoArqHTMLBase` | `tables/CaminhoArqHTMLBase.tmdl` | caminho local do clone | Template HTML do dashboard |

### Dimensoes conectadas ao DW

| Tabela TMDL | Tabela no DW (`prohmdw`) |
|---|---|
| `dim_cid` | `dim_cid_doenca` |
| `dim_estabelecimento` | `dim_estabelecimento` |
| `dim_pessoa` | `dim_pessoa` |
| `dim_setor_atendimento` | `dim_setor_atendimento` |

### Nota dim_cid

DW entrega `CID___Codigo / CID___Descricao / CID___Codigo_Descricao`. sourceColumn atualizado no TMDL. Colunas DAX (`CD_CID`, `DS_CID`, `DS_CID_ORIGINAL`) nao mudaram.

### Instrucoes para novo usuario/maquina

1. Abrir PBIP no Power BI Desktop.
2. Home → Transform data → Edit parameters.
3. Ajustar `ServidorDW` se IP/porta do DW diferir. `SchemaDW` normalmente permanece `public`.
4. Ajustar `CaminhoArqHTMLBase` para caminho local de `dashboard_template_v2.html`.
5. Executar refresh. Credenciais PostgreSQL pedidas na primeira conexao.

### Parametros removidos (obsoletos)

`CaminhoArqDimCid`, `CaminhoArqDimEstabelecimento`, `CaminhoArqDimPessoa`, `CaminhoArqDimSetor` — substituidos por conexao direta ao DW.

## Status

- Spec criada em `2026-05-07`.
- Implementacao concluida em `2026-05-07`.
- Pendente: validacao funcional no Power BI Desktop.

## Proximo passo

Abrir PBIP no Power BI Desktop, confirmar parametros em Edit Parameters, executar refresh, validar dashboard.