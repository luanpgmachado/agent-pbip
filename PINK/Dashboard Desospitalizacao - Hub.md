---
title: Dashboard Desospitalizacao - Hub
aliases:
  - Hub Dashboard Desospitalizacao
tags:
  - projeto/pbip
  - dashboard/desospitalizacao
status: ativo
---

# Dashboard Desospitalizacao - Hub

## Regra de fonte

> [!warning] Governanca
> Repo = fonte executavel e operacional. Obsidian = mapa humano, decisoes, reunioes, resumo e links.

Nao duplicar no Obsidian:
- DAX completo.
- Schema completo.
- SQL inteiro.
- Planos longos.
- Payload JSON completo.

## Fontes operacionais do repo

- Governanca do agente: [AGENTS.md](../AGENTS.md)
- Indice operacional: [PLAN.md](../PLAN.md)
- Specs ativas: [docs/specs/](../docs/specs/)
- Plans ativos: [docs/plans/](../docs/plans/)
- Schema/linhagem: [docs/References/notebook/NOTEBOK.md](../docs/References/notebook/NOTEBOK.md)
- Cards/medidas: [docs/GUIA_MEDIDAS_DASHBOARD_V2.md](../docs/GUIA_MEDIDAS_DASHBOARD_V2.md)
- Contrato HTML/payload: [docs/specs/dashboard_tecnico_manutencao.md](../docs/specs/dashboard_tecnico_manutencao.md)

## Estrutura do vault

- [[00-Inbox/README|00-Inbox]]: demandas brutas, ideias e notas de reuniao ainda sem execucao.
- [[01-Decisoes/README|01-Decisoes]]: ADRs curtas e decisoes humanas.
- [[02-Specs/README|02-Specs]]: mapas/resumos de specs, sempre linkando arquivo em `docs/specs/`.
- [[03-Plans/README|03-Plans]]: mapas/resumos de plans, sempre linkando arquivo em `docs/plans/`.
- [[04-Releases/README|04-Releases]]: resumo humano de entregas fechadas.
- [[05-Reunioes/README|05-Reunioes]]: atas e encaminhamentos.
- [[06-Glossario/README|06-Glossario]]: termos de negocio e semantica.
- [[99-Archive/README|99-Archive]]: notas antigas ou contexto substituido.

## Ciclo de vida

1. Nova demanda nasce em `00-Inbox/` como nota curta.
2. Quando vira trabalho real, criar `docs/specs/spec-XXX.md` no repo.
3. Criar `docs/plans/SPEC-XXX.md` no repo.
4. Implementar no PBIP/TMDL/JSON/docs operacionais.
5. Validar no Power BI Desktop/Fabric.
6. Ao fechar, comprimir spec/plan para manter so decisao, evidencias e resultado.
7. Mover concluidos para `docs/archive/specs/` e `docs/archive/plans/` se nao forem mais ativos.
8. Manter `PLAN.md` com linha curta apontando arquivo ativo ou arquivado.
9. Registrar resumo humano em `04-Releases/` ou decisao em `01-Decisoes/`.

## Links rapidos

- [[Templates/Template - Spec|Template - Spec]]
- [[Templates/Template - Plan|Template - Plan]]
- [[Templates/Template - Decisao|Template - Decisao]]
- [[Templates/Template - Release|Template - Release]]
