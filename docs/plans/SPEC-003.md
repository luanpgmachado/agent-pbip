# Plano - SPEC-003 (Chaves explicitas nas dimensoes)

## Objetivo

Marcar chaves formais nas dimensoes principais do modelo PBIP.

## Checklist

- [x] Extrair issue de Documentacao da auditoria `_review/index.html`.
- [x] Criar spec operacional em `docs/specs/spec-003-chaves-explicitas-dimensoes.md`.
- [x] Confirmar chave de cada dimensao via `relationships.tmdl`.
- [x] Aplicar `isKey: true` nas dimensoes pendentes.
- [x] Validar unicidade ou registrar risco.
- [ ] Abrir PBIP no Power BI Desktop/Fabric e validar modelo.

## Evidencias iniciais

- Issue: `Dimensoes sem chave explicita (isKey: true)`.
- Severidade: Media.
- Arquivos citados: `dim_calendario`, `dim_cid`, `dim_estabelecimento`, `dim_pessoa`, `dim_setor_atendimento`.

## Mapeamento chave x relacionamento (2026-05-07)

| Dimensao | Coluna chave | Confirmado em `relationships.tmdl` |
|---|---|---|
| `dim_calendario` | `dt_data` | `Indicador 02/06/13/14/15.DT_*` -> `dim_calendario.dt_data` |
| `dim_cid` | `CD_CID` | `Indicador 02/06.CD_CID` -> `dim_cid.CD_CID` |
| `dim_estabelecimento` | `cd_estabelecimento` | `Indicador 02/06/14/15.CD_ESTABELECIMENTO*` -> `dim_estabelecimento.cd_estabelecimento` |
| `dim_pessoa` | `Pessoa___Codigo` | `Indicador 02/06/13/14/15.CD_MEDICO*` -> `dim_pessoa.Pessoa___Codigo` |
| `dim_setor_atendimento` | `cd_setor_atendimento` | `Indicador 02/06/13/14/15.CD_SETOR*` -> `dim_setor_atendimento.cd_setor_atendimento` |

## Risco de unicidade

`isUnique` aplicado so em `dim_calendario.dt_data` (gerada por `CALENDAR`, unicidade garantida). Demais dimensoes vem de CSV/Excel externo (`dim_cid.xlsx`, `dim_estabelecimento_*.csv`, `dim_pessoa_*.csv`, `dim_setor_atendimento_*.csv`); unicidade nao validada nesta sessao. Risco registrado conforme regra 4 da spec — se Power BI acusar duplicata ao abrir, corrigir na origem antes de marcar `isUnique`.

## Status

- Spec criada `2026-05-07`.
- `isKey: true` aplicado em `dim_cid.CD_CID`, `dim_estabelecimento.cd_estabelecimento`, `dim_pessoa.Pessoa___Codigo`, `dim_setor_atendimento.cd_setor_atendimento` em `2026-05-07`.
- `dim_calendario.dt_data` ja vinha com `isKey: true` desde SPEC-002.
- Pendente: validacao funcional no Power BI Desktop/Fabric.

## Proximo passo

Abrir PBIP no Power BI Desktop/Fabric, atualizar modelo, conferir erros de modelagem e duplicidade nas chaves marcadas.