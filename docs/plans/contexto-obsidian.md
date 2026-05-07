# Contexto Obsidian

Plano transversal para usar Obsidian como camada humana do fluxo `spec -> plan -> implementar -> validar -> arquivar`, sem duplicar fonte operacional do repo.

## Status

- [x] Detectar disponibilidade da skill/CLI Obsidian.
- [x] Registrar bloqueio: `obsidian` CLI nao esta disponivel no PATH desta sessao.
- [x] Criar bootstrap equivalente em `docs/obsidian-bootstrap/`.
- [x] Criar estrutura de pastas sugerida para vault.
- [x] Criar nota hub do projeto.
- [x] Criar templates Obsidian.
- [x] Atualizar `AGENTS.md` com regra de governanca.
- [x] Atualizar `PLAN.md` sem virar diario longo.
- [x] Criar `docs/archive/specs/` e `docs/archive/plans/` como destino proposto para concluidos.
- [ ] Sincronizar `docs/obsidian-bootstrap/` para vault real quando Obsidian CLI estiver disponivel.

## Regra de governanca

Repo e fonte executavel e operacional:
- `AGENTS.md`
- `PLAN.md`
- `docs/specs/`
- `docs/plans/`
- `docs/References/notebook/NOTEBOK.md`
- `docs/GUIA_MEDIDAS_DASHBOARD_V2.md`
- `docs/specs/dashboard_tecnico_manutencao.md`

Obsidian e camada humana:
- hub de navegacao;
- decisoes;
- reunioes;
- resumo de release;
- glossario;
- links para arquivos do repo.

Nao duplicar no Obsidian:
- DAX completo;
- schema completo;
- SQL inteiro;
- planos longos;
- payload JSON completo.

## Ciclo de vida

1. Nova demanda nasce no Obsidian em `00-Inbox/`.
2. Quando vira trabalho real, criar spec operacional em `docs/specs/spec-XXX.md`.
3. Criar plan operacional em `docs/plans/SPEC-XXX.md`.
4. Implementar no repo PBIP/TMDL/JSON/docs.
5. Validar no Power BI Desktop/Fabric.
6. Ao fechar, comprimir spec/plan para decisao, evidencias e resultado.
7. Se nao estiver mais ativo, mover para `docs/archive/specs/` e `docs/archive/plans/`.
8. Manter `PLAN.md` com linha curta e link para arquivo ativo ou arquivado.
9. Registrar resumo humano em Obsidian `04-Releases/` ou decisao em `01-Decisoes/`.

## Bootstrap criado

- Hub: `docs/obsidian-bootstrap/Dashboard Desospitalizacao - Hub.md`
- Templates: `docs/obsidian-bootstrap/Templates/`
- Pastas: `00-Inbox/`, `01-Decisoes/`, `02-Specs/`, `03-Plans/`, `04-Releases/`, `05-Reunioes/`, `06-Glossario/`, `99-Archive/`

## Como sincronizar depois

Quando `obsidian` CLI estiver disponivel:

```powershell
obsidian help
obsidian create path="Dashboard Desospitalizacao - Hub.md" content="..." silent overwrite
```

Alternativa simples: copiar o conteudo de `docs/obsidian-bootstrap/` para vault real e preservar links para o repo.
